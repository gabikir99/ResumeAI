import React, {useState, useRef, useEffect} from 'react';
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

// Feedback Modal Component
const FeedbackModal = ({ isOpen, onClose, onSubmit, externalSuccess, setExternalSuccess }) => {
  const [feedback, setFeedback] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (isOpen && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!feedback.trim()) return;

    setIsSubmitting(true);
    
    try {
      // Simulate API call
      await onSubmit(feedback);
      setIsSuccess(true);
      setTimeout(() => {
        setIsSuccess(false);
        setFeedback('');
        onClose();
      }, 2000);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setFeedback('');
      setIsSuccess(false);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="feedback-modal-overlay" onClick={handleClose}>
      <div className="feedback-modal" onClick={(e) => e.stopPropagation()}>
        <div className="feedback-modal-header">
          <div className="feedback-modal-title">
            <span className="feedback-icon">💭</span>
            <h3>Share Your Feedback</h3>
          </div>
          <button 
            className="feedback-close-btn"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            ×
          </button>
        </div>

        <div className="feedback-modal-content">
          {isSuccess ? (
            <div className="feedback-success">
              <div className="success-icon">✅</div>
              <h4>Thank you for your feedback!</h4>
              <p>We appreciate your input and will use it to improve our service.</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <div className="feedback-form-group">
                <label htmlFor="feedback-text">
                  Tell us what you think about our AI Resume Assistant
                </label>
                <textarea
                  ref={textareaRef}
                  id="feedback-text"
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  placeholder="Share your experience, suggestions, or report any issues..."
                  className="feedback-textarea"
                  rows="5"
                  disabled={isSubmitting}
                  maxLength={1000}
                />
                <div className="character-count">
                  {feedback.length}/1000
                </div>
              </div>

              <div className="feedback-modal-actions">
                <button
                  type="button"
                  onClick={handleClose}
                  className="feedback-btn feedback-btn-secondary"
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="feedback-btn feedback-btn-primary"
                  disabled={!feedback.trim() || isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <span className="loading-spinner"></span>
                      Sending...
                    </>
                  ) : (
                    'Send Feedback'
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

// Landing Page Component
const LandingPage = ({ user, onSendMessage, onFileUpload, onClickLogin, onClickSignup, onLogout }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [userName, setUserName] = useState('');
  const [connectionError, setConnectionError] = useState(false);
  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);
  const [rateLimitInfo, setRateLimitInfo] = useState({ remaining: 50, total: 50 });
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

 const fetchRateLimitInfo = async (sessionIdToUse = sessionId) => {
  try {
    const res = await fetch(`${API_BASE}/api/rate-limit/status?session_id=${sessionIdToUse}`);
    if (!res.ok) throw new Error('Failed to fetch rate limit status');
    const data = await res.json();
    console.log("✅ Rate limit data:", data);
    setRateLimitInfo({ remaining: data.messages_remaining, total: data.messages_limit });
  } catch (err) {
    console.error('Error fetching rate limit status:', err);
  }
};

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (showChat && inputRef.current) {
      inputRef.current.focus();
    }
  }, [showChat]);

  const handleFeedbackSubmit = async (feedbackText) => {

    try {
    
      const response = await fetch(`${API_BASE}/api/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedback: feedbackText, user_id: user?.id })
    });

    if (response.ok) {
      setFeedbackSubmitted(true);
    } else {
      console.error("email could not be sent");
    }
  } catch (error) {
    console.error('error submitting feedback', error);
  }

  
  };

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

  // Fixed API base URL
  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  // Persist session ID so chats remain consistent across reloads
  const [sessionId, setSessionId] = useState(() => {
    let storedSessionID = sessionStorage.getItem('session_id') || null
     if (!storedSessionID) {
    storedSessionID = 'session_'+ Date.now() + '_' + Math.random().toString(36).substr(2,9); 
    sessionStorage.setItem('session_id', storedSessionID);
  }
  return storedSessionID; 
});
 

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

 const simulateTyping = (text, messageId, delay = 30) => {
  return new Promise((resolve) => {
    let currentIndex = 0;
    const words = text.split(' ');
    
    const typeNextWord = () => {
      if (currentIndex < words.length) {
        const currentText = words.slice(0, currentIndex + 1).join(' ');
        
        setMessages(prev =>
          prev.map(msg =>
            msg.id === messageId 
              ? { ...msg, text: currentText, isStreaming: true } 
              : msg
          )
        );
        
        currentIndex++;
        setTimeout(typeNextWord, delay);
      } else {
        // Finished typing
        setMessages(prev =>
          prev.map(msg =>
            msg.id === messageId 
              ? { ...msg, text: text, isStreaming: false } 
              : msg
          )
        );
        resolve();
      }
    };
    
    typeNextWord();
  });
};
const handleStreamingResponse = async (response, messageId) => {
  if (response.body) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let accumulatedText = '';
    let chunkCount = 0;

    try {
      // Collect all chunks
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        chunkCount++;
        const chunk = decoder.decode(value, { stream: true });
        accumulatedText += chunk;
      }

      if (accumulatedText.trim()) {
        const wordCount = accumulatedText.trim().split(' ').length;
        
        // Force typing simulation for responses with less than 50 words or single chunks
        if (wordCount < 50 || chunkCount === 1) {
          console.log(`🎯 Using typing simulation (${wordCount} words, ${chunkCount} chunks)`);
          await simulateTyping(accumulatedText.trim(), messageId, 35);
        } else {
          console.log(`⚡ Using instant display (${wordCount} words, ${chunkCount} chunks)`);
          setMessages(prev =>
            prev.map(msg =>
              msg.id === messageId 
                ? { ...msg, text: accumulatedText.trim(), isStreaming: false } 
                : msg
            )
          );
        }
        return accumulatedText;
      }
    } catch (streamError) {
      console.log('❌ Streaming failed:', streamError);
    }
  }

  // Fallback
  try {
    const fullResponse = await response.text();
    if (fullResponse.trim()) {
      await simulateTyping(fullResponse.trim(), messageId, 35);
      return fullResponse;
    }
  } catch (textError) {
    console.log("❌ Failed to get text response:", textError);
  }

  return '';
};

const handleFIleSend = async (responseId) => {
  if (!selectedFile) {
    console.error("No file selected");
    return;
  }

  const formData = new FormData(); 
  formData.append('file', selectedFile);
  formData.append('session_id', sessionId);

  try {
    console.log("Making request to:", `${API_BASE}/api/upload/pdf`);
    
    const response = await fetch(`${API_BASE}/api/upload/pdf`, {
      method: 'POST',
      body: formData
    }); 

    console.log("Response status:", response.status);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Upload failed with status: ${response.status} - ${errorText}`);
    }

    const result = await response.json(); 
    console.log("File upload result:", result);

    // Update session ID if provided by backend
    if (result.session_id) {
      setSessionId(result.session_id);
      console.log("Updated session_id from file upload:", result.session_id);
    }

    // Use typing simulation for file upload response
    const responseText = result.response || result.message || 'File uploaded successfully';
    await simulateTyping(responseText, responseId, 20); // Slightly faster for file responses

    // Update rate limit info
    await fetchRateLimitInfo();

  } catch(error) {
    console.error("Couldn't send the file attachment:", error);
    
    setMessages(prev =>
      prev.map(msg =>
        msg.id === responseId
          ? { 
              ...msg, 
              text: `Error uploading file: ${error.message}`, 
              isStreaming: false, 
              isError: true 
            }
          : msg
      )
    );
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
  const originalMessage = inputMessage.trim();
  setInputMessage('');
  setIsTyping(true);
  setConnectionError(false);

  inputRef.current?.focus();

  const aiResponseId = Date.now() + 1;
  const aiResponseTime = formatTime();

  setMessages((prev) => [
    ...prev,
    {
      id: aiResponseId,
      text: 'bot is typing...',
      sender: 'ai',
      time: aiResponseTime,
      isStreaming: true
    }
  ]);

  let currentSessionId = sessionId;
  console.log("Sending with session_id", currentSessionId);

  try {
    if (selectedFile && originalMessage.trim()) {
      // BOTH file and text message
      console.log("Processing both file and text message");
      
      // First, handle the file upload (this has its own response handling)
      await handleFIleSend(aiResponseId);
      
      // Then, create a new AI response for the text message
      const textResponseId = Date.now() + 2;
      setMessages((prev) => [
        ...prev,
        {
          id: textResponseId,
          text: 'Processing your additional question...',
          sender: 'ai',
          time: formatTime(),
          isStreaming: true
        }
      ]);
      
      // Handle the text message with streaming/typing simulation
      const response = await fetch(`${API_BASE}/api/chat-stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: originalMessage, 
          session_id: currentSessionId 
        })
      });

      if (response.ok) {
        await handleStreamingResponse(response, textResponseId);
      } else {
        throw new Error(`API request failed with status: ${response.status}`);
      }
      
    } else if (selectedFile) {
      // Only file - use existing file handler with typing simulation
      await handleFIleSend(aiResponseId);
      
    } else if (originalMessage.trim()) {
      // Only text message
      const response = await fetch(`${API_BASE}/api/chat-stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: originalMessage, 
          session_id: currentSessionId 
        })
      });

      if (response.ok) {
        const responseText = await handleStreamingResponse(response, aiResponseId);
        await fetchRateLimitInfo();
      } else {
        // Fallback to regular API call
        console.log('Streaming failed, trying regular API...');
        const fallbackResponse = await fetch(`${API_BASE}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            message: originalMessage, 
            session_id: currentSessionId 
          })
        });

        if (!fallbackResponse.ok) {
          throw new Error(`API request failed with status: ${fallbackResponse.status}`);
        }

        const data = await fallbackResponse.json();
        
        if (data.session_id) {
          currentSessionId = data.session_id;
          setSessionId(data.session_id);
          console.log("Received new session_id from backend:", currentSessionId);
        }

        // Use typing simulation for fallback response too
        await simulateTyping(data.response || 'Sorry, I couldn\'t generate a response.', aiResponseId);
        await fetchRateLimitInfo(currentSessionId);
      }
    }

  } catch (error) {
    console.error('Error in handleSendMessage:', error);
    setConnectionError(true);

    const errorMessage = connectionError 
      ? `Connection error: ${error.message}\n\nPlease check that your backend server is running on ${API_BASE}`
      : `Sorry, I encountered an error: ${error.message}`;

    setMessages(prev =>
      prev.map(msg =>
        msg.id === aiResponseId
          ? { ...msg, text: errorMessage, isStreaming: false, isError: true }
          : msg
      )
    );
  } finally {
    setIsTyping(false);
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
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
                <p style={{color: 'lightgreen', fontWeight: '600'}}>Remaining free messages left: {rateLimitInfo.remaining}/{rateLimitInfo.total}</p>
                
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
            <div className="chat-header-actions">
              <button
                onClick={() => setIsFeedbackModalOpen(true)}
                className="feedback-header-btn"
                title="Share feedback"
              >
                💭
              </button>
              <button onClick={handleCloseChat} className="close-button">
                ×
              </button>
            </div>
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
                      <div className="message-time">
                        {message.time}
                        {message.isStreaming && (
                          <span className="streaming-indicator"> ...</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
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
                readOnly={isTyping}
                style={{
                  cursor: isTyping ? 'wait' : 'text'
                }}
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

        <FeedbackModal
          isOpen={isFeedbackModalOpen}
          onClose={() => setIsFeedbackModalOpen(false)}
          onSubmit={handleFeedbackSubmit}
          externalSuccess={feedbackSubmitted}
          setExternalSuccess={setFeedbackSubmitted}
        />
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

      {/* Floating Feedback Button */}
      <button
        onClick={() => setIsFeedbackModalOpen(true)}
        className="floating-feedback-btn"
        title="Share your feedback"
      >
        <span className="feedback-btn-icon">💭</span>
        <span className="feedback-btn-text">Feedback</span>
      </button>

      <div className="main-content">
        {!user && ( 
          <div className='auth-buttons'>
            <button className='auth-btn login' onClick={onClickLogin}>Login</button>
            <button className='auth-btn' onClick={onClickSignup}>Sign up</button>
          </div>
        )}
        {user && (
          <div className='auth-buttons'>
            <button className='auth-btn' onClick={onLogout}>Sign Out</button>
          </div>
        )}
        
        <div className="content-grid">
          {/* Left Content */}
          <div className="left-content">
            <div className="badge">
              ⚡ AI-Powered Resume Optimization
            </div>
            
            <h1 className="main-heading">
              Land Your{' '}
              <span className="highlight-text">Dream Job with ResumindAI</span>
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

      <FeedbackModal
        isOpen={isFeedbackModalOpen}
        onClose={() => setIsFeedbackModalOpen(false)}
        onSubmit={handleFeedbackSubmit}
      />
    </div>
  );
};

export default LandingPage;