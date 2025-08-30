import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header.js";
import { loginUser } from "../services/TaskService.js";
import { useAuth } from "../context/AuthProvider";

export default function SignIn() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const { login } = useAuth(); // Use the context

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    try {
      const response = await loginUser({ email, password });
      
      // Get user info from the response
      const userData = {
        id: response.data.user.id,
        email: response.data.user.email,
        role: response.data.user.role
      };
      
      login(null, userData);
      console.log("Login successful:", userData);
      
      // Redirect based on user role
      if (userData.role === 'admin') {
        navigate('/admin/dashboard');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      console.error("Login failed:", err.response?.data || err);
      setError("Invalid email or password. Please try again.");
    }
  };

  return (
    <div>
     
      <Header />
   

      <div className="container py-md-5 py-5 mt-5">
        <div className="row">
          <div className="col-md-8 offset-md-2">
            <div className="card p-4 text-center">
              <h2>Sign In</h2>
              {error && (
                <div className="alert alert-danger mt-3" role="alert">
                  {error}
                </div>
              )}
              <form onSubmit={handleSubmit} className="mt-3 text-center">
                <div className="mb-3 text-start">
                  <label className="form-label">Email</label>
                  <input
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="form-control"
                  />
                </div>
                <div className="mb-3 text-start">
                  <label className="form-label">Password</label>
                  <input
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="form-control"
                  />
                </div>
                <div>
                  <button type="submit" className="btn btn-info me-2">
                    Submit
                  </button>
                  <button
                    type="button"
                    onClick={() => navigate("/")}
                    className="btn btn-secondary"
                  >
                    Go Home
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
