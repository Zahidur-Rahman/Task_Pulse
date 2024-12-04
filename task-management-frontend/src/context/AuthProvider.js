import React, { createContext, useState, useContext, useEffect } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("accessToken") || null);

  // Validate the token (e.g., check expiration if applicable)
  const validateToken = (token) => {
    if (!token) return false;

    try {
      const decoded = JSON.parse(atob(token.split('.')[1])); // Decode JWT
      const expiryTime = decoded.exp * 1000; // Convert to milliseconds
      return expiryTime > Date.now(); // Check if the token is still valid
    } catch (e) {
      return false; // Return false if decoding fails
    }
  };

  const login = (newToken) => {
    localStorage.setItem("accessToken", newToken);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem("accessToken");
    setToken(null);
  };

  useEffect(() => {
    const storedToken = localStorage.getItem("accessToken");
    if (storedToken && validateToken(storedToken)) {
      setToken(storedToken);
    } else {
      // Clear invalid or expired token
      localStorage.removeItem("accessToken");
      setToken(null);
    }
  }, []); // This effect runs only once when the component mounts

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
