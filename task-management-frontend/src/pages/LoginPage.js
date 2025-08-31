import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthProvider';
import { loginUser } from '../services/TaskService';
import './LoginPage.css';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError(''); // Clear error when user types
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await loginUser(formData);
      console.log('Full login response:', response);
      console.log('Response status:', response.status);
      console.log('Response data:', response.data);
      
      // Check if login was successful (status 200)
      if (response.status === 200 && response.data) {
        // Handle different possible response structures
        let userData;
        
        if (response.data.user) {
          // Expected structure: { user: { id, email, role } }
          userData = {
            id: response.data.user.id,
            email: response.data.user.email,
            role: response.data.user.role
          };
        } else if (response.data.id) {
          // Alternative structure: { id, email, role } directly
          userData = {
            id: response.data.id,
            email: response.data.email,
            role: response.data.role
          };
        } else {
          // Fallback: use form data for basic info
          userData = {
            id: null,
            email: formData.email,
            role: 'user' // default role
          };
        }
        
        console.log('Processed user data:', userData);
        
        // Login with dual authentication (token + user data)
        const accessToken = response.data.access_token;
        login(accessToken, userData);
        
        // Redirect based on user role
        if (userData.role === 'admin') {
          navigate('/admin/dashboard');
        } else {
          navigate('/dashboard');
        }
      } else {
        console.error('Login failed - unexpected status or no data:', response);
        setError('Login failed. Please check your credentials.');
      }
    } catch (err) {
      console.error('Login error details:', {
        message: err.message,
        response: err.response,
        status: err.response?.status,
        data: err.response?.data
      });
      
      if (err.response?.status === 401) {
        setError('Invalid email or password.');
      } else if (err.response?.status === 422) {
        setError('Please check your input format.');
      } else {
        const errorMessage = err.response?.data?.detail || err.message || 'Login failed. Please try again.';
        setError(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };


  return (
    <div className="container-fluid d-flex align-items-center justify-content-center" style={{background: 'linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 50%, #81d4fa 100%)', minHeight: '100vh', padding: '2rem 0'}}>
      <div className="row w-100 justify-content-center">
        <div className="col-sm-10 col-md-6 col-lg-4 col-xl-3">
          <div className="form-modern animate-fade-in-up" style={{maxWidth: '350px', margin: '0 auto', padding: '2rem'}}>
            <div className="text-center mb-3">
              <img src="/image/logo.webp" alt="TaskPulse Logo" className="mb-2" style={{width: '60px', height: '60px', borderRadius: '50%'}} />
              <h2 className="fw-bold" style={{color: '#0369a1', fontSize: '1.5rem'}} >Welcome Back</h2>
              <p className="text-muted" style={{fontSize: '0.9rem'}}>Sign in to your TaskPulse account</p>
            </div>

            <form onSubmit={handleSubmit} className="login-form">
              {error && (
                <div className="error-message">
                  <i className="fas fa-exclamation-circle"></i>
                  {error}
                </div>
              )}

              <div className="form-group-modern">
                <label htmlFor="email" className="form-label-modern">
                  Email Address
                </label>
                <input
                  type="email"
                  className="form-control-modern"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  placeholder="Enter your email"
                />
              </div>

              <div className="form-group-modern">
                <label htmlFor="password" className="form-label-modern">
                  Password
                </label>
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="form-control-modern"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  <i className={`fas ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                </button>
              </div>

              <button
                type="submit"
                className="btn-modern btn-modern-primary w-100 mb-3"
                disabled={isLoading}
                style={{padding: '10px 20px', fontSize: '0.95rem'}}
              >
                {isLoading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Signing in...
                  </>
                ) : (
                  <>
                    <i className="bi bi-box-arrow-in-right me-2"></i>
                    Sign In
                  </>
                )}
              </button>
            </form>

            <div className="login-footer">
              <p style={{fontSize: '0.9rem', marginBottom: '1rem'}}>
                Don't have an account?{' '}
                <button
                  type="button"
                  className="link-button"
                  onClick={() => navigate('/signup')}
                >
                  Sign up here
                </button>
              </p>
              
              <div className="text-center">
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
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage; 