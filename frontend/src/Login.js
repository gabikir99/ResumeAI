import React, { useState } from 'react';
import API_BASE from './api';

const Login = ({ onLoginSuccess, onSwitchToRegister, onClose }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsLoading(true);
    
    try {
      // Send login data to your Flask backend
      const response = await fetch(`${API_BASE}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      });

      const data = await response.json();

      if (data.success) {
        // Login successful
        console.log('Login successful:', data.user);
        
        // Create session after successful login
        try {
          const sessionRes = await fetch('http://localhost:5000/api/session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'new' })
          });

          const sessionData = await sessionRes.json();
          if (sessionData.session_id) {
            // Store session ID but NOT user data in sessionStorage
            sessionStorage.setItem('session_id', sessionData.session_id);
            // Optionally store just the user ID for session management
            sessionStorage.setItem('user_id', data.user.id.toString());
          }
        } catch (e) {
          console.error('Session creation failed:', e);
        }
        
        // Call success callback with user data
        onLoginSuccess({
          id: data.user.id,
          name: data.user.name,
          email: data.user.email
        });
      } else {
        // Login failed
        setErrors({ submit: data.message || 'Login failed. Please check your credentials.' });
      }
    } catch (error) {
      console.error('Login error:', error);
      setErrors({ 
        submit: 'Unable to connect to server. Please check your internet connection and try again.' 
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="login-container">
        <div className="login-modal">
          <button className="close-btn" onClick={onClose}>&times;</button>
          
          <h1>Welcome Back</h1>
          <p>Sign in to your account</p>

          <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className={errors.email ? 'error' : ''}
              placeholder="Enter your email"
            />
            {errors.email && <span className="error-text">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              className={errors.password ? 'error' : ''}
              placeholder="Enter your password"
            />
            {errors.password && <span className="error-text">{errors.password}</span>}
          </div>

          {errors.submit && (
            <div className="error-text submit-error">{errors.submit}</div>
          )}

          <button 
            type="submit" 
            className="submit-button"
            disabled={isLoading}
          >
            {isLoading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>

        <div className="auth-footer">
          <p>Don't have an account? 
            <button 
              type="button" 
              className="link-btn" 
              onClick={onSwitchToRegister}
            >
              Sign Up
            </button>
          </p>
        </div>
      </div>
    </div>
  </div>
  );
};

export default Login;