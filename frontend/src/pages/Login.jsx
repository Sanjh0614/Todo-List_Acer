import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

function Login() {
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const handleDemoLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      await login();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div id="login-page" className="page">
      <div className="login-container">
        <div className="login-logo">
          <span style={{ fontSize: '3rem' }}>🎯</span>
        </div>
        <h1>AI Productivity Assistant</h1>
        <p className="muted">Organize, prioritize, and focus — powered by AI & Supabase.</p>

        {error && (
          <div className="error-banner">
            ⚠️ {error}
          </div>
        )}

        <button
          id="demo-login-btn"
          onClick={handleDemoLogin}
          className="btn btn-primary btn-large"
          disabled={loading}
        >
          {loading ? (
            <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="spinner-sm" /> Connecting…
            </span>
          ) : (
            '🚀 Try Demo — Connect to Supabase'
          )}
        </button>

        <p className="muted" style={{ fontSize: '0.75rem', marginTop: '1rem' }}>
          Demo mode creates a persistent user in your Supabase database.
        </p>
      </div>
    </div>
  );
}

export default Login;
