import React, { useState, useEffect, useRef } from 'react';
import './App.css';

// Simple markdown renderer component
const MarkdownRenderer = ({ text }) => {
  const formatMarkdown = (text) => {
    if (!text) return '';
    
    let formatted = text;
    
    // Bold text: **text** or __text__
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/__(.*?)__/g, '<strong>$1</strong>');
    
    // Italic text: *text* or _text_
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    formatted = formatted.replace(/_(.*?)_/g, '<em>$1</em>');
    
    // Code blocks: ```code```
    formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    
    // Inline code: `code`
    formatted = formatted.replace(/`(.*?)`/g, '<code>$1</code>');
    
    // Headers: ### Header
    formatted = formatted.replace(/^### (.*$)/gm, '<h3>$1</h3>');
    formatted = formatted.replace(/^## (.*$)/gm, '<h2>$1</h2>');
    formatted = formatted.replace(/^# (.*$)/gm, '<h1>$1</h1>');
    
    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    // Lists: - item or * item
    formatted = formatted.replace(/^[-*] (.*$)/gm, '<li>$1</li>');
    formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    // Numbered lists: 1. item
    formatted = formatted.replace(/^\d+\. (.*$)/gm, '<li>$1</li>');
    
    return formatted;
  };

  return (
    <div 
      dangerouslySetInnerHTML={{ __html: formatMarkdown(text) }}
      style={{ lineHeight: '1.6' }}
    />
  );
};

const Login = ({ onSwitchToRegister, onLoginSuccess }) => {
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
      alert('No registered user found. Please sign up first.');
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
      
      // Store user data
      const userData = {
        id: Date.now(),
        name: formData.name,
        email: formData.email,
        password: formData.password,
        registeredAt: new Date().toISOString()
      };
      
      // Use sessionStorage instead of localStorage
      sessionStorage.setItem('registeredUser', JSON.stringify(userData));
      
      // Call success callback
      onSignupSuccess({
        name: userData.name,
        email: userData.email
      });
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
              required
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
              required
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
              required
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
              required
            />
            {errors.confirmPassword && <p className="error-text">{errors.confirmPassword}</p>}
          </div>

          {errors.submit && <div className="submit-error">{errors.submit}</div>}

          <button type="submit" disabled={isLoading} className="submit-button">
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </button>
          <button type='button' onClick={onSwitchToLogin} className='login-button'>
            Already have an account? Login
          </button>
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
  const [connectionError, setConnectionError] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState('');
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
    setConnectionError(false);
  };

  const handleCloseChat = () => {
    setIsAnimating(false);
    setTimeout(() => {
      setShowChat(false);
      setMessages([]);
      setInputMessage('');
      setSelectedFile(null);
      setConnectionError(false);
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
      // Validate file type
      const allowedTypes = ['.pdf', '.doc', '.docx', '.txt'];
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
      
      if (!allowedTypes.includes(fileExtension)) {
        alert('Please upload a PDF, DOC, DOCX, or TXT file.');
        return;
      }
      
      // Validate file size (10MB limit)
      const maxSize = 10 * 1024 * 1024; // 10MB in bytes
      if (file.size > maxSize) {
        alert('File size must be less than 10MB.');
        return;
      }
      
      setSelectedFile(file);
      if (onFileUpload) onFileUpload(file);
    }
  };

  // Fixed API base URL - this was the main issue
  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  // Persist session ID so chats remain consistent across reloads
  const [sessionId, setSessionId] = useState(() =>
    sessionStorage.getItem('session_id') || null
  );

  useEffect(() => {
    if (sessionId) {
      sessionStorage.setItem('session_id', sessionId);
    }
  }, [sessionId]);

  // Test server connection when chat opens
  useEffect(() => {
    if (showChat) {
      testServerConnection();
    }
  }, [showChat]);

  // Streaming text effect
  const streamText = (text, callback) => {
    setStreamingMessage('');
    setIsTyping(true);
    
    let index = 0;
    const interval = setInterval(() => {
      if (index < text.length) {
        setStreamingMessage(prev => prev + text[index]);
        index++;
      } else {
        clearInterval(interval);
        setIsTyping(false);
        setStreamingMessage('');
        callback(text);
      }
    }, 20); // Adjust speed here (lower = faster)
    
    return () => clearInterval(interval);
  };

  const testServerConnection = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Server connection successful:', data);
      setConnectionError(false);
    } catch (error) {
      console.error('Server connection failed:', error);
      setConnectionError(true);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() && !selectedFile) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage.trim(),
      file: selectedFile ? { name: selectedFile.name, size: selectedFile.size } : null,
      sender: 'user',
      time: formatTime(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);
    setConnectionError(false);

    try {
      let aiText = '';
      let newSession = sessionId;

      if (selectedFile) {
        const formData = new FormData();
        formData.append('file', selectedFile);
        if (sessionId) formData.append('session_id', sessionId);

        console.log('Uploading file to:', `${API_BASE}/api/upload`);
        
        const response = await fetch(`${API_BASE}/api/upload`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Upload failed with status: ${response.status}`);
        }

        const data = await response.json();
        aiText = data.response || 'File uploaded successfully, but no response received.';
        newSession = data.session_id || newSession;
        
        // Clear file input after successful upload
        fileInputRef.current.value = '';
        setSelectedFile(null);
      } else {
        console.log('Sending message to:', `${API_BASE}/api/chat`);
        
        const response = await fetch(`${API_BASE}/api/chat`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            message: userMessage.text, 
            session_id: sessionId 
          }),
        });

        if (!response.ok) {
          throw new Error(`Chat request failed with status: ${response.status}`);
        }

        const data = await response.json();
        aiText = data.response || 'Message sent successfully, but no response received.';
        newSession = data.session_id || newSession;
      }

      if (newSession && newSession !== sessionId) {
        setSessionId(newSession);
      }

      const aiResponse = {
        id: Date.now() + 1,
        text: aiText,
        sender: 'ai',
        time: formatTime(),
      };
      setMessages((prev) => [...prev, aiResponse]);
      
    } catch (error) {
      console.error('Error in handleSendMessage:', error);
      setConnectionError(true);
      
      let errorMessage = 'Sorry, I encountered an error. ';
      
      if (error.message.includes('Failed to fetch')) {
        errorMessage += 'Please make sure the backend server is running on http://localhost:5000';
      } else if (error.message.includes('status: 500')) {
        errorMessage += 'There was a server error. Please check the backend logs.';
      } else if (error.message.includes('status: 404')) {
        errorMessage += 'The API endpoint was not found. Please check the backend configuration.';
      } else {
        errorMessage += `Error: ${error.message}`;
      }
      
      const aiResponse = {
        id: Date.now() + 1,
        text: errorMessage,
        sender: 'ai',
        time: formatTime(),
        isError: true,
      };
      setMessages((prev) => [...prev, aiResponse]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleRetryConnection = () => {
    testServerConnection();
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
                <p className="chat-subtitle">
                  {connectionError ? (
                    <span style={{ color: '#ff6b6b' }}>
                      ⚠️ Connection Error - 
                      <button 
                        onClick={handleRetryConnection}
                        style={{ 
                          background: 'none', 
                          border: 'none', 
                          color: '#ff6b6b', 
                          textDecoration: 'underline',
                          cursor: 'pointer',
                          fontSize: 'inherit'
                        }}
                      >
                        Retry
                      </button>
                    </span>
                  ) : (
                    'Online • Ready to help'
                  )}
                </p>
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
                {connectionError && (
                  <div style={{ 
                    marginTop: '1rem', 
                    padding: '1rem', 
                    backgroundColor: '#fff3cd', 
                    border: '1px solid #ffeaa7', 
                    borderRadius: '8px',
                    color: '#856404'
                  }}>
                    <strong>⚠️ Server Connection Issue</strong>
                    <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.9rem' }}>
                      Make sure your Flask backend is running on port 5000:
                      <br />
                      <code style={{ 
                        backgroundColor: '#f8f9fa', 
                        padding: '2px 6px', 
                        borderRadius: '4px',
                        fontSize: '0.8rem'
                      }}>
                        python app.py
                      </code>
                    </p>
                  </div>
                )}
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
                      <div className={`message-content ${message.isError ? 'error-message' : ''}`}>
                        {message.sender === 'ai' && !message.isError ? (
                          <MarkdownRenderer text={message.text} />
                        ) : (
                          message.text
                        )}
                        {message.file && (
                          <div className="file-attachment">
                            📎 <span>{message.file.name}</span>
                            {message.file.size && (
                              <span className="file-size">
                                ({(message.file.size / 1024).toFixed(1)} KB)
                              </span>
                            )}
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
                      {streamingMessage ? (
                        <div className="message-content">
                          <MarkdownRenderer text={streamingMessage} />
                        </div>
                      ) : (
                        <div className="typing-dots">
                          <div className="typing-dot"></div>
                          <div className="typing-dot"></div>
                          <div className="typing-dot"></div>
                        </div>
                      )}
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
                title="Send message"
              >
                ➤
              </button>
              <button
                type="button"
                className="attach-button"
                onClick={handleAttachmentClick}
                title="Attach resume (PDF, DOC, DOCX, TXT)"
                disabled={isTyping}
              >
                📎
              </button>
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleFileChange}
              />
              {selectedFile && (
                <div className="selected-file-info">
                  <span className="selected-file-name">{selectedFile.name}</span>
                  <button
                    onClick={() => {
                      setSelectedFile(null);
                      fileInputRef.current.value = '';
                    }}
                    className="remove-file-button"
                    title="Remove file"
                  >
                    ×
                  </button>
                </div>
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

  const handleLoginSuccess = (userData) => {
    setUser(userData);
  };

  // Show registration page if no user, otherwise show landing page
  if (!user) {
    return showRegistration ? ( 
      <Registration 
        onSignupSuccess={handleSignupSuccess} 
        onSwitchToLogin={() => setShowRegistration(false)} 
      />
    ) : (
      <Login 
        onSwitchToRegister={() => setShowRegistration(true)} 
        onLoginSuccess={handleLoginSuccess} 
      />
    );
  }

  return <LandingPage user={user} />;
};

export default App;