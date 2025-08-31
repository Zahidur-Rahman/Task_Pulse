import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { SignUpUser } from "../services/TaskService.js";

export default function SignUp() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    try {
      await SignUpUser({ email, password, firstName, lastName });
      setSuccess("Account created successfully! Please login.");
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {
      if (err.response?.status === 422) {
        setError(err.response.data?.detail[0]?.msg || "Invalid input.");
      } else {
        setError("Error occurred. Try again.");
      }
      console.error("Sign-up failed:", err);
    }
  };

  return (
    <section className="py-5" style={{background: 'linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 50%, #81d4fa 100%)', minHeight: '100vh'}}>
      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-sm-10 col-md-8 col-lg-6 col-xl-5">
          <div className="form-modern animate-fade-in-up text-center">
              <div className="text-center mb-4">
                <img src="/image/logo.webp" alt="TaskPulse Logo" className="mb-3" style={{width: '80px', height: '80px', borderRadius: '50%'}} />
                <h2 className="fw-bold" style={{color: '#0369a1', fontSize: '1.75rem'}}>Create Account</h2>
                <p className="text-muted">Join TaskPulse to manage your tasks</p>
              </div>
              {error && (
                <div className="alert alert-danger mt-3" role="alert">
                  {error}
                </div>
              )}
              {success && (
                <div className="alert alert-success mt-3" role="alert">
                  {success}
                </div>
              )}
              <form onSubmit={handleSubmit} className="mt-3 text-center">
                <div className="row">
                  <div className="col-md-6">
                    <div className="form-group-modern">
                      <label className="form-label-modern">First Name</label>
                      <input
                        type="text"
                        placeholder="Enter your first name"
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        className="form-control-modern"
                        required
                      />
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="form-group-modern">
                      <label className="form-label-modern">Last Name</label>
                      <input
                        type="text"
                        placeholder="Enter your last name"
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        className="form-control-modern"
                        required
                      />
                    </div>
                  </div>
                </div>
                <div className="form-group-modern">
                  <label className="form-label-modern">Email</label>
                  <input
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="form-control-modern"
                    required
                  />
                </div>
                <div className="form-group-modern">
                  <label className="form-label-modern">Password</label>
                  <input
                    type="password"
                    placeholder="Enter a minimum 6 character password"
                    value={password}
                    className="form-control-modern"
                    onChange={(e) => setPassword(e.target.value)}
                    minLength="6"
                    required
                  />
                </div>
                <div className="d-grid gap-2">
                  <button type="submit" className="btn-modern btn-modern-primary">
                    <i className="bi bi-person-plus me-2"></i>
                    Create Account
                  </button>
                  <div className="text-center mt-3">
                    <p className="mb-3">
                      Already have an account?{' '}
                      <button
                        type="button"
                        className="link-button"
                        onClick={() => navigate('/login')}
                      >
                        Sign in here
                      </button>
                    </p>
                    
                    <button
                      type="button"
                      className="btn btn-outline-secondary btn-sm"
                      onClick={() => navigate('/')}
                      style={{fontSize: '0.85rem', padding: '0.5rem 1rem'}}
                    >
                      <i className="bi bi-house me-1"></i>
                      Back to Homepage
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
