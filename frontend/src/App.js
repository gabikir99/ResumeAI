import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import Registration from './Registration'; 
import Login from './Login';
import LandingPage from './LandingPage'; 


// Main App Component
const App = () => {
  const [user, setUser] = useState(null);
  const [showRegistration, setShowRegistration] = useState(false);
  const [showLogin, setShowLogin] = useState(false); 

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
    sessionStorage.removeItem('registeredUser');
  }; 

  // Show registration page if no user, otherwise show landing page
  if (!user) {
    return (
   <>
    <LandingPage user={user} onClickLogin={() => setShowLogin(true)} onClickSignup={() => setShowRegistration(true)} />

      {showLogin && (
        <Login onClose={() => setShowLogin(false)}
        onSwitchToRegister={() => {
          setShowLogin(false); 
          setShowRegistration(true)
        }}
        onLoginSuccess={handleLoginSuccess} />
      )}
      {showRegistration && (
          <Registration onClose={() => setShowRegistration(false)}
            onSwitchToLogin={() => {
              setShowRegistration(false);
              setShowLogin(true);
            }}
            onSignupSuccess={handleSignupSuccess}
          />
        )}
   </>
   );
  };
  return <LandingPage user={user} onLogout={handleLogout} />;
};

export default App;
