import React, { useRef, useState } from "react";
import ReactCardFlip from "react-card-flip";

const CARD_WIDTH = 400;

const App = () => {
  const inputRef = useRef();
  const [pdfUrl, setPdfUrl] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [urlInput, setUrlInput] = useState("");
  const [isFlipped, setIsFlipped] = useState(false);

  const handleButtonClick = () => {
    inputRef.current.click();
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.type === "application/pdf") {
      const url = URL.createObjectURL(file);
      setPdfUrl(url);
      setShowModal(true);
    } else {
      alert("Please upload a PDF file.");
    }
  };

  const handleReplace = () => {
    setShowModal(false);
    setTimeout(() => {
      setPdfUrl(null);
      inputRef.current.click();
    }, 300);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsFlipped(true);
    setShowModal(false);
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      setShowModal(false);
    }
  };

  // Optional: Flip back function if you want to allow flipping back
  const handleFlipBack = () => setIsFlipped(false);

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#f6f7fb",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <ReactCardFlip isFlipped={isFlipped} flipDirection="vertical">
        {/* Front of the Card */}
        <div
          key="front"
          className="pulsating-card"
          style={{
            background: "#fff",
            borderRadius: 16,
            boxShadow: "0 8px 40px rgba(0,0,0,0.10)",
            padding: "48px 36px 36px 36px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            minWidth: CARD_WIDTH,
            animation: "pulse 2.2s infinite",
          }}
        >
          <h1
            style={{
              fontSize: "3rem",
              fontWeight: "bold",
              marginBottom: 48,
              color: "#333",
              animation: "pulse 2s infinite",
              letterSpacing: "2px",
              textAlign: "center",
              userSelect: "none",
            }}
          >
            Resume Optimizer
          </h1>
          <button
            onClick={handleButtonClick}
            style={{
              width: 180,
              height: 180,
              borderRadius: "50%",
              border: "none",
              background: "transparent",
              cursor: "pointer",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              animation: "pulse 2s infinite",
              boxShadow: "0 4px 24px rgba(0,0,0,0.06)",
            }}
            aria-label="Upload PDF"
          >
            <svg
              width="96"
              height="96"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#888"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 5 17 10" />
              <line x1="12" y1="5" x2="12" y2="19" />
            </svg>
          </button>
          <input
            ref={inputRef}
            type="file"
            accept="application/pdf"
            style={{ display: "none" }}
            onChange={handleFileChange}
          />
          <input
            type="text"
            placeholder="paste your URL here..."
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            className="pulse-input"
            style={{
              marginTop: 40,
              width: 320,
              padding: "16px 20px",
              fontSize: "1.1rem",
              borderRadius: 8,
              border: "1.5px solid #ccc",
              outline: "none",
              boxShadow: "0 2px 8px rgba(0,0,0,0.03)",
              transition: "border 0.2s",
              animation: "pulse 2s infinite",
            }}
          />
          <button
            style={{
              marginTop: 24,
              width: 320,
              padding: "16px 0",
              fontSize: "1.1rem",
              fontWeight: "bold",
              background: "#222",
              color: "#fff",
              border: "none",
              borderRadius: 8,
              cursor: "pointer",
              transition: "background 0.2s",
              boxShadow: "0 2px 8px rgba(0,0,0,0.03)",
            }}
            onClick={handleSubmit}
          >
            Submit
          </button>
        </div>

        {/* Back of the Card */}
        <div
          key="back"
          className="pulsating-card"
          style={{
            background: "#fff",
            borderRadius: 16,
            boxShadow: "0 8px 40px rgba(0,0,0,0.10)",
            padding: "48px 36px 36px 36px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            minWidth: CARD_WIDTH,
            minHeight: 500,
            animation: "pulse 2.2s infinite",
            justifyContent: "center",
          }}
        >
          <h1
            style={{
              fontSize: "2.5rem",
              fontWeight: "bold",
              color: "#222",
              letterSpacing: "2px",
              textAlign: "center",
              userSelect: "none",
            }}
          >
            Resume Optimizer Review
          </h1>
          {/* Optional: Flip back button for demo purposes */}
          {/* <button
            style={{
              marginTop: 32,
              padding: "12px 32px",
              fontSize: "1rem",
              borderRadius: 8,
              border: "1.5px solid #222",
              background: "#fff",
              color: "#222",
              cursor: "pointer",
            }}
            onClick={handleFlipBack}
          >
            Back
          </button> */}
        </div>
      </ReactCardFlip>

      {/* Modal */}
      {pdfUrl && (
        <div
          className={`modal-overlay${showModal ? " show" : ""}`}
          onClick={handleOverlayClick}
        >
          <div className={`modal-content${showModal ? " show" : ""}`}>
            <iframe
              src={pdfUrl}
              title="PDF Preview"
              width="100%"
              height="400px"
              style={{
                border: "1px solid #eee",
                borderRadius: 8,
                background: "#fafafa",
                marginBottom: 24,
              }}
            />
            <div style={{ display: "flex", justifyContent: "flex-end", gap: 16 }}>
              <button
                onClick={handleSubmit}
                style={{
                  padding: "10px 24px",
                  background: "#222",
                  color: "#fff",
                  border: "none",
                  borderRadius: 4,
                  fontSize: 16,
                  cursor: "pointer",
                }}
              >
                Submit
              </button>
              <button
                onClick={handleReplace}
                style={{
                  padding: "10px 24px",
                  background: "#fff",
                  color: "#222",
                  border: "1px solid #222",
                  borderRadius: 4,
                  fontSize: 16,
                  cursor: "pointer",
                }}
              >
                Replace
              </button>
            </div>
          </div>
          <style>{`
            .modal-overlay {
              position: fixed;
              top: 0; left: 0; right: 0; bottom: 0;
              background: rgba(0,0,0,0.6);
              display: flex;
              align-items: center;
              justify-content: center;
              opacity: 0;
              pointer-events: none;
              transition: opacity 0.3s ease;
              z-index: 1000;
            }
            .modal-overlay.show {
              opacity: 1;
              pointer-events: auto;
            }
            .modal-content {
              background: #fff;
              border-radius: 10px;
              box-shadow: 0 8px 40px rgba(0,0,0,0.18);
              padding: 32px 24px 24px 24px;
              min-width: 340px;
              max-width: 90vw;
              max-height: 90vh;
              opacity: 0;
              transform: translateY(-40px) scale(0.97);
              transition: opacity 0.3s cubic-bezier(.4,2,.6,1), transform 0.3s cubic-bezier(.4,2,.6,1);
            }
            .modal-content.show {
              opacity: 1;
              transform: translateY(0) scale(1);
            }
          `}</style>
        </div>
      )}
      <style>{`
        @keyframes pulse {
          0% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.04); opacity: 0.93; }
          100% { transform: scale(1); opacity: 1; }
        }
        .pulsating-card {
          animation: pulse 2.2s infinite;
        }
        .pulse-input {
          animation: pulse 2s infinite;
        }
        input[type="text"]:focus {
          border: 1.5px solid #888;
        }
      `}</style>
    </div>
  );
};

export default App;
