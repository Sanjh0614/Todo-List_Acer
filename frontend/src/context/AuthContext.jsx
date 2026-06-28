/**
 * AuthContext.jsx — Global auth state
 * - Reads token from localStorage on mount → calls /auth/me to rehydrate
 * - Exposes { user, loading, login, logout } via useAuth() hook
 * - Eliminates prop-drilling across pages
 */
import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getToken, setToken, clearToken, getMe, demoLogin, logout as apiLogout } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);
  const [loading, setLoading] = useState(true);

  // Rehydrate on mount if a token exists in localStorage or URL
  useEffect(() => {
    const init = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const urlToken = urlParams.get('token');
      if (urlToken) {
        setToken(urlToken);
        window.history.replaceState({}, document.title, window.location.pathname);
      }

      if (getToken()) {
        try {
          const me = await getMe();
          setUser(me);
        } catch {
          clearToken(); // token expired / invalid
        }
      }
      setLoading(false);
    };
    init();
  }, []);

  const login = useCallback(async () => {
    const res = await demoLogin();
    setToken(res.access_token);
    const me = await getMe();
    setUser(me);
    return me;
  }, []);

  const logout = useCallback(() => {
    apiLogout();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
