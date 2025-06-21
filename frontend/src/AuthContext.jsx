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

  // Configure axios instance
  const api = axios.create({
    baseURL: 'https://search-engine-2-kcv6.onrender.com',
    headers: {
      'Content-Type': 'application/json'
    }
  });

  // Add/remove auth token from requests
  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      localStorage.setItem('token', token);
    } else {
      delete api.defaults.headers.common['Authorization'];
      localStorage.removeItem('token');
    }
  }, [token]);

  const login = async (credentials) => {
    setLoading(true);
    try {
      const { data } = await api.post('/api/user/login', credentials);
      setToken(data.token);
      setUser(data.user);
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
      // Always perform cleanup
      setToken(null);
      setUser(null);
      localStorage.removeItem('token');
      delete api.defaults.headers.common['Authorization'];
      navigate('/');
      toast.success('Logged out successfully!');
      setLoading(false);
    }
  };

  // Verify auth status on mount
  useEffect(() => {
    const verifyAuth = async () => {
      if (!token) return;
      
      try {
        const { data } = await api.get('/api/user/verify-token');
        setUser(data.user);
        if (window.location.pathname === '/') {
          navigate('/dashboard');
        }
      } catch (error) {
        // Token verification failed - clear everything
        setToken(null);
        localStorage.removeItem('token');
        delete api.defaults.headers.common['Authorization'];
      }
    };

    verifyAuth();
  }, []);

  return (
    <AuthContext.Provider value={{ 
      user, 
      token, 
      loading,
      login, 
      logout, 
      api 
    }}>
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