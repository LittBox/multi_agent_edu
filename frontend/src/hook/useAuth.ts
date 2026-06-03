// src/hooks/useAuth.ts
import { useEffect, useState } from 'react';
import { fetchCurrentUser, type User, login as apiLogin, logout as apiLogout } from '../api/auth';

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUser = async () => {
      try {
        const userData = await fetchCurrentUser();
        setUser(userData);
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    loadUser();
  }, []);

  const login = async (username: string, pwd: string) => {
    const { token, user } = await apiLogin({ username, pwd });
    localStorage.setItem('accessToken', token);
    setUser(user);
  };

  const logout = async () => {
    await apiLogout();
    localStorage.removeItem('accessToken');
    setUser(null);
  };

  return { user, loading, login, logout };
};