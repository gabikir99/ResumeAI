import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const Login = ({ onSwitchToRegister, onLoginSuccess }) => {
  const [email, setEmail] = useState(''); 
  const [password, setPassword] = useState(''); 
  const [error, setError] = useState(''); 

  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem('registeredUser'));
    if (stored) {
      setEmail(stored.email);
      setPassword(stored.password); 
    }
  }, []);

  const handleLogin = (e) => {
    e.preventDefault(); 
    const stored = JSON.parse(localStorage.getItem('registeredUser'));

    if (stored && stored.email === email && stored.password === password) {
      onLoginSuccess({
        name: stored.name || 'User',
        email: stored.email
      });
    } else {
      setError('Invalid email or password');
      alert('invalid email or password');
    }
  }
  return (
    <div className="login-container">
      <div className="login-modal">
        <h1>Welcome! Please login to the app</h1>
        <form onSubmit={handleLogin}>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email address..."
            autoComplete="username"
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password..."
            autoComplete="current-password"
          />
          <button type="submit">Login</button>
          {error && <p style={{color: 'red', fontSize: '0.9rem'}}>{error}</p>}
          <a href="#" onClick={(e) => { e.preventDefault(); onSwitchToRegister(); }}>
            Don’t have an account? Sign up
          </a>
        </form>
      </div>
    </div>
  );
};

const Registration = ({ onSignupSuccess, onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: ''
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
    
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Store user data (in real app, this would be handled by your backend)
      const userData = {
        id: Date.now(),
        name: formData.name,
        email: formData.email,
        registeredAt: new Date().toISOString()
      };
      
      localStorage.setItem('registeredUser', JSON.stringify({
        email: formData.email,
        password: formData.password
      }))
      // Call success callback
      onSignupSuccess(userData);
    } catch (error) {
      setErrors({ submit: 'Registration failed. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
     <div className="registration-container">
      <div className="registration-modal">
        <div className="modal-header">
          <h1>Create Account</h1>
          <p>Join us today and get started</p>
        </div>
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label htmlFor="name">Full Name</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className={errors.name ? 'error' : ''}
              placeholder="Enter your full name"
            />
            {errors.name && <p className="error-text">{errors.name}</p>}
          </div>

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
            {errors.email && <p className="error-text">{errors.email}</p>}
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
              placeholder="Create a password"
            />
            {errors.password && <p className="error-text">{errors.password}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              className={errors.confirmPassword ? 'error' : ''}
              placeholder="Confirm your password"
            />
            {errors.confirmPassword && <p className="error-text">{errors.confirmPassword}</p>}
          </div>

          {errors.submit && <div className="submit-error">{errors.submit}</div>}

          <button type="submit" disabled={isLoading} className="submit-button">
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </button>
          <button type='button' onClick={onSwitchToLogin} className='login-button'>login</button>
        </form>
      </div>
    </div>
  );
};

// Landing Page Component
const LandingPage = ({ user, onSendMessage, onFileUpload }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);

   const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (showChat && inputRef.current) {
      inputRef.current.focus();
    }
  }, [showChat]);

  const handleOpenChat = () => {
    setShowChat(true);
    setIsAnimating(true);
  };

  const handleCloseChat = () => {
    setIsAnimating(false);
    setTimeout(() => {
      setShowChat(false);
      setMessages([]);
      setInputMessage('');
      setSelectedFile(null); // Clear selected file on close
    }, 300);
  };

  const formatTime = () => {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleAttachmentClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      if (onFileUpload) onFileUpload(file);
    }
  };

  const simulateAIResponse = (userMessage, file) => {
    const responses = [
      file
        ? `Received your file: ${file.name}. I can analyze it for resume optimization. Would you like me to suggest improvements based on this file?`
        : "I'd be happy to help you optimize your resume! Could you tell me more about the specific job you're applying for?",
      "That's a great question! Based on current industry trends, I recommend highlighting your key achievements with quantifiable results.",
      "For that type of role, you'll want to emphasize your technical skills and any relevant project experience. What's your background?",
      "I can definitely help with that! Let me analyze the job requirements and suggest some improvements to make your resume stand out.",
      "Excellent! Here are some tips to make your resume more compelling for recruiters in that field...",
      "That's exactly the kind of experience employers are looking for! How would you like to present it on your resume?",
    ];
    return file ? responses[0] : responses[Math.floor(Math.random() * responses.length)];
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() && !selectedFile) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage.trim(),
      file: selectedFile ? { name: selectedFile.name } : null,
      sender: 'user',
      time: formatTime(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setSelectedFile(null); // Clear the file after sending
    fileInputRef.current.value = null; // Reset file input
    setIsTyping(true);

    // Simulate AI thinking time
    setTimeout(() => {
      const aiResponse = {
        id: Date.now() + 1,
        text: simulateAIResponse(userMessage.text, userMessage.file),
        sender: 'ai',
        time: formatTime(),
      };

      setMessages((prev) => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1000 + Math.random() * 2000); // Random delay between 1-3 seconds
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (showChat) {
    return (
      <div className={`chat-modal ${isAnimating ? 'modal-entering' : 'modal-exiting'}`}>
        <div className="chat-container">
          <div className="chat-header">
            <div className="chat-header-info">
              <div className="chat-avatar">🤖</div>
              <div>
                <h2 className="chat-title">AI Resume Assistant</h2>
                <p className="chat-subtitle">Online • Ready to help</p>
              </div>
            </div>
            <button onClick={handleCloseChat} className="close-button">
              ×
            </button>
          </div>

          <div className="chat-messages">
            {messages.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">💬</div>
                <h3 className="empty-state-title">Start the conversation</h3>
                <p className="empty-state-subtitle">
                  Ask me anything about resume optimization, job applications, or career advice!
                </p>
              </div>
            ) : (
              <>
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`message ${message.sender === 'user' ? 'user-message' : 'ai-message'}`}
                  >
                    <div className="message-avatar">
                      {message.sender === 'user' ? '👤' : '🤖'}
                    </div>
                    <div>
                      <div className="message-content">
                        {message.text}
                        {message.file && (
                          <div className="file-attachment">
                            📎 <span>{message.file.name}</span>
                          </div>
                        )}
                      </div>
                      <div className="message-time">{message.time}</div>
                    </div>
                  </div>
                ))}
                {isTyping && (
                  <div className="message ai-message">
                    <div className="message-avatar">🤖</div>
                    <div className="typing-indicator">
                      <div className="typing-dots">
                        <div className="typing-dot"></div>
                        <div className="typing-dot"></div>
                        <div className="typing-dot"></div>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-container">
            <div className="chat-input-wrapper">
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about resume optimization..."
                className="chat-input"
                rows="1"
                disabled={isTyping}
              />
              <button
                onClick={handleSendMessage}
                disabled={(!inputMessage.trim() && !selectedFile) || isTyping}
                className="send-button"
              >
                ➤
              </button>
              <button
                type="button"
                className="attach-button"
                onClick={handleAttachmentClick}
                title="Attach resume (PDF, DOC, DOCX)"
              >
                📎
              </button>
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                accept=".pdf,.doc,.docx"
                onChange={handleFileChange}
              />
              {selectedFile && (
                <span className="selected-file-name">{selectedFile.name}</span>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

 return (
    <div className="landing-container">
      {/* Background Elements */}
      <div className="background-elements">
        <div className="bg-element bg-element-1"></div>
        <div className="bg-element bg-element-2"></div>
        <div className="bg-element bg-element-3"></div>
      </div>

      <div className="main-content">
        <div className="content-grid">
          {/* Left Content */}
          <div className="left-content">
            <div className="badge">
              ⚡ AI-Powered Resume Optimization
            </div>
            
            <h1 className="main-heading">
              Land Your{' '}
              <span className="highlight-text">Dream Job</span>
            </h1>
            
            <p className="main-description">
              Transform your resume in seconds with AI. Our smart assistant analyzes job descriptions and tailors your resume to match exactly what employers are looking for.
            </p>

            <div className="tags-container">
              <div className="tag">
                👥 Perfect for Recent Graduates
              </div>
              <div className="tag">
                🎯 Job-Specific Optimization
              </div>
            </div>

            <button
              onClick={handleOpenChat}
              className="cta-button"
            >
              Start Chatting Now →
            </button>

            <div className="stats-container">
              <div className="stat">
                <div className="stat-number">10K+</div>
                <div className="stat-label">Resumes Optimized</div>
              </div>
              <div className="stat">
                <div className="stat-number">85%</div>
                <div className="stat-label">Interview Rate</div>
              </div>
              <div className="stat">
                <div className="stat-number">2min</div>
                <div className="stat-label">Average Time</div>
              </div>
            </div>
          </div>

          {/* Right Visual */}
          <div className="right-visual">
            <div className="ai-assistant-card">
              <div className="assistant-header">
                <div className="assistant-icon">⚡</div>
                <div className="assistant-info">
                  <h3 className="assistant-title">AI Resume Assistant</h3>
                  <p className="assistant-subtitle">Ready to help you succeed</p>
                </div>
              </div>
              
              <div className="process-steps">
                <div className="process-step process-step-1">
                  💬 Chat with our AI assistant
                </div>
                <div className="process-step process-step-2">
                  🎯 Get personalized advice
                </div>
                <div className="process-step process-step-3">
                  ✨ Optimize your resume instantly
                </div>
              </div>

              <div className="status-indicator">
                <div className="status-dot"></div>
                <span className="status-text">AI is online and ready</span>
              </div>
            </div>
            
            {/* Floating Elements */}
            <div className="floating-element floating-element-1"></div>
            <div className="floating-element floating-element-2"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
const App = () => {
  const [user, setUser] = useState(null);
   const [showRegistration, setShowRegistration] = useState(false);

  const handleSignupSuccess = (userData) => {
    setUser(userData);
  };

  // Show registration page if no user, otherwise show landing page
  if (!user) {
    return showRegistration ? ( 
    <Registration onSignupSuccess={handleSignupSuccess} onSwitchToLogin={() => setShowRegistration(false)} />
    ) : (
      <Login onSwitchToRegister={() => setShowRegistration(true)} onLoginSuccess={(userData) =>setUser(userData)} />
    );
  }
 

  return <LandingPage user={user} />;
};

export default App;