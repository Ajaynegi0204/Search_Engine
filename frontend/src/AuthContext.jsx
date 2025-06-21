import { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Create a shared axios instance
  const api = axios.create({
    baseURL: 'https://search-engine-2-kcv6.onrender.com',
    headers: {
      'Content-Type': 'application/json'
    }
  });

  // Interceptor to attach token dynamically
  api.interceptors.request.use((config) => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      config.headers.Authorization = `Bearer ${storedToken}`;
    }
    return config;
  });

  const login = async (credentials) => {
    setLoading(true);
    try {
      const { data } = await api.post('/api/user/login', credentials);
      setToken(data.token);
      setUser(data.user);
      localStorage.setItem('token', data.token);
      navigate('/dashboard');
      toast.success('Logged in successfully!');
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Login failed';
      toast.error(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await api.post('/api/user/logout');
    } catch (error) {
      console.error('Logout API error:', error);
    } finally {
      // Clear state and localStorage
      setToken(null);
      setUser(null);
      localStorage.removeItem('token');
      navigate('/');
      toast.success('Logged out successfully!');
      setLoading(false);
    }
  };

  useEffect(() => {
    const verifyAuth = async () => {
      const storedToken = localStorage.getItem('token');
      if (!storedToken) return;

      try {
        const { data } = await api.get('/api/user/verify-token');
        setUser(data.user);
        if (window.location.pathname === '/') {
          navigate('/dashboard');
        }
      } catch (error) {
        if (error.response?.status === 401) {
          setToken(null);
          setUser(null);
          localStorage.removeItem('token');
        } else {
          console.error('Token verification failed:', error);
        }
      }
    };

    verifyAuth();
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, api }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
