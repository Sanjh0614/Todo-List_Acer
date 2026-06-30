import { useState } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { useStats } from '../context/StatsContext';
import AgentChat from '../pages/AgentChat';


function Layout({ user, onLogout }) {
  const { todayStats } = useStats();
  const location = useLocation();
  const [showAiAgent, setShowAiAgent] = useState(false);

  const [isSidebarExpanded, setIsSidebarExpanded] = useState(false);

  return (
    <div className="page" id="app-page">
      <nav className={`sidebar ${isSidebarExpanded ? '' : 'collapsed'}`}>
        <div className="sidebar-header">
          <button 
            className="hamburger-btn" 
            onClick={() => setIsSidebarExpanded(!isSidebarExpanded)}
            title={isSidebarExpanded ? "Collapse menu" : "Expand menu"}
          >
            ☰
          </button>
        </div>

        <div className="user-profile">
          <img src={user?.avatar_url || "https://ui-avatars.com/api/?name=" + (user?.name || 'U')} alt="Avatar" className="avatar" />
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
            <span className="nav-text" style={{ display: 'block' }}>{user?.name || 'User'}</span>
            {!user?.google_id && (
              <a 
                href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/auth/google/login?token=${localStorage.getItem('auth_token')}`}
                className="nav-text"
                style={{ fontSize: '10px', color: 'var(--color-primary)', textDecoration: 'none', marginTop: '2px', fontWeight: 600, display: 'block' }}
                title="Connect Google Calendar for 2-way sync"
              >
                + Connect Calendar
              </a>
            )}
          </div>
        </div>
        
        <ul className="nav-links">
          <li>
            <NavLink to="/dashboard" className={({isActive}) => isActive ? 'active' : ''} title="Home">
              <span className="nav-icon" style={{ fontSize: '18px' }}>🏠</span>
              <span className="nav-text">Home</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/today" className={({isActive}) => isActive ? 'active' : ''} title="Today">
              <span className="nav-icon" style={{ fontSize: '18px' }}>📅</span>
              <span className="nav-text">Today</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/focus" className={({isActive}) => isActive ? 'active' : ''} title="Focus">
              <span className="nav-icon" style={{ fontSize: '18px' }}>⏱️</span>
              <span className="nav-text">Focus</span>
            </NavLink>
          </li>
        </ul>

        <div className="sidebar-section">
          <div className="section-title">DAILY RITUALS</div>
          <ul className="nav-links">
            <li>
              <NavLink to="/today?tab=planning" className={() => location.pathname === '/today' && location.search.includes('tab=planning') ? 'active' : ''} title="Daily planning">
                <span className="nav-icon" style={{ fontSize: '18px' }}>📝</span>
                <span className="nav-text">Daily planning</span>
              </NavLink>
            </li>
            <li>
              <NavLink to="/today?tab=highlights" className={() => (location.pathname === '/today' && location.search.includes('tab=highlights')) ? 'active' : ''} title="Daily highlights">
                <span className="nav-icon" style={{ fontSize: '18px' }}>✨</span>
                <span className="nav-text">Daily highlights</span>
              </NavLink>
            </li>
          </ul>
        </div>

        <div className="sidebar-section">
          <div className="section-title">WEEKLY RITUALS</div>
          <ul className="nav-links">
            <li>
              <NavLink to="/weekly-planning" className={({isActive}) => isActive ? 'active' : ''} title="Weekly planning">
                <span className="nav-icon" style={{ fontSize: '18px' }}>📅</span>
                <span className="nav-text">Weekly planning</span>
              </NavLink>
            </li>
            <li>
              <NavLink to="/weekly-review" className={({isActive}) => isActive ? 'active' : ''} title="Weekly review">
                <span className="nav-icon" style={{ fontSize: '18px' }}>🔍</span>
                <span className="nav-text">Weekly review</span>
              </NavLink>
            </li>
          </ul>
        </div>

        <ul className="nav-links" style={{ marginTop: '24px' }}>
          <li>
            <NavLink to="/commitments" className={({isActive}) => isActive ? 'active' : ''} title="Backlog">
              <span className="nav-icon" style={{ fontSize: '18px' }}>📋</span>
              <span className="nav-text">Backlog</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/analytics" className={({isActive}) => isActive ? 'active' : ''} title="Analytics">
              <span className="nav-icon" style={{ fontSize: '18px' }}>📊</span>
              <span className="nav-text">Analytics</span>
            </NavLink>
          </li>
        </ul>

        <button onClick={onLogout} className="btn btn-ghost mt-auto" style={{marginTop: 'auto', display: 'flex', alignItems: 'center', gap: '12px'}} title="Logout">
          <span className="nav-icon" style={{ fontSize: '18px' }}>🚪</span>
          <span className="nav-text">Logout</span>
        </button>
      </nav>
      <main className="main-content" style={{ display: 'flex', flexDirection: 'column' }}>
        {todayStats && (
          <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '16px', fontSize: '0.875rem', padding: '12px 24px', background: 'var(--color-surface-1)', borderBottom: '1px solid var(--color-surface-2)' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><span>🕐</span> {todayStats.total_hours}h today</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><span>🍅</span> {todayStats.pomodoros_completed} pomodoros</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', marginRight: '8px' }}><span>🔥</span> {todayStats.streak_days}d streak</span>
            
            <button 
              className="btn btn-ghost ai-topbar-toggle"
              onClick={() => setShowAiAgent(p => !p)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: showAiAgent ? 'rgba(99, 102, 241, 0.15)' : 'rgba(255,255,255,0.03)',
                border: showAiAgent ? '1px solid rgba(99, 102, 241, 0.3)' : '1px solid rgba(255,255,255,0.08)',
                color: showAiAgent ? '#8B5CF6' : 'var(--color-text-muted)',
                borderRadius: '8px',
                padding: '6px 12px',
                fontSize: '16px',
                transition: 'all 0.2s ease',
                cursor: 'pointer',
                boxShadow: showAiAgent ? '0 0 10px rgba(99, 102, 241, 0.2)' : 'none'
              }}
              title="Open AI Assistant"
            >
              ✨ {showAiAgent ? 'Close AI' : 'Ask AI'}
            </button>
          </div>
        )}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
          <Outlet />
        </div>
      </main>
      
      {/* ── Slide-out AI Agent Panel ── */}
      <div className={`ai-agent-panel ${showAiAgent ? 'open' : ''}`}>
        <button className="close-ai-btn" onClick={() => setShowAiAgent(false)}>✕</button>
        <AgentChat />
      </div>
    </div>
  );
}

export default Layout;
