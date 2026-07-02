import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

function Home() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('project');
  const [faqOpen, setFaqOpen] = useState(0);
  const [promptValue, setPromptValue] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const toggleFaq = (index) => {
    setFaqOpen(faqOpen === index ? -1 : index);
  };

  return (
    <div className="stitch-container">
      {/* Background Glows */}
      <div className="stitch-glow top-glow"></div>
      <div className="stitch-glow bottom-glow"></div>

      {/* Sticky Header */}
      <header className="stitch-header">
        <div className="stitch-logo-container">
          <span className="stitch-logo-text">KodoAI</span>
          <span className="stitch-beta-pill">BETA</span>
        </div>
        <div className="stitch-nav-right">
          <button className="stitch-btn-text" onClick={() => navigate('/login')}>Login</button>
          <button className="stitch-btn-primary" onClick={() => navigate('/login')}>Try now</button>
        </div>
      </header>

      <main className="stitch-main">
        {/* Hero Section */}
        <section className="stitch-hero">
          <h1 className="stitch-headline">Productivity at the speed of AI</h1>
          <p className="stitch-subheadline">
            Transform chaos into clear execution plans, intelligent schedules, and focused workflows.
          </p>

          {/* Prompt Card */}
          <div className="stitch-prompt-card">
            <textarea 
              className="stitch-prompt-input" 
              placeholder={isGenerating ? "Analyzing project requirements..." : "What project shall we organize today?"}
              rows={2}
              value={promptValue}
              onChange={(e) => setPromptValue(e.target.value)}
              disabled={isGenerating}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  if (promptValue.trim()) {
                    setIsGenerating(true);
                    setTimeout(() => navigate(`/login?intent=${encodeURIComponent(promptValue)}`), 1200);
                  }
                }
              }}
            ></textarea>
            <div className="stitch-prompt-controls">
              <div className="controls-left">
                <button className="icon-btn">➕</button>
                <div className="toggle-pill">
                  <button 
                    className={`toggle-btn ${activeTab === 'task' ? 'active' : ''}`}
                    onClick={() => setActiveTab('task')}
                    disabled={isGenerating}
                  >
                    📋 Task
                  </button>
                  <button 
                    className={`toggle-btn ${activeTab === 'project' ? 'active' : ''}`}
                    onClick={() => setActiveTab('project')}
                    disabled={isGenerating}
                  >
                    🚀 Project
                  </button>
                </div>
              </div>
              <div className="controls-right">
                <div className="model-selector">✨ 3 Flash <span className="chevron">▼</span></div>
                <button className="icon-btn">🎤</button>
                <button 
                  className="stitch-btn-submit" 
                  disabled={isGenerating}
                  onClick={() => {
                    if (promptValue.trim()) {
                      setIsGenerating(true);
                      setTimeout(() => navigate(`/login?intent=${encodeURIComponent(promptValue)}`), 1200);
                    } else {
                      navigate('/login');
                    }
                  }}
                >
                  {isGenerating ? '⏳' : '↑'}
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Examples Section */}
        <section className="stitch-examples">
          <div className="example-pills">
            <span className="example-pill">✈️ A trip packing checklist for Japan...</span>
            <span className="example-pill">📈 Q3 Marketing Campaign launch plan...</span>
            <span className="example-pill">💻 Profile page redesign sprint...</span>
          </div>
          
          <div className="stitch-showcase">
            <div className="showcase-content">
              <div className="mockup-image-container">
                <img src="/images/dashboard_ui.png" alt="KodoAI Dashboard UI Mockup" className="ui-mockup-img main-dashboard-img" />
              </div>
            </div>
            <button className="play-intro-btn">▶ Play intro</button>
          </div>
        </section>

        {/* Templates Section Removed */}

        {/* Features Grid */}
        <section className="stitch-features-grid">
          <div className="feature-box">
            <div className="feature-visual ui-overlap">
              <div className="mock-calendar">
                <div className="mock-cal-header">🗓️ Schedule</div>
                <div className="mock-cal-grid">
                  <div className="mock-cal-block b1"></div>
                  <div className="mock-cal-block b2 dragging"></div>
                  <div className="mock-cal-block b3"></div>
                </div>
              </div>
            </div>
            <div className="feature-text">
              <h3>Easy scheduling</h3>
              <p>Drag and drop tasks instantly. The AI auto-schedules based on your calendar availability and focus energy.</p>
            </div>
          </div>
          <div className="feature-box">
            <div className="feature-visual code-export">
              <div className="sync-animation">
                <span className="sync-icon brand">🎯</span>
                <div className="sync-arrows">
                  <span className="arrow-left">←</span>
                  <span className="arrow-right">→</span>
                </div>
                <span className="sync-icon calendar">📅</span>
              </div>
            </div>
            <div className="feature-text">
              <h3>Calendar Sync</h3>
              <p>Bi-directional sync with Google Calendar ensures your plans exist in the real world.</p>
            </div>
          </div>
          <div className="feature-box">
            <div className="feature-visual gemini-logo">
              <div className="gemini-star-container">
                <div className="gemini-star">✨</div>
                <div className="ai-chat-bubble b1">Organizing backlog...</div>
                <div className="ai-chat-bubble b2">Schedule optimized!</div>
              </div>
            </div>
            <div className="feature-text">
              <h3>Build with Gemini</h3>
              <p>Powered by Google DeepMind's most capable models to actively think through your backlog.</p>
            </div>
          </div>
          <div className="feature-box">
            <div className="feature-visual ownership">
              <div className="shield-container">
                <span className="shield-icon">🛡️</span>
                <div className="shield-ring"></div>
              </div>
            </div>
            <div className="feature-text">
              <h3>Own your productivity</h3>
              <p>Full control over your agents. Export your data, tweak your schedules, and adapt the AI to your workflow.</p>
            </div>
          </div>
        </section>

        {/* Secondary CTA */}
        <section className="stitch-cta-section">
          <h2 className="cta-headline">Flow state is here</h2>
          <p className="cta-subtext">Stop managing your tasks. Let intelligent agents manage them for you.</p>
          <button className="stitch-btn-primary large" onClick={() => navigate('/login')}>Start organizing</button>
        </section>

        {/* FAQ Section */}
        <section className="stitch-faq">
          <h2>Questions?</h2>
          <div className="faq-list">
            {[
              { q: 'What is KodoAI?', a: 'KodoAI is an intelligent productivity orchestrator that uses LangGraph agents to autonomously manage your backlog, plan your days, and sync seamlessly with your calendar.' },
              { q: 'Is KodoAI free of charge?', a: 'During our beta phase, core AI features are completely free to use.' },
              { q: 'Where is KodoAI available?', a: 'It is available globally as a web application.' },
              { q: 'Does it sync with Google Calendar?', a: 'Yes! KodoAI features full bi-directional syncing so your tasks show up perfectly scheduled on your actual calendar.' }
            ].map((item, i) => (
              <div key={i} className={`faq-item ${faqOpen === i ? 'open' : ''}`} onClick={() => toggleFaq(i)}>
                <div className="faq-header">
                  <span>{item.q}</span>
                  <span className="faq-icon">{faqOpen === i ? '✕' : '＋'}</span>
                </div>
                {faqOpen === i && <div className="faq-body">{item.a}</div>}
              </div>
            ))}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="stitch-footer">
        <div className="footer-left">
          <span className="footer-logo">🧪 KodoAI Labs</span>
        </div>
        <div className="footer-right">
          <a href="#">Privacy Notice</a>
          <a href="#">Terms & Privacy</a>
          <a href="#">Third Party Notices</a>
        </div>
      </footer>
    </div>
  );
}

export default Home;
