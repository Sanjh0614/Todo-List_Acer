"""
tests/test_db_connection.py
============================
Verifies that the backend is correctly connected to the Supabase PostgreSQL database.

Run with:
    cd backend
    python -m pytest tests/test_db_connection.py -v

What is tested:
1. DB URL points to PostgreSQL (not SQLite)
2. A raw psycopg2 connection can be established to Supabase
3. SQLAlchemy engine can connect and reflect the DB
4. All ORM tables can be created (create_all is idempotent)
5. CRUD: insert + query + delete a User row
6. FastAPI /health and / endpoints respond correctly
"""

import pytest
import psycopg2
from sqlalchemy import text, inspect as sa_inspect
from app.config import settings
from app.database import engine, Base, get_db
from app.models import user, commitment, task, focus_session, reminder  # noqa: registers models
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from starlette.testclient import TestClient
from app.main import app


# ─── 1. Configuration ────────────────────────────────────────────────────────

class TestDatabaseConfig:
    """Ensure environment is pointing at PostgreSQL, not SQLite."""

    def test_database_url_is_postgresql(self):
        """DATABASE_URL must start with postgresql:// (not sqlite)."""
        assert settings.DATABASE_URL.startswith("postgresql"), (
            f"Expected PostgreSQL URL, got: {settings.DATABASE_URL[:30]}..."
        )

    def test_database_url_contains_supabase_host(self):
        """DATABASE_URL should reference the Supabase host."""
        assert "supabase.co" in settings.DATABASE_URL, (
            "DATABASE_URL does not appear to point to Supabase"
        )

    def test_supabase_url_is_set(self):
        """SUPABASE_URL should be populated (not the placeholder)."""
        assert settings.SUPABASE_URL and "YOURPROJECT" not in settings.SUPABASE_URL, (
            "SUPABASE_URL is still the placeholder value"
        )


# ─── 2. Raw psycopg2 Connection ───────────────────────────────────────────────

class TestRawPsycopg2Connection:
    """Direct psycopg2 smoke tests — independent of SQLAlchemy."""

    def test_can_connect(self):
        """Establish a bare psycopg2 connection to Supabase (retries on transient SSL reset)."""
        last_err = None
        for attempt in range(3):
            try:
                conn = psycopg2.connect(settings.DATABASE_URL)
                assert conn is not None
                conn.close()
                return  # success
            except psycopg2.OperationalError as e:
                last_err = e
                import time; time.sleep(2)
        raise AssertionError(f"Could not connect after 3 attempts: {last_err}")

    def test_can_execute_simple_query(self):
        """Run SELECT 1 over a raw cursor."""
        conn = psycopg2.connect(settings.DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        cur.close()
        conn.close()
        assert result == (1,), f"Expected (1,), got {result}"

    def test_server_version_is_postgres(self):
        """Confirm the remote server is PostgreSQL."""
        conn = psycopg2.connect(settings.DATABASE_URL)
        version = conn.server_version
        conn.close()
        assert version > 0, "Could not retrieve server_version"
        print(f"\n  ✅ PostgreSQL server version: {version}")


# ─── 3. SQLAlchemy Engine ────────────────────────────────────────────────────

class TestSQLAlchemyEngine:
    """Verify SQLAlchemy can communicate with the database."""

    def test_engine_connect(self):
        """engine.connect() must succeed without exceptions."""
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1

    def test_engine_dialect_is_postgresql(self):
        """SQLAlchemy engine dialect must be 'postgresql'."""
        assert engine.dialect.name == "postgresql", (
            f"Expected 'postgresql', got '{engine.dialect.name}'"
        )

    def test_pool_pre_ping_enabled(self):
        """Pool pre-ping should be active for PostgreSQL connections."""
        # pool_pre_ping=True is set in database.py for non-SQLite DBs
        assert engine.pool._pre_ping is True  # type: ignore[attr-defined]


# ─── 4. Schema / Table Creation ──────────────────────────────────────────────

class TestSchemaCreation:
    """Ensure create_all runs cleanly and the expected tables exist."""

    EXPECTED_TABLES = {"users", "commitments", "tasks", "focus_sessions", "reminders", "feedback"}

    def test_create_all_is_idempotent(self):
        """Base.metadata.create_all should not raise even if tables exist."""
        Base.metadata.create_all(bind=engine)  # should be a no-op if tables exist

    def test_expected_tables_exist(self):
        """All ORM-defined tables must be present in the Supabase DB."""
        inspector = sa_inspect(engine)
        actual_tables = set(inspector.get_table_names())
        missing = self.EXPECTED_TABLES - actual_tables
        assert not missing, (
            f"Missing tables in Supabase: {missing}\nFound: {actual_tables}"
        )


# ─── 5. CRUD via SQLAlchemy Session ──────────────────────────────────────────

class TestCRUDOperations:
    """Write, read, and delete a record through the ORM session."""

    TEST_GOOGLE_ID = "test_google_id_pytest_12345"
    TEST_EMAIL = "pytest_integration@test.invalid"

    def setup_method(self):
        """Clean up any leftover test row before each test."""
        from app.models.user import User
        with engine.begin() as conn:
            conn.execute(
                text("DELETE FROM users WHERE google_id = :gid"),
                {"gid": self.TEST_GOOGLE_ID},
            )

    def teardown_method(self):
        """Always clean up after each test."""
        self.setup_method()

    def test_insert_and_query_user(self):
        """Create a User row and read it back via ORM."""
        from app.models.user import User

        db_gen = get_db()
        db = next(db_gen)
        try:
            new_user = User(
                google_id=self.TEST_GOOGLE_ID,
                email=self.TEST_EMAIL,
                name="PyTest Integration User",
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            assert new_user.id is not None, "User was not assigned a PK"
            fetched = db.query(User).filter_by(google_id=self.TEST_GOOGLE_ID).first()
            assert fetched is not None, "User row not found after insert"
            assert fetched.email == self.TEST_EMAIL
        finally:
            db.close()

    def test_delete_user(self):
        """Insert then delete a User row and confirm it is gone."""
        from app.models.user import User

        db_gen = get_db()
        db = next(db_gen)
        try:
            db.add(User(google_id=self.TEST_GOOGLE_ID, email=self.TEST_EMAIL, name="Delete Me"))
            db.commit()

            user_row = db.query(User).filter_by(google_id=self.TEST_GOOGLE_ID).first()
            assert user_row is not None
            db.delete(user_row)
            db.commit()

            gone = db.query(User).filter_by(google_id=self.TEST_GOOGLE_ID).first()
            assert gone is None, "User row still exists after delete"
        finally:
            db.close()


# ─── 6. FastAPI Health Endpoints ─────────────────────────────────────────────

class TestFastAPIEndpoints:
    """Smoke-test the API layer; the lifespan creates tables on startup."""

    @pytest.fixture(scope="class")
    def client(self):
        """Spin up the full FastAPI app (with lifespan) for endpoint tests."""
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c

    def test_root_endpoint(self, client):
        """GET / returns 200 with message field."""
        resp = client.get("/")
        assert resp.status_code == 200
        body = resp.json()
        assert "message" in body

    def test_health_endpoint(self, client):
        """GET /health returns status: ok."""
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_docs_accessible(self, client):
        """OpenAPI docs page must load (200)."""
        resp = client.get("/docs")
        assert resp.status_code == 200
