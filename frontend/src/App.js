import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import Registration from './Registration'; 
import Login from './Login';
import API_BASE from './api';
import LandingPage from './LandingPage'; 

// Main App Component
const App = () => {
  const [user, setUser] = useState(null);
  const [showRegistration, setShowRegistration] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is already logged in on app load
  useEffect(() => {
    const checkUserSession = async () => {
      try {
        const userId = sessionStorage.getItem('user_id');
        const sessionId = sessionStorage.getItem('session_id');
        
        if (userId && sessionId) {
          // Verify the session is still valid with the backend
          const response = await fetch(`${API_BASE}/api/user/${userId}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              'Session-ID': sessionId
            }
          });
          
          if (response.ok) {
            const userData = await response.json();
            setUser(userData.user);
          } else {
            // Session invalid, clear storage
            sessionStorage.removeItem('user_id');
            sessionStorage.removeItem('session_id');
          }
        }
      } catch (error) {
        console.error('Error checking user session:', error);
        // Clear invalid session data
        sessionStorage.removeItem('user_id');
        sessionStorage.removeItem('session_id');
      } finally {
        setIsLoading(false);
      }
    };

    checkUserSession();
  }, []);

  const handleSignupSuccess = (userData) => {
    setUser(userData);
    setShowRegistration(false);
  };

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    setShowLogin(false); 
  };

  const handleLogout = () => {
    setUser(null); 
    // Clear all session data
    sessionStorage.removeItem('user_id');
    sessionStorage.removeItem('session_id');
    sessionStorage.removeItem('registeredUser'); // Remove old sessionStorage data if it exists
  }; 

  // Show loading while checking session
  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '18px'
      }}>
        Loading...
      </div>
    );
  }

  // Show registration page if no user, otherwise show landing page
  if (!user) {
    return (
      <>
        <LandingPage 
          user={user} 
          onClickLogin={() => setShowLogin(true)} 
          onClickSignup={() => setShowRegistration(true)} 
        />

        {showLogin && (
          <Login 
            onClose={() => setShowLogin(false)}
            onSwitchToRegister={() => {
              setShowLogin(false); 
              setShowRegistration(true)
            }}
            onLoginSuccess={handleLoginSuccess} 
          />
        )}

        {showRegistration && (
          <Registration 
            onClose={() => setShowRegistration(false)}
            onSwitchToLogin={() => {
              setShowRegistration(false);
              setShowLogin(true);
            }}
            onSignupSuccess={handleSignupSuccess}
          />
        )}
      </>
    );
  }

  return <LandingPage user={user} onLogout={handleLogout} />;
};

export default App;