import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function Backlog() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBacklog();
  }, []);

  const fetchBacklog = async () => {
    setLoading(true);
    try {
      // The backend now fully dynamically calculates overdue tasks and feeds them through 
      // the LangGraph recommendation pipeline, returning authentic data.
      const res = await api.get('/api/tasks/backlog'); 
      setTasks(Array.isArray(res) ? res : (res.data || []));
    } catch (e) {
      console.error("Failed to fetch backlog:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkDone = async (task) => {
    try {
      await api.patch('/api/tasks/' + task.id + '/done');
      fetchBacklog();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ padding: '24px', color: 'var(--text-main)', maxWidth: '800px', margin: '0 auto' }}>
      <h2 style={{ marginBottom: '8px' }}>Backlog</h2>
      <p style={{ color: 'var(--text-muted)', marginBottom: '32px' }}>Unfinished tasks from past days.</p>
      
      {loading ? (
        <div style={{ color: 'var(--text-muted)', fontStyle: 'italic', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="spinner" style={{ width: '16px', height: '16px', border: '2px solid var(--text-muted)', borderTopColor: 'var(--color-primary)', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></span>
          Loading backlog tasks & generating AI recommendations...
        </div>
      ) : tasks.length === 0 ? (
        <div style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>No backlog tasks! You are all caught up.</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {tasks.map(task => (
            <div key={task.id} style={{ display: 'flex', flexDirection: 'column', gap: '12px', background: 'var(--color-surface)', padding: '16px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
              
              {/* Task Header */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <button 
                  onClick={() => handleMarkDone(task)}
                  style={{ width: '22px', height: '22px', borderRadius: '50%', border: '2px solid var(--color-border)', background: 'transparent', cursor: 'pointer', flexShrink: 0 }}
                  title="Mark as Done"
                />
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '16px', fontWeight: '500' }}>{task.title}</div>
                  <div style={{ display: 'flex', gap: '12px', fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                    <span style={{ color: '#ef4444' }}>⚠️ Overdue since {new Date(task.planned_date).toLocaleDateString()}</span>
                    {task.priority && task.priority !== 'none' && <span>Priority: {task.priority}</span>}
                    {task.estimated_minutes > 0 && <span>{task.estimated_minutes} min</span>}
                  </div>
                </div>
              </div>

              {/* AI Recommendation Block */}
              {task.ai_recommendation && (
                <div style={{ marginTop: '8px', padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '6px', borderLeft: '3px solid var(--color-primary)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--color-primary)', fontWeight: '600', fontSize: '13px', marginBottom: '8px' }}>
                    ✨ AI Recommendation
                  </div>
                  <div style={{ fontSize: '14px', color: 'var(--text-main)', lineHeight: '1.5' }}>
                    {task.ai_recommendation}
                  </div>
                </div>
              )}

            </div>
          ))}
        </div>
      )}
      
      <style>{`
        @keyframes spin { 100% { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}