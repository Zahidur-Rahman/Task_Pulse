import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header.js";
import { SignUpUser } from "../services/TaskService.js";

export default function SignUp() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    try {
      const response = await SignUpUser({ email, password });
      navigate("/");
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
    <section>
      <Header />

      <div className="container py-md-5 py-5 " style={{ marginTop: "66px" }}>
        <div className="row">
          <div className="col-md-8 offset-md-2">
          <div className="card p-4 shadow-lg border-secondary text-center">
              <h2>Sign Up</h2>
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
                  ></input>
                </div>
                <div className="mb-3 text-start">
                  <label className="form-label">Password</label>
                  <input
                    type="password"
                    placeholder="Enter a minimum 6 character password"
                    value={password}
                    className="form-control"
                    onChange={(e) => setPassword(e.target.value)}
                  ></input>
                </div>
                <div>
                  <button type="submit" className="btn btn-info me-2">
                    Sign Up
                  </button>
                  <button type="button" onClick={() => navigate("/")} className="btn btn-secondary">Go Home</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
