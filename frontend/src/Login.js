import React, {useState, useRef, useEffect} from 'react';
const Login = ({ onSwitchToRegister, onLoginSuccess, onClose }) => {
  const [email, setEmail] = useState(''); 
  const [password, setPassword] = useState(''); 
  const [error, setError] = useState(''); 

  useEffect(() => {
    // Use in-memory storage instead of localStorage for Claude artifacts
    const stored = sessionStorage.getItem('registeredUser');
    if (stored) {
      const userData = JSON.parse(stored);
      setEmail(userData.email);
      setPassword(userData.password); 
    }
  }, []);

  const handleLogin = (e) => {
    e.preventDefault(); 
    const stored = sessionStorage.getItem('registeredUser');

    if (stored) {
      const userData = JSON.parse(stored);
      if (userData.email === email && userData.password === password) {
        onLoginSuccess({
          name: userData.name || 'User',
          email: userData.email
        });
      } else {
        setError('Invalid email or password');
        alert('Invalid email or password');
      }
    } else {
      setError('No registered user found. Please sign up first.');
    
    }
  }

  return (
    <div className='modal-overlay'>
      
    <div className="login-container">
      <div className="login-modal">
        <h1>Welcome!</h1>
      <p>Please login to the app</p>
        <form onSubmit={handleLogin}>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email address..."
            autoComplete="username"
            required
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password..."
            autoComplete="current-password"
            required
          />
          <button type="submit">Login</button>
          {error && <p style={{color: 'red', fontSize: '0.9rem'}}>{error}</p>}
          <a href="#" onClick={(e) => { e.preventDefault(); onSwitchToRegister(); }}>
            Don't have an account? Sign up
          </a>
        </form>
        <button className='close-btn' onClick={onClose}>X</button>
      </div>
      
    </div>
    
    </div>
  
  );
};
export default Login;
