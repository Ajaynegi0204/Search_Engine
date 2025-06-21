import { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const api = axios.create({
    baseURL: 'https://search-engine-2-kcv6.onrender.com',
    withCredentials: true,
  });

  
  api.interceptors.response.use(
    response => response,
    error => {
      if (error.response?.status === 401) {
        setUser(null);
        if (window.location.pathname.startsWith('/dashboard')) {
          navigate('/');
        }
      }
      return Promise.reject(error);
    }
  );

  const verifyToken = async () => {
    try {
      const { data } = await api.get('/api/user/verify-token');
      return data?.success ? data.user : null;
    } catch {
      return null;
    }
  };

  const login = async (credentials) => {
    setLoading(true);
    try {
      const { data } = await api.post('/api/user/login', credentials);
      if (data?.user) {
        setUser(data.user);
        navigate('/dashboard');
        toast.success('Login successful');
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await api.post('/api/user/logout');
      setUser(null);
      navigate('/');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const checkAuth = async () => {
      const user = await verifyToken();
      if (user) {
        setUser(user);
        if (window.location.pathname === '/') {
          navigate('/dashboard');
        }
      }
    };
    checkAuth();
  }, [navigate]);

  return (
    <AuthContext.Provider value={{ 
      user, 
      loading, 
      login, 
      logout,
      api 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);