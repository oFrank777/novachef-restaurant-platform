import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('access_token'));
  const [loading, setLoading] = useState(true);

  const clearSession = useCallback(() => {
    localStorage.removeItem('access_token');
    setToken(null);
    setUser(null);
  }, []);

  const fetchUser = useCallback(async () => {
    try {
      const res = await api.get('/auth/me');
      setUser(res.data);
    } catch {
      clearSession();
    } finally {
      setLoading(false);
    }
  }, [clearSession]);

  useEffect(() => {
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [token, fetchUser]);

  useEffect(() => {
    const onLogout = () => clearSession();
    window.addEventListener('auth:logout', onLogout);
    return () => window.removeEventListener('auth:logout', onLogout);
  }, [clearSession]);

  const login = async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username.trim());
    formData.append('password', password);

    const res = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      skipGlobalError: true,
    });

    const accessToken = res.data.access_token;
    localStorage.setItem('access_token', accessToken);
    setToken(accessToken);

    try {
      const userRes = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${accessToken}` },
        skipGlobalError: true,
      });
      setUser(userRes.data);
      return userRes.data;
    } catch {
      clearSession();
      throw new Error('No se pudo iniciar sesión. Intenta de nuevo.');
    }
  };

  const register = async (data) => {
    const payload = {
      username: data.username,
      first_name: data.first_name,
      last_name: data.last_name,
      email: data.email,
      password: data.password,
      role: 'cliente',
    };
    const res = await api.post('/auth/register', payload, { skipGlobalError: true });
    return res.data;
  };

  const logout = () => {
    clearSession();
  };

  const isAuthenticated = !!user;
  const isAdmin = user?.role === 'admin';
  const isCajero = user?.role === 'cajero';
  const isAdminOrCajero = isAdmin || isCajero;

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAuthenticated,
        isAdmin,
        isCajero,
        isAdminOrCajero,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
