import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FaSearch, FaSpinner, FaExternalLinkAlt, FaSignOutAlt, FaTimes, FaCode } from "react-icons/fa";
import { SiLeetcode, SiCodeforces } from "react-icons/si";
import { useAuth } from './AuthContext';
import { useNavigate } from 'react-router-dom';
import Lottie from 'lottie-react';
import foxAnimation from './assets/fox-animation.json';
import { toast } from 'react-toastify';

const Dashboard = () => {
  const { api, logout, token } = useAuth();
  const [currentSearchPlatform, setCurrentSearchPlatform] = useState("all");
  const [query, setQuery] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedPlatform, setSelectedPlatform] = useState("all");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);
  const resultsContainerRef = useRef(null);
  const navigate = useNavigate();

  const SEARCH_TIMEOUT = 60000 * 2;

  // Redirect if no token
  useEffect(() => {
    if (!token) {
      navigate('/');
      toast.error('Please login to access dashboard');
    }
  }, [token, navigate]);

  // Handle API response errors
  useEffect(() => {
    const interceptor = api.interceptors.response.use(
      response => response,
      error => {
        if (error.response?.status === 401) {
          logout();
          navigate('/');
          toast.error('Session expired. Please login again.');
        }
        return Promise.reject(error);
      }
    );

    return () => {
      api.interceptors.response.eject(interceptor);
    };
  }, [api, logout, navigate]);

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    
    if (!token) {
      setError("Please login to search");
      navigate('/');
      return;
    }

    const trimmedQuery = query.trim();
    if (!trimmedQuery || loading) { 
      setError(loading ? "Please wait for current search to complete" : "Please enter a search query");
      return;
    }

    setSearchTerm(trimmedQuery);
    setCurrentSearchPlatform(selectedPlatform);  
    setHasSearched(true);
    setLoading(true);
    setError("");
    setResults([]);

    try {
      const requestBody = selectedPlatform !== "all"
        ? { query: trimmedQuery, filters: { platform: selectedPlatform } }
        : { query: trimmedQuery };

      const { data } = await api.post('/api/query', requestBody, {
        timeout: SEARCH_TIMEOUT
      });

      if (!data) throw new Error("Server returned empty response");
      if (data.error) throw new Error(data.error);

      const filteredResults = selectedPlatform !== "all"
        ? (Array.isArray(data) ? data : []).filter(item => 
            item.platform.toLowerCase() === selectedPlatform.toLowerCase()
          )
        : (Array.isArray(data) ? data : []);

      setResults(filteredResults);
    } catch (err) {
      setError(err.response?.data?.message || "Failed to fetch results");
    } finally {
      setLoading(false);
    }
  };

  const clearSearch = () => {
    setQuery("");
    setSearchTerm("");
    setSelectedPlatform("all");
    setResults([]);
    setError("");
    setHasSearched(false);
  };

  const handleLogout = async () => {
    try {
      await logout();
      setResults([]);
      setQuery("");
      navigate('/');
      toast.success('Logged out successfully');
    } catch (error) {
      console.error("Logout error:", error);
      // Force logout anyway
      setResults([]);
      setQuery("");
      navigate('/');
    }
  };

  const platformData = {
    all: {
      icon: <div className="flex items-center space-x-1">
        <SiLeetcode className="text-orange-500" />
        <SiCodeforces className="text-blue-400" />
      </div>,
      name: "All",
      color: "from-purple-500 to-indigo-500",
    },
    leetcode: {
      icon: <SiLeetcode className="text-orange-500" />,
      name: "LeetCode",
      color: "from-orange-500 to-orange-600",
    },
    codeforces: {
      icon: <SiCodeforces className="text-blue-400" />,
      name: "Codeforces",
      color: "from-blue-500 to-blue-600",
    },
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-4 md:p-8 font-sans text-gray-100 relative overflow-hidden">
      {/* Background elements */}
      <div className="absolute right-10 bottom-10 w-64 h-64 z-0 opacity-40 hover:opacity-70 transition-opacity">
        <Lottie animationData={foxAnimation} loop={true} />
      </div>
      <div className="absolute inset-0 bg-gradient-to-b from-blue-900/10 via-transparent to-purple-900/10 pointer-events-none z-0"></div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header */}
        <header className="flex justify-between items-center mb-8">
          <div className="flex items-center space-x-3 group">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center group-hover:from-blue-400 group-hover:to-purple-400 transition-all">
              <FaCode className="text-white text-lg" />
            </div>
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400 group-hover:from-blue-300 group-hover:to-purple-300 transition-all">
              CodeHunt
            </h1>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-gray-200 transition-all"
          >
            <FaSignOutAlt className="mr-2" />
            Logout
          </button>
        </header>

        {/* Search Section */}
        <div className="bg-gray-800/70 backdrop-blur-lg rounded-xl shadow-lg p-6 mb-8 border border-gray-700/50 relative overflow-hidden">
          <div className="absolute -right-20 -top-20 w-64 h-64 bg-blue-500/10 rounded-full filter blur-3xl"></div>
          <div className="absolute -left-20 -bottom-20 w-64 h-64 bg-purple-500/10 rounded-full filter blur-3xl"></div>

          <form onSubmit={handleSearch} className="relative z-10 space-y-4">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <FaSearch className="text-gray-500" />
              </div>
              <input
                type="text"
                placeholder="Search coding problems (e.g., 'binary search trees')"
                value={query}
                onChange={(e) => !loading && setQuery(e.target.value)}
                disabled={loading}
                className={`block w-full pl-12 pr-24 py-3 border border-gray-700 rounded-lg bg-gray-900/50 focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-200 placeholder-gray-500 transition-all ${
                  loading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              />
              <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex space-x-2">
                {query && (
                  <button
                    type="button"
                    onClick={() => !loading && clearSearch()}  
                    disabled={loading} 
                    className={`text-gray-400 hover:text-gray-200 p-2 ${
                      loading ? 'opacity-50 cursor-not-allowed' : ''
                    }`}  
                  >
                    <FaTimes />
                  </button>
                )}
                <button
                  type="submit"
                  className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-4 py-1.5 rounded-lg flex items-center disabled:opacity-70 hover:shadow-lg hover:shadow-blue-500/20 transition-all"
                  disabled={loading}
                >
                  {loading ? (
                    <FaSpinner className="animate-spin mr-2" />
                  ) : (
                    <FaSearch className="mr-2" />
                  )}
                  Search
                </button>
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              {Object.entries(platformData).map(([platform, data]) => (
                <button
                  key={platform}
                  type="button"
                  disabled={loading} 
                  className={`px-4 py-2 rounded-lg flex items-center text-sm transition-all ${
                    selectedPlatform === platform
                      ? `bg-gradient-to-r ${data.color} text-white shadow-md`
                      : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                  } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}  
                  onClick={() => !loading && setSelectedPlatform(platform)} 
                >
                  <span className="mr-2">
                    {data.icon}
                  </span>
                  {data.name}
                </button>
              ))}
            </div>
          </form>
        </div>

        {/* Results Section */}
        <div className="bg-gray-800/70 backdrop-blur-lg rounded-xl shadow-lg overflow-hidden border border-gray-700/50 relative">
          <div className="border-b border-gray-700/50 px-6 py-4 bg-gradient-to-r from-gray-800 to-gray-800/50">
            <h2 className="text-xl font-semibold text-gray-100 flex items-center">
              <FaSearch className="mr-3 text-blue-400" />
              Search Results
              {results.length > 0 && (
                <span className="ml-3 px-2 py-0.5 bg-blue-900/30 text-blue-400 rounded-full text-sm font-medium">
                  {results.length} {results.length === 1 ? "result" : "results"}
                </span>
              )}
            </h2>
          </div>

          <div
            ref={resultsContainerRef}
            className="min-h-[50vh] max-h-[65vh] overflow-y-auto p-4 md:p-6 custom-scrollbar"
          >
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="bg-red-900/30 border-l-4 border-red-500 p-4 mb-6 rounded-lg"
                >
                  <div className="flex justify-between items-center">
                    <div className="text-red-100 font-medium">{error}</div>
                    <button
                      onClick={() => setError("")}
                      className="text-red-300 hover:text-red-100"
                    >
                      <FaTimes />
                    </button>
                  </div>
                </motion.div>
              )}

              {loading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex flex-col items-center justify-center py-16"
                >
                  <div className="mb-6">
                    <FaSpinner className="text-4xl text-blue-400 animate-spin" />
                  </div>
                  <h3 className="text-xl font-medium text-gray-200 mb-2">
                    Searching for problems...
                  </h3>
                  <p className="text-gray-400">
                    Looking for "{searchTerm}" in {platformData[currentSearchPlatform].name}
                  </p>
                </motion.div>
              )}

              {!loading && results.length > 0 && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                >
                  {results.map((item, index) => (
                    <motion.div
                      key={`${item.problem_link}-${index}`}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                      whileHover={{ y: -3 }}
                      className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700 hover:border-blue-500/50 transition-all hover:shadow-lg hover:shadow-blue-500/10"
                    >
                      <div className="p-5">
                        <div className="flex items-center mb-3">
                          <span className="mr-2">
                            {platformData[item.platform.toLowerCase()]?.icon || (
                              <SiLeetcode className="text-orange-500" />
                            )}
                          </span>
                          <span className="text-sm font-medium text-gray-400">
                            {item.platform}
                          </span>
                        </div>

                        <h3 className="font-bold text-gray-100 mb-4 line-clamp-2">
                          {item.problem_name}
                        </h3>

                        <a
                          href={item.problem_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center justify-center w-full bg-gray-700 hover:bg-gray-600 text-blue-400 px-4 py-2 rounded-lg font-medium transition-all"
                        >
                          <span>View Problem</span>
                          <FaExternalLinkAlt className="ml-2 text-sm" />
                        </a>
                      </div>
                    </motion.div>
                  ))}
                </motion.div>
              )}

              {!loading && hasSearched && results.length === 0 && !error && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex flex-col items-center justify-center py-16"
                >
                  <div className="w-16 h-16 rounded-full bg-gray-700 flex items-center justify-center mb-6">
                    <FaSearch className="text-2xl text-blue-400" />
                  </div>
                  <h3 className="text-xl font-medium text-gray-200 mb-2">
                    No results found
                  </h3>
                  <p className="text-gray-400 mb-6">
                    No problems found for "{searchTerm}"
                  </p>
                  <button
                    onClick={clearSearch}
                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-200 rounded-lg transition-all"
                  >
                    Clear Search
                  </button>
                </motion.div>
              )}

              {!loading && !hasSearched && results.length === 0 && !error && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex flex-col items-center justify-center py-16"
                >
                  <div className="w-16 h-16 rounded-full bg-gray-700 flex items-center justify-center mb-6">
                    <FaSearch className="text-2xl text-blue-400" />
                  </div>
                  <h3 className="text-xl font-medium text-gray-200 mb-2">
                    Ready to search
                  </h3>
                  <p className="text-gray-400">
                    Enter your query to find coding problems
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
          height: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(31, 41, 55, 0.5);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(99, 102, 241, 0.6);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(99, 102, 241, 0.8);
        }
      `}</style>
    </div>
  );
};

export default Dashboard;