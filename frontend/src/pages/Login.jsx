import { useAuth } from '../context/AuthContext';

function Login() {
  return (
    <div id="login-page" className="page">
      <div className="login-container">
        <div className="login-logo">
          <span style={{ fontSize: '3rem' }}>🎯</span>
        </div>
        <h1>AI Productivity Assistant</h1>
        <p className="muted">Organize, prioritize, and focus — powered by AI.</p>

        <button
          onClick={() => window.location.href = 'http://localhost:8000/auth/google/login'}
          className="btn btn-primary btn-large"
        >
          Login with Google
        </button>
      </div>
    </div>
  );
}

export default Login;
