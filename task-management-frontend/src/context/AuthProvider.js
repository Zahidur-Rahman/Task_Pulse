import React, { createContext, useState, useContext, useEffect } from "react";

const AuthContext = createContext();

export { AuthContext };

export function AuthProvider({ children }) {
  const [user, setUser] = useState(JSON.parse(localStorage.getItem("user")) || null);
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem("user"));

  const login = (token, userData) => {
    // Store both token and user data for dual authentication support
    if (token) {
      localStorage.setItem("access_token", token);
    }
    if (userData) {
      localStorage.setItem("user", JSON.stringify(userData));
      setUser(userData);
    }
    
    setIsAuthenticated(true);
  };

  const logout = async () => {
    try {
      // Call logout endpoint to clear HttpOnly cookie
      const { logoutUser } = await import('../services/TaskService');
      await logoutUser();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local state regardless of backend response
      setUser(null);
      setIsAuthenticated(false);
      localStorage.removeItem('user');
      localStorage.removeItem('access_token');
    }
  };

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
        setIsAuthenticated(true);
      } catch (e) {
        console.error("Error parsing stored user data:", e);
        localStorage.removeItem("user");
        setIsAuthenticated(false);
      }
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
