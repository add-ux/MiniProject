import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [usageCount, setUsageCount] = useState(0);
  const [showLimitModal, setShowLimitModal] = useState(false);

  // Load usage count from localStorage on component mount
  useEffect(() => {
    const storedUsage = localStorage.getItem('codeAnalyzerUsage');
    if (storedUsage) {
      setUsageCount(parseInt(storedUsage));
    }
  }, []);

  const handleSignup = () => navigate('/signup');
  const handleLogin = () => navigate('/login');

  const handleStartAnalysis = () => {
    const currentUsage = usageCount;
    
    if (currentUsage >= 2) {
      // Show limit modal when user exceeds free usage
      setShowLimitModal(true);
    } else {
      // Allow free analysis
      navigate('/analyze');
    }
  };

  const closeModal = () => {
    setShowLimitModal(false);
  };

  return (
    <div className="landing-wrapper">
      {/* Navigation */}
      <nav className="analyze-nav">
        <div className="analyze-nav-logo">
          <div className="brand-logo-img">
            <i className="fas fa-code"></i>
          </div>
          <span className="brand-name">Code<span>Analyzer</span></span>
        </div>
        <div className="analyze-nav-right">
          {usageCount > 0 && (
            <div className="usage-badge">
              <i className="fas fa-chart-simple"></i> {usageCount}/2 Free Uses
            </div>
          )}
          <button 
            className="analyze-profile-trigger"
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          >
            <span className="analyze-profile-icon"><i className="fas fa-user"></i></span>
            <span className="analyze-profile-label">Menu</span>
            <span className="analyze-profile-chevron"><i className="fas fa-chevron-down"></i></span>
          </button>
          {isDropdownOpen && (
            <div className="analyze-profile-dropdown">
              <button className="analyze-dropdown-item" onClick={handleLogin}>
                <i className="fas fa-sign-in-alt"></i> Login
              </button>
              <button className="analyze-dropdown-item" onClick={handleSignup}>
                <i className="fas fa-user-plus"></i> Sign Up
              </button>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <div className="hero-badge">
            <i className="fas fa-magic"></i> AI-Powered Analysis
          </div>
          <h1>
            Write Cleaner Code,<br />
            <span className="accent-text">Faster & Smarter</span>
          </h1>
          <p className="hero-description">
            Get instant, actionable insights on your code quality, security vulnerabilities, 
            and performance bottlenecks. Used by 10,000+ developers.
          </p>
          
          {/* Free Usage Info */}
          <div className="free-usage-info">
            <i className="fas fa-gift"></i> 
            <span>Try 2 free analyses — no credit card required!</span>
          </div>
          
          <button className="btn-primary" onClick={handleStartAnalysis}>
            Start Analyzing Free <i className="fas fa-arrow-right"></i>
          </button>
        </div>
        <div className="hero-visual">
          <div className="code-card">
            <div className="code-header">
              <div className="code-dot"></div>
              <div className="code-dot"></div>
              <div className="code-dot"></div>
            </div>
            <div className="code-snippet">
              {`function calculateTotal(items) {
  return items
    .filter(item => item.price > 0)
    .reduce((sum, item) => sum + item.price, 0);
}
// ✅ High readability score`}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-highlight">
        <div className="container">
          <h2 className="section-title">Deep Code Analysis in Seconds</h2>
          <div className="features-flex">
            <div className="feature-block">
              <div className="feature-icon"><i className="fas fa-chart-line"></i></div>
              <h4>Quality Metrics</h4>
              <p>Cyclomatic complexity, maintainability index, and duplication detection.</p>
            </div>
            <div className="feature-block">
              <div className="feature-icon"><i className="fas fa-shield-alt"></i></div>
              <h4>Security Audit</h4>
              <p>Detect OWASP Top 10 vulnerabilities, hardcoded secrets, and unsafe patterns.</p>
            </div>
            <div className="feature-block">
              <div className="feature-icon"><i className="fas fa-tachometer-alt"></i></div>
              <h4>Performance Insights</h4>
              <p>Identify bottlenecks, memory leaks, and inefficient algorithms.</p>
            </div>
            <div className="feature-block">
              <div className="feature-icon"><i className="fas fa-robot"></i></div>
              <h4>AI Recommendations</h4>
              <p>Get smart fixes with contextual explanations and best practices.</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="steps-section">
        <div className="container">
          <h2 className="section-title">How It Works</h2>
          <div className="steps-grid">
            <div className="step-item">
              <div className="step-number">1</div>
              <h3>Paste or Upload</h3>
              <p>Paste your code snippet or upload a file (JS, Python, Java, Go, Rust, etc.)</p>
            </div>
            <div className="step-item">
              <div className="step-number">2</div>
              <h3>Instant Analysis</h3>
              <p>Our AI scans your code for quality, security, and performance issues.</p>
            </div>
            <div className="step-item">
              <div className="step-number">3</div>
              <h3>Get Actionable Report</h3>
              <p>Receive a detailed report with scores, issue severity, and fix suggestions.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <div className="container" style={{ textAlign: 'center', padding: '2rem' }}>
        <div className="stats-grid">
          <div className="stat-item">
            <strong className="stat-number">10k+</strong>
            <span className="stat-label">Developers</span>
          </div>
          <div className="stat-item">
            <strong className="stat-number">50k+</strong>
            <span className="stat-label">Projects Analyzed</span>
          </div>
          <div className="stat-item">
            <strong className="stat-number">99%</strong>
            <span className="stat-label">Accuracy Rate</span>
          </div>
        </div>
      </div>

      {/* CTA Banner */}
      <div className="cta-section">
        <h2>Ready to level up your code quality?</h2>
        <p>Join thousands of developers who ship cleaner, safer code with CodeAnalyzer.</p>
        <button className="btn-cta-light" onClick={handleStartAnalysis}>
          Start Free Analysis <i className="fas fa-chevron-right"></i>
        </button>
      </div>

      {/* Footer */}
      <footer className="footer">
        <p>© 2025 CodeAnalyzer — AI-powered code quality platform</p>
      </footer>

      {/* Limit Modal - Shows when free trials are exhausted */}
      {showLimitModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-icon">
              <i className="fas fa-lock"></i>
            </div>
            <h2>Free Trials Exhausted</h2>
            <p>You've used both of your free analyses! 🎯</p>
            <p className="modal-message">
              Create a free account to unlock unlimited code analysis, 
              save your reports, and get personalized recommendations.
            </p>
            <div className="modal-buttons">
              <button className="modal-btn-secondary" onClick={closeModal}>
                Maybe Later
              </button>
              <button className="modal-btn-primary" onClick={handleSignup}>
                Sign Up Now <i className="fas fa-arrow-right"></i>
              </button>
            </div>
            <button className="modal-close" onClick={closeModal}>
              <i className="fas fa-times"></i>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LandingPage;