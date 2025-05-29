import React, { useState, useEffect } from 'react';
import './App.css';

export default function App() {
  const [showChatbot, setShowChatbot] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [uploadedResume, setUploadedResume] = useState(null);
  const [jobDescription, setJobDescription] = useState('');

  const handleResumeUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedResume(file.name);
    }
  };

  const handleOpenChatbot = () => {
    setShowChatbot(true);
    setIsAnimating(true);
  };

  const handleCloseChatbot = () => {
    setIsAnimating(false);
    setTimeout(() => {
      setShowChatbot(false);
    }, 300); // Match the CSS animation duration
  };

  const optimizeResume = () => {
    alert('Resume optimization would happen here!');
  };

  if (showChatbot) {
    return (
      <div className={`chatbot-container ${isAnimating ? 'chatbot-entering' : 'chatbot-exiting'}`}>
        <div className="chatbot-wrapper">
          <div className="chatbot-content">
            <div className="chatbot-header">
              <h2 className="chatbot-title">AI Resume Optimizer</h2>
              <button 
                onClick={handleCloseChatbot}
                className="close-button"
              >
                ×
              </button>
            </div>
            
            <div className="chatbot-grid">
              <div className="form-section">
                <div className="upload-section">
                  <label className="form-label">Upload Your Resume</label>
                  <div className="upload-area">
                    <div className="upload-icon">📄</div>
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={handleResumeUpload}
                      className="file-input"
                      id="resume-upload"
                    />
                    <label htmlFor="resume-upload" className="upload-label">
                      <span className="upload-text-primary">Click to upload</span>
                      <span className="upload-text-secondary"> or drag and drop</span>
                    </label>
                    {uploadedResume && (
                      <p className="upload-success">
                        ✓ {uploadedResume}
                      </p>
                    )}
                  </div>
                </div>

                <div className="textarea-section">
                  <label className="form-label">Job Description</label>
                  <textarea
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    placeholder="Paste the job description here..."
                    className="job-description-textarea"
                  />
                </div>

                <button
                  onClick={optimizeResume}
                  disabled={!uploadedResume || !jobDescription}
                  className={`optimize-button ${(!uploadedResume || !jobDescription) ? 'disabled' : ''}`}
                >
                  ⚡ Optimize My Resume
                </button>
              </div>

              <div className="how-it-works">
                <h3 className="how-it-works-title">How It Works</h3>
                <div className="steps-container">
                  <div className="step">
                    <div className="step-icon step-icon-1">📄</div>
                    <div className="step-content">
                      <div className="step-title">Upload Resume</div>
                      <div className="step-description">
                        Upload your current resume in PDF or Word format
                      </div>
                    </div>
                  </div>
                  <div className="step">
                    <div className="step-icon step-icon-2">🎯</div>
                    <div className="step-content">
                      <div className="step-title">Add Job Description</div>
                      <div className="step-description">
                        Paste the job posting you're applying for
                      </div>
                    </div>
                  </div>
                  <div className="step">
                    <div className="step-icon step-icon-3">⚡</div>
                    <div className="step-content">
                      <div className="step-title">Get Optimized</div>
                      <div className="step-description">
                        AI tailors your resume to match the job requirements
                      </div>
                    </div>
                  </div>
                </div>
              </div>
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
              onClick={handleOpenChatbot}
              className="cta-button"
            >
              Start Optimizing Now →
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
                  📄 Upload your current resume
                </div>
                <div className="process-step process-step-2">
                  🎯 Paste the job description
                </div>
                <div className="process-step process-step-3">
                  ✨ Get your optimized resume instantly
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
}