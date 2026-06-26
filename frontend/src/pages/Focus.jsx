import { useState, useEffect, useRef, useCallback } from 'react';
import { startSession, stopSession, getActiveSession, getRecommendation, getTodayStats, getFocusTasks } from '../services/api';

const MODES = {
  pomodoro:  { label: '🍅 Pomodoro',  minutes: 25, icon: '🍅' },
  deepwork:  { label: '🧠 Deep Work', minutes: 90, icon: '🧠' },
  break:     { label: '☕ Break',      minutes: 5,  icon: '☕', isBreak: true },
  longbreak: { label: '🛋 Long Break', minutes: 20, icon: '🛋', isBreak: true },
};

function pad(n) { return String(n).padStart(2, '0'); }

function Focus() {
  const [mode, setMode]             = useState('pomodoro');
  const [timeLeft, setTimeLeft]     = useState(MODES.pomodoro.minutes * 60);
  const [running, setRunning]       = useState(false);
  const [sessionId, setSessionId]   = useState(null);
  const [pomNumber, setPomNumber]   = useState(1);

  const [tasks, setTasks]           = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [todayStats, setTodayStats] = useState(null);

  const [statusMsg, setStatusMsg]   = useState('');
  const [loading, setLoading]       = useState(false);

  const timerRef = useRef(null);
  const startedAtRef = useRef(null);

  // ── Load initial data ─────────────────────────────────────────────
  const loadData = useCallback(async () => {
    try {
      const [t, rec, stats] = await Promise.all([getFocusTasks(), getRecommendation(), getTodayStats()]);
      setTasks(t);
      setRecommendation(rec.recommendation);
      setTodayStats(stats);
    } catch (e) { console.error('Focus load error:', e); }
  }, []);

  // ── Check for active session on mount ────────────────────────────
  useEffect(() => {
    const init = async () => {
      await loadData();
      try {
        const { session } = await getActiveSession();
        if (session) {
          setSessionId(session.id);
          setRunning(true);
          setMode(session.mode || 'pomodoro');
          const elapsed = Math.floor((Date.now() - new Date(session.started_at).getTime()) / 1000);
          const planned = (session.planned_duration_minutes || MODES[session.mode]?.minutes || 25) * 60;
          setTimeLeft(Math.max(0, planned - elapsed));
          startedAtRef.current = new Date(session.started_at);
          setStatusMsg('Resuming active session…');
        }
      } catch (e) { /* no active session */ }
    };
    init();
  }, [loadData]);

  // ── Countdown tick ────────────────────────────────────────────────
  useEffect(() => {
    if (running) {
      timerRef.current = setInterval(() => {
        setTimeLeft(t => {
          if (t <= 1) {
            clearInterval(timerRef.current);
            setRunning(false);
            setStatusMsg('⏰ Session complete! Great work.');
            return 0;
          }
          return t - 1;
        });
      }, 1000);
    } else {
      clearInterval(timerRef.current);
    }
    return () => clearInterval(timerRef.current);
  }, [running]);

  // ── Change mode resets timer ──────────────────────────────────────
  const switchMode = (m) => {
    if (running) return; // don't switch mid-session
    setMode(m);
    setTimeLeft(MODES[m].minutes * 60);
    setStatusMsg('');
  };

  // ── Start ─────────────────────────────────────────────────────────
  const handleStart = async () => {
    setLoading(true);
    try {
      const cfg = MODES[mode];
      const sess = await startSession({
        mode,
        task_id: selectedTask?.id ?? null,
        planned_duration_minutes: cfg.minutes,
        pomodoro_number: pomNumber,
        is_break: cfg.isBreak ?? false,
      });
      setSessionId(sess.id);
      startedAtRef.current = new Date(sess.started_at);
      setRunning(true);
      setStatusMsg(`▶ ${cfg.label} started — saved to Supabase`);
    } catch (e) {
      setStatusMsg('⚠ ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  // ── Stop ──────────────────────────────────────────────────────────
  const handleStop = async (status = 'completed') => {
    if (!sessionId) { setRunning(false); return; }
    setLoading(true);
    try {
      const res = await stopSession({ session_id: sessionId, status, flow_rating: null });
      setRunning(false);
      setSessionId(null);
      setTimeLeft(MODES[mode].minutes * 60);
      if (status === 'completed') {
        setPomNumber(p => p + 1);
        setStatusMsg(`✅ Session saved! ${res.duration_minutes}m recorded in Supabase.`);
      } else {
        setStatusMsg('⏸ Session interrupted and saved.');
      }
      // Refresh stats
      const stats = await getTodayStats();
      setTodayStats(stats);
    } catch (e) {
      setStatusMsg('⚠ ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  const mins  = Math.floor(timeLeft / 60);
  const secs  = timeLeft % 60;
  const total = MODES[mode].minutes * 60;
  const pct   = ((total - timeLeft) / total) * 100;

  // ── Circular SVG timer ────────────────────────────────────────────
  const R = 110, C = 2 * Math.PI * R;

  return (
    <div className="tab-content">
      <header className="top-header">
        <h2>Focus</h2>
        {todayStats && (
          <div style={{ display: 'flex', gap: 16, fontSize: '0.875rem' }}>
            <span>🕐 {todayStats.total_hours}h today</span>
            <span>🍅 {todayStats.pomodoros_completed} pomodoros</span>
            <span>🔥 {todayStats.streak_days}d streak</span>
          </div>
        )}
      </header>

      <div className="focus-layout">
        {/* ── Left: Timer ─────────────────────────────────────────── */}
        <div className="timer-section">
          {/* Mode selector */}
          <div className="mode-selector">
            {Object.entries(MODES).map(([key, cfg]) => (
              <button
                key={key}
                className={`mode-btn ${mode === key ? 'active' : ''}`}
                onClick={() => switchMode(key)}
                disabled={running}
                title={running ? 'Stop current session to switch mode' : ''}
              >
                {cfg.icon} {cfg.label.split(' ').slice(1).join(' ')}
              </button>
            ))}
          </div>

          {/* SVG Circular Timer */}
          <div className="timer-display-container">
            <svg width="260" height="260" viewBox="0 0 260 260" className="timer-svg">
              <circle cx="130" cy="130" r={R} fill="none" stroke="var(--color-surface-2)" strokeWidth="12" />
              <circle
                cx="130" cy="130" r={R} fill="none"
                stroke={running ? 'var(--color-primary)' : 'var(--color-surface-3)'}
                strokeWidth="12"
                strokeDasharray={C}
                strokeDashoffset={C - (C * pct / 100)}
                strokeLinecap="round"
                transform="rotate(-90 130 130)"
                style={{ transition: 'stroke-dashoffset 1s linear' }}
              />
              <text x="130" y="118" textAnchor="middle" className="timer-mode-text">{MODES[mode].icon} {MODES[mode].label.split(' ').slice(1).join(' ')}</text>
              <text x="130" y="152" textAnchor="middle" className="timer-time-text">{pad(mins)}:{pad(secs)}</text>
              <text x="130" y="175" textAnchor="middle" className="timer-session-text">Session #{pomNumber}</text>
            </svg>
          </div>

          {/* Controls */}
          <div className="timer-controls">
            {!running ? (
              <button id="focus-start-btn" className="btn btn-primary btn-large" onClick={handleStart} disabled={loading}>
                {loading ? '…' : '▶ Start Session'}
              </button>
            ) : (
              <div style={{ display: 'flex', gap: 10 }}>
                <button className="btn btn-primary btn-large" onClick={() => handleStop('completed')} disabled={loading}>
                  ✅ Complete
                </button>
                <button className="btn btn-ghost btn-large" onClick={() => handleStop('interrupted')} disabled={loading}>
                  ⏸ Interrupt
                </button>
              </div>
            )}
          </div>

          {statusMsg && <div className="focus-status">{statusMsg}</div>}
        </div>

        {/* ── Right: Tasks + Recommendation ───────────────────────── */}
        <div className="focus-sidebar">
          {/* AI Recommendation */}
          {recommendation && (
            <div className="recommendation-card">
              <h4>🤖 AI Recommends</h4>
              <p className="rec-task">{recommendation.task_title}</p>
              <p className="muted rec-commitment">{recommendation.commitment_title}</p>
              <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                <span className="risk-badge risk-high" style={{ fontSize: '0.7rem' }}>
                  Priority {Math.round(recommendation.priority_score)}
                </span>
                <span className="muted" style={{ fontSize: '0.75rem' }}>
                  🍅 {recommendation.pomodoros_completed}/{recommendation.pomodoros_estimated}
                </span>
              </div>
              <button
                className="btn btn-ghost btn-sm"
                style={{ marginTop: 8 }}
                onClick={() => setSelectedTask({ id: recommendation.task_id, title: recommendation.task_title })}
                disabled={running}
              >
                Focus on this →
              </button>
            </div>
          )}

          {/* Task Picker */}
          <div className="task-picker">
            <h4>📋 Focus on Task</h4>
            {tasks.length === 0 ? (
              <p className="muted">No incomplete tasks. Add commitments first.</p>
            ) : (
              <ul className="task-pick-list">
                {tasks.map(t => (
                  <li
                    key={t.id}
                    className={`task-pick-item ${selectedTask?.id === t.id ? 'selected' : ''}`}
                    onClick={() => !running && setSelectedTask(t)}
                  >
                    <span className="task-pick-title">{t.title}</span>
                    <span className="muted task-pick-commitment">{t.commitment_title}</span>
                  </li>
                ))}
              </ul>
            )}
            {selectedTask && (
              <div className="selected-task-bar">
                Focusing on: <strong>{selectedTask.title}</strong>
                {!running && <button className="icon-btn" onClick={() => setSelectedTask(null)}>✕</button>}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Focus;
