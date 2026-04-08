import { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./analyzepage.css";

function AnalyzePage() {
  const navigate = useNavigate();
  const [profileOpen, setProfileOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("upload");
  const [selectedFile, setSelectedFile] = useState(null);
  const [codeText, setCodeText] = useState("");
  const [language, setLanguage] = useState("python");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [usageCount, setUsageCount] = useState(0);
  const [showLimitModal, setShowLimitModal] = useState(false);
  
  const fileInputRef = useRef(null);
  const username = localStorage.getItem("auth_username") || "Profile";

  // Load usage count from localStorage
  useEffect(() => {
    const storedUsage = localStorage.getItem('codeAnalyzerUsage');
    if (storedUsage) {
      setUsageCount(parseInt(storedUsage));
    } else {
      setUsageCount(0);
    }
  }, []);

  const hasFreeTrials = () => {
    if (localStorage.getItem("auth_username")) {
      return true;
    }
    return usageCount < 2;
  };

  const incrementUsage = () => {
    const newCount = usageCount + 1;
    setUsageCount(newCount);
    localStorage.setItem('codeAnalyzerUsage', newCount);
    return newCount;
  };

  const handleLogout = () => {
    setProfileOpen(false);
    localStorage.removeItem("auth_username");
    navigate("/login");
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && isValidFileType(file.name)) {
      setSelectedFile(file);
      setError(null);
    } else {
      setError("Invalid file type. Please upload .py, .c, .cpp files");
    }
  };

  const isValidFileType = (filename) => {
    const validExtensions = ['.py', '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp'];
    return validExtensions.some(ext => filename.toLowerCase().endsWith(ext));
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && isValidFileType(file.name)) {
      setSelectedFile(file);
      setError(null);
    } else if (file) {
      setError("Invalid file type. Please upload .py, .c, .cpp files");
    }
  };

  const handleCancelFile = () => {
    setSelectedFile(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleAnalyzeFile = async () => {
    if (!hasFreeTrials()) {
      setShowLimitModal(true);
      return;
    }

    if (!selectedFile) {
      setError("Please select a file first");
      return;
    }
    
    setLoading(true);
    setError(null);
    setResults(null);
    
    const formData = new FormData();
    formData.append("file", selectedFile);
    
    try {
      const response = await fetch("http://localhost:5000/api/analyze", {
        method: "POST",
        body: formData,
      });
      
      const data = await response.json();
      
      if (data.success) {
        setResults(data.results);
        if (!localStorage.getItem("auth_username")) {
          const newCount = incrementUsage();
          if (newCount >= 2) {
            setTimeout(() => {
              setShowLimitModal(true);
            }, 1500);
          }
        }
      } else {
        setError(data.error || "Analysis failed");
      }
    } catch (err) {
      setError("Failed to connect to server. Make sure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzePaste = async () => {
    if (!hasFreeTrials()) {
      setShowLimitModal(true);
      return;
    }

    if (!codeText.trim()) {
      setError("Please paste some code to analyze");
      return;
    }
    
    setLoading(true);
    setError(null);
    setResults(null);
    
    try {
      const response = await fetch("http://localhost:5000/api/analyze-text", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          code: codeText,
          language: language,
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setResults(data.results);
        if (!localStorage.getItem("auth_username")) {
          const newCount = incrementUsage();
          if (newCount >= 2) {
            setTimeout(() => {
              setShowLimitModal(true);
            }, 1500);
          }
        }
      } else {
        setError(data.error || "Analysis failed");
      }
    } catch (err) {
      setError("Failed to connect to server. Make sure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleClearResults = () => {
    setResults(null);
    setError(null);
  };

  const getSeverityClass = (severity) => {
    switch(severity?.toUpperCase()) {
      case "CRITICAL": return "critical";
      case "HIGH": return "high";
      case "MEDIUM": return "medium";
      default: return "low";
    }
  };

  const getRemainingTrials = () => {
    if (localStorage.getItem("auth_username")) return "Unlimited";
    return Math.max(0, 2 - usageCount);
  };

  // Check if there's code to analyze (either uploaded file or pasted code)
  const hasCodeToAnalyze = () => {
    if (activeTab === "upload") {
      return selectedFile !== null;
    } else {
      return codeText.trim().length > 0;
    }
  };

  // Get graph data from results
  const getGraphData = () => {
    if (!results) return null;
    
    return {
      readabilityScore: results.readability?.score || 0,
      totalIssues: results.summary?.total_issues || 0,
      criticalIssues: results.summary?.critical_issues || 0,
      complexity: results.readability?.cyclomatic_complexity || 0,
      memoryIssues: results.memory_issues?.length || 0,
      securityIssues: results.security_issues?.length || 0,
      grade: results.readability?.grade || "N/A",
      status: results.summary?.status || "N/A"
    };
  };

  return (
    <div className="analyze-page">
      {/* Navigation Bar */}
      <nav className="analyze-nav">
        <Link to="/" className="analyze-nav-logo">
          <img src="/log.png" alt="Logo" className="analyze-logo" />
        </Link>
        
        <div className="analyze-nav-right">
          <div className="nav-controls">
            {!localStorage.getItem("auth_username") && (
              <div className="usage-badge-nav">
                <i className="fa fa-chart-simple"></i>
                <span>{getRemainingTrials()}/2 Free Uses</span>
              </div>
            )}
            {localStorage.getItem("auth_username") && (
              <div className="usage-badge-nav premium">
                <i className="fa fa-crown"></i>
                <span>Premium</span>
              </div>
            )}
            
            <button
              type="button"
              className="analyze-profile-trigger"
              onClick={() => setProfileOpen(!profileOpen)}
            >
              <span className="analyze-profile-icon">
                <i className="fa fa-user-circle"></i>
              </span>
              <span className="analyze-profile-label">{username}</span>
              <i className={`fa fa-chevron-${profileOpen ? "up" : "down"} analyze-profile-chevron`}></i>
            </button>
          </div>
          
          {profileOpen && (
            <>
              <div className="analyze-profile-backdrop" onClick={() => setProfileOpen(false)} />
              <div className="analyze-profile-dropdown">
                <Link to="/analyze" className="analyze-dropdown-item" onClick={() => setProfileOpen(false)}>
                  <i className="fa fa-user"></i> {username}
                </Link>
                {!localStorage.getItem("auth_username") && (
                  <div className="analyze-dropdown-item trial-info">
                    <i className="fa fa-gift"></i> Free Trials Left: {getRemainingTrials()}
                  </div>
                )}
                <button className="analyze-dropdown-item analyze-dropdown-logout" onClick={handleLogout}>
                  <i className="fa fa-sign-out"></i> Logout
                </button>
              </div>
            </>
          )}
        </div>
      </nav>
      
      {/* Main Content */}
      <main className="analyze-main">
        <div className="analyze-container">
          {/* Header */}
          <div className="analyze-header">
            <h1>Code Quality Analyzer</h1>
            <p>Check your code for readability issues, memory safety, and security vulnerabilities</p>
            {!localStorage.getItem("auth_username") && (
              <div className="free-trial-banner">
                <i className="fa fa-info-circle"></i>
                You have {getRemainingTrials()} free {getRemainingTrials() === 1 ? 'analysis' : 'analyses'} remaining. 
                <Link to="/signup" className="signup-link"> Sign up</Link> for unlimited access!
              </div>
            )}
          </div>

          {/* Two Column Layout */}
          <div className="two-column-layout">
            {/* Left Column - Upload/Paste Section */}
            <div className="left-column">
              <div className="analyze-tabs">
                <button 
                  className={`analyze-tab ${activeTab === "upload" ? "active" : ""}`}
                  onClick={() => {
                    setActiveTab("upload");
                    setResults(null);
                    setError(null);
                  }}
                >
                  <i className="fa fa-cloud-upload"></i> Upload File
                </button>
                <button 
                  className={`analyze-tab ${activeTab === "paste" ? "active" : ""}`}
                  onClick={() => {
                    setActiveTab("paste");
                    setResults(null);
                    setError(null);
                  }}
                >
                  <i className="fa fa-code"></i> Paste Code
                </button>
              </div>

              {/* Upload Tab Content */}
              {activeTab === "upload" && (
                <div className="analyze-upload-section">
                  {!selectedFile ? (
                    <div 
                      className={`upload-area ${isDragging ? "dragging" : ""}`}
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      onDrop={handleDrop}
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <i className="fa fa-file-code-o"></i>
                      <h3>Drag & Drop Your Code File</h3>
                      <p>or click to browse</p>
                      <p className="file-hint">
                        <i className="fa fa-check-circle"></i> Supported: .py, .c, .cpp, .cc, .h, .hpp
                      </p>
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept=".py,.c,.cpp,.cc,.cxx,.h,.hpp"
                        onChange={handleFileSelect}
                        style={{ display: "none" }}
                      />
                      <button className="btn-browse" onClick={(e) => {
                        e.stopPropagation();
                        fileInputRef.current?.click();
                      }}>
                        <i className="fa fa-folder-open"></i> Browse Files
                      </button>
                    </div>
                  ) : (
                    <div className="selected-file-card">
                      <div className="file-info">
                        <i className="fa fa-file-code"></i>
                        <div className="file-details">
                          <span className="file-name">{selectedFile.name}</span>
                          <span className="file-size">
                            {(selectedFile.size / 1024).toFixed(2)} KB
                          </span>
                        </div>
                      </div>
                      <div className="file-actions">
                        <button className="btn-cancel" onClick={handleCancelFile}>
                          <i className="fa fa-times"></i> Cancel
                        </button>
                        <button className="btn-analyze" onClick={handleAnalyzeFile}>
                          <i className="fa fa-chart-line"></i> Analyze
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Paste Tab Content */}
              {activeTab === "paste" && (
                <div className="analyze-paste-section">
                  <div className="language-selector">
                    <label>
                      <i className="fa fa-code"></i> Programming Language:
                    </label>
                    <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                      <option value="python"> Python</option>
                      <option value="c"> C</option>
                      <option value="cpp"> C++</option>
                    </select>
                  </div>
                  <textarea
                    className="code-input"
                    placeholder="Paste your code here..."
                    value={codeText}
                    onChange={(e) => setCodeText(e.target.value)}
                  ></textarea>
                  <button className="btn-analyze-paste" onClick={handleAnalyzePaste}>
                    <i className="fa fa-chart-line"></i> Analyze Code
                  </button>
                </div>
              )}
            </div>

            {/* Right Column - Graph Section */}
            <div className="right-column">
              <div className="graph-section">
                <h3 className="graph-title">
                  <i className="fa fa-chart-line"></i> Analysis Graph
                </h3>
                
                {!hasCodeToAnalyze() ? (
                  // No code uploaded or pasted
                  <div className="graph-placeholder">
                    <div className="empty-circle">
                      <div className="circle">
                        <i className="fa fa-code"></i>
                        <span>No Graph</span>
                      </div>
                    </div>
                    <p className="placeholder-text">
                      <i className="fa fa-info-circle"></i>
                      Upload a file or paste code to see analysis graph
                    </p>
                  </div>
                ) : !results ? (
                  // Code exists but not analyzed yet
                  <div className="graph-placeholder">
                    <div className="empty-circle">
                      <div className="circle">
                        <i className="fa fa-chart-line"></i>
                        <span>No Graph</span>
                      </div>
                    </div>
                    <p className="placeholder-text">
                      <i className="fa fa-info-circle"></i>
                      Click "Analyze" to generate graph
                    </p>
                  </div>
                ) : (
                  // Results available - show graphs
                  <div className="graph-content">
                    {/* Readability Score Circle */}
                    <div className="graph-card">
                      <h4>Readability Score</h4>
                      <div className="circle-progress">
                        <svg viewBox="0 0 120 120">
                          <circle cx="60" cy="60" r="54" fill="none" stroke="#e5e7eb" strokeWidth="8"/>
                          <circle 
                            cx="60" cy="60" r="54" fill="none" 
                            stroke="#10b981" strokeWidth="8"
                            strokeDasharray={`${(getGraphData()?.readabilityScore / 100) * 339.3} 339.3`}
                            strokeLinecap="round"
                            transform="rotate(-90 60 60)"
                          />
                          <text x="60" y="70" textAnchor="middle" fontSize="24" fontWeight="bold" fill="#1f2937">
                            {getGraphData()?.readabilityScore}
                          </text>
                          <text x="60" y="85" textAnchor="middle" fontSize="10" fill="#6b7280">/100</text>
                        </svg>
                        <div className={`grade ${getGraphData()?.grade?.toLowerCase()}`}>
                          Grade: {getGraphData()?.grade}
                        </div>
                      </div>
                    </div>

                    {/* Issues Distribution */}
                    <div className="graph-card">
                      <h4>Issues Distribution</h4>
                      <div className="donut-chart">
                        <div className="donut-segments">
                          <div className="donut-segment critical" style={{ 
                            width: `${(getGraphData()?.criticalIssues / (getGraphData()?.totalIssues || 1)) * 100}%` 
                          }}>
                            Critical: {getGraphData()?.criticalIssues}
                          </div>
                          <div className="donut-segment memory" style={{ 
                            width: `${(getGraphData()?.memoryIssues / (getGraphData()?.totalIssues || 1)) * 100}%` 
                          }}>
                            Memory: {getGraphData()?.memoryIssues}
                          </div>
                          <div className="donut-segment security" style={{ 
                            width: `${(getGraphData()?.securityIssues / (getGraphData()?.totalIssues || 1)) * 100}%` 
                          }}>
                            Security: {getGraphData()?.securityIssues}
                          </div>
                        </div>
                      </div>
                      <div className="stats-summary">
                        <div className="stat">
                          <span className="stat-color total"></span>
                          <span>Total: {getGraphData()?.totalIssues}</span>
                        </div>
                        <div className="stat">
                          <span className="stat-color critical"></span>
                          <span>Critical: {getGraphData()?.criticalIssues}</span>
                        </div>
                      </div>
                    </div>

                    {/* Complexity Meter */}
                    <div className="graph-card">
                      <h4>Cyclomatic Complexity</h4>
                      <div className="complexity-meter">
                        <div className="meter-bar">
                          <div className="meter-fill" style={{ 
                            width: `${Math.min(100, (getGraphData()?.complexity / 20) * 100)}%`,
                            background: getGraphData()?.complexity > 10 ? '#dc2626' : getGraphData()?.complexity > 5 ? '#f59e0b' : '#10b981'
                          }}></div>
                        </div>
                        <div className="meter-labels">
                          <span>Low</span>
                          <span>Medium</span>
                          <span>High</span>
                        </div>
                        <div className="complexity-value">
                          Value: {getGraphData()?.complexity}
                        </div>
                      </div>
                    </div>

                    {/* Status Badge */}
                    <div className={`status-card ${getGraphData()?.status?.toLowerCase()}`}>
                      <i className={`fa ${getGraphData()?.status === 'PASS' ? 'fa-check-circle' : getGraphData()?.status === 'CAUTION' ? 'fa-exclamation-triangle' : 'fa-times-circle'}`}></i>
                      <div>
                        <div className="status-label">Overall Status</div>
                        <div className="status-value">{getGraphData()?.status}</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Loading Indicator */}
          {loading && (
            <div className="loading-overlay">
              <div className="loading-card">
                <div className="spinner"></div>
                <h3>Analyzing Your Code</h3>
                <p>Checking for issues...</p>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && !loading && (
            <div className="error-message">
              <i className="fa fa-exclamation-circle"></i>
              <div>
                <h4>Error</h4>
                <p>{error}</p>
              </div>
              <button onClick={() => setError(null)} className="close-error">
                <i className="fa fa-times"></i>
              </button>
            </div>
          )}

          {/* Results Section (Full Details) */}
          {results && !loading && (
            <div className="results-section">
              <div className="results-header">
                <h2><i className="fa fa-chart-bar"></i> Detailed Analysis Results</h2>
                <button className="btn-clear-results" onClick={handleClearResults}>
                  <i className="fa fa-times"></i> Clear
                </button>
              </div>

              {/* Summary Cards */}
              <div className="summary-grid">
                <div className="summary-card status">
                  <div className="card-icon"><i className="fa fa-clipboard-check"></i></div>
                  <div className="card-content">
                    <span className="card-label">Status</span>
                    <span className={`card-value ${results.summary?.status?.toLowerCase()}`}>
                      {results.summary?.status || "N/A"}
                    </span>
                  </div>
                </div>
                <div className="summary-card issues">
                  <div className="card-icon"><i className="fa fa-exclamation-triangle"></i></div>
                  <div className="card-content">
                    <span className="card-label">Total Issues</span>
                    <span className="card-value">{results.summary?.total_issues || 0}</span>
                  </div>
                </div>
                <div className="summary-card readability">
                  <div className="card-icon"><i className="fa fa-book-open"></i></div>
                  <div className="card-content">
                    <span className="card-label">Readability Score</span>
                    <span className="card-value">{results.readability?.score || "N/A"}/100</span>
                  </div>
                </div>
                <div className="summary-card security">
                  <div className="card-icon"><i className="fa fa-shield-alt"></i></div>
                  <div className="card-content">
                    <span className="card-label">Critical Issues</span>
                    <span className="card-value">{results.summary?.critical_issues || 0}</span>
                  </div>
                </div>
              </div>

              {/* Code Metrics */}
              {results.metrics && (
                <div className="detail-card">
                  <h3><i className="fa fa-chart-line"></i> Code Metrics</h3>
                  <div className="metrics-grid">
                    <div className="metric">
                      <span className="metric-label">Total Lines</span>
                      <span className="metric-value">{results.metrics.total_lines}</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Code Lines</span>
                      <span className="metric-value">{results.metrics.code_lines}</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Comment Lines</span>
                      <span className="metric-value">{results.metrics.comment_lines}</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Comment Ratio</span>
                      <span className="metric-value">{(results.metrics.comment_ratio * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Readability */}
              {results.readability && (
                <div className="detail-card">
                  <h3><i className="fa fa-book"></i> Readability Analysis</h3>
                  <div className="readability-details">
                    <div className="readability-item">
                      <span>Cyclomatic Complexity:</span>
                      <strong>{results.readability.cyclomatic_complexity || "N/A"}</strong>
                    </div>
                    <div className="readability-item">
                      <span>Max Nesting Depth:</span>
                      <strong>{results.readability.max_nesting_depth || "N/A"}</strong>
                    </div>
                    <div className="readability-item">
                      <span>Grade:</span>
                      <strong className="grade">{results.readability.grade || "N/A"}</strong>
                    </div>
                  </div>
                </div>
              )}

              {/* Memory Issues */}
              {results.memory_issues && results.memory_issues.length > 0 && (
                <div className="detail-card">
                  <h3><i className="fa fa-memory"></i> Memory Safety Issues</h3>
                  <div className="issues-list">
                    {results.memory_issues.map((issue, idx) => (
                      <div key={idx} className={`issue ${getSeverityClass(issue.severity)}`}>
                        <div className="issue-header">
                          <span className="issue-type">{issue.type}</span>
                          <span className={`severity ${getSeverityClass(issue.severity)}`}>
                            {issue.severity}
                          </span>
                        </div>
                        {issue.line && <div className="issue-line">Line {issue.line}</div>}
                        <div className="issue-message">{issue.message}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Security Issues */}
              {results.security_issues && results.security_issues.length > 0 && (
                <div className="detail-card">
                  <h3><i className="fa fa-lock"></i> Security Issues</h3>
                  <div className="issues-list">
                    {results.security_issues.map((issue, idx) => (
                      <div key={idx} className={`issue ${getSeverityClass(issue.severity)}`}>
                        <div className="issue-header">
                          <span className="issue-type">{issue.type}</span>
                          <span className={`severity ${getSeverityClass(issue.severity)}`}>
                            {issue.severity}
                          </span>
                        </div>
                        {issue.line && <div className="issue-line">Line {issue.line}</div>}
                        <div className="issue-message">{issue.message}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* No Issues Found */}
              {(!results.memory_issues || results.memory_issues.length === 0) && 
               (!results.security_issues || results.security_issues.length === 0) && (
                <div className="success-message">
                  <i className="fa fa-check-circle"></i>
                  <h3>No Issues Found!</h3>
                  <p>Your code looks clean and secure. Great job! 🎉</p>
                </div>
              )}

              {/* Recommendations */}
              <div className="detail-card recommendations">
                <h3><i className="fa fa-lightbulb"></i> Recommendations</h3>
                <ul>
                  {results.summary?.status === "FAIL" && (
                    <>
                      <li>🔴 Fix all CRITICAL security issues immediately</li>
                      <li>🟡 Address memory safety issues to prevent crashes</li>
                      {results.readability?.score < 50 && <li>📖 Improve code readability by reducing complexity</li>}
                    </>
                  )}
                  {results.summary?.status === "CAUTION" && (
                    <>
                      <li>🟠 Review security issues - they could lead to vulnerabilities</li>
                      {results.readability?.score < 70 && <li>📖 Consider refactoring to improve maintainability</li>}
                    </>
                  )}
                  {results.summary?.status === "PASS" && (
                    <li>✅ Great job! Your code is clean, readable, and secure! 🎉</li>
                  )}
                </ul>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Limit Modal */}
      {showLimitModal && (
        <div className="modal-overlay" onClick={() => setShowLimitModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-icon">
              <i className="fa fa-lock"></i>
            </div>
            <h2>Free Trials Exhausted</h2>
            <p>You've used both of your free analyses! 🎯</p>
            <p className="modal-message">
              Create a free account to unlock unlimited code analysis, 
              save your reports, and get personalized recommendations.
            </p>
            <div className="modal-buttons">
              <button className="modal-btn-secondary" onClick={() => setShowLimitModal(false)}>
                Maybe Later
              </button>
              <button className="modal-btn-primary" onClick={() => navigate("/signup")}>
                Sign Up Now <i className="fa fa-arrow-right"></i>
              </button>
            </div>
            <button className="modal-close" onClick={() => setShowLimitModal(false)}>
              <i className="fa fa-times"></i>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default AnalyzePage;