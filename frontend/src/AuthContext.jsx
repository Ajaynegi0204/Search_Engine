import { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  // Configure axios to always send cookies
  const api = axios.create({
    baseURL: 'https://search-engine-2-kcv6.onrender.com',
    withCredentials: true
  });

  const login = async (credentials) => {
    try {
      const { data } = await api.post('/api/user/login', credentials);
      setUser(data.user);
      navigate('/dashboard');
      toast.success('Logged in successfully!');
    } catch (error) {
      toast.error(error.response?.data?.message || 'Login failed');
    }
  };

  const logout = async () => {
    try {
      await api.post('/api/user/logout');
      setUser(null);
      navigate('/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // Check auth status on initial load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const { data } = await api.get('/api/user/verify-token');
        if (data?.user) {
          setUser(data.user);
          if (window.location.pathname === '/') {
            navigate('/dashboard');
          }
        }
      } catch (error) {
        // Not logged in - do nothing
      }
    };
    checkAuth();
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout, api }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);