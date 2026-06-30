import React, { useState, useRef, useEffect } from 'react';
import { GripVertical, Trash2, Edit2, Check, X, Clock, PlayCircle, StopCircle } from 'lucide-react';
import api from '../services/api';
import './AddTaskBar.css';

function AddTaskBar({ defaultDate, channels, onTaskAdded }) {
  const [isOpen, setIsOpen] = useState(false);
  const [title, setTitle] = useState('');
  
  // Selections
  const [plannedDate, setPlannedDate] = useState(defaultDate);
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [priority, setPriority] = useState('none'); // urgent, high, medium, low, none
  const [channelId, setChannelId] = useState(channels.length > 0 ? channels[0].id : null);
  const [reminderHoursBefore, setReminderHoursBefore] = useState(null);
  
  // Sync channelId when channels are loaded asynchronously
  useEffect(() => {
    if (!channelId && channels.length > 0) {
      setChannelId(channels[0].id);
    }
  }, [channels, channelId]);
  
  // Popovers
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showPriorityPicker, setShowPriorityPicker] = useState(false);
  const [showChannelPicker, setShowChannelPicker] = useState(false);
  const [showReminderPicker, setShowReminderPicker] = useState(false);
  const [showManageChannels, setShowManageChannels] = useState(false);
  const [channelSearch, setChannelSearch] = useState('');

  const containerRef = useRef(null);

  // Close on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
        setShowDatePicker(false);
        setShowPriorityPicker(false);
        setShowChannelPicker(false);
        setShowReminderPicker(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = async () => {
    if (!title.trim()) return;
    try {
      await api.post('/api/tasks', {
        title: title.trim(),
        planned_date: plannedDate,
        start_time: startTime || null,
        end_time: endTime || null,
        priority,
        channel_id: channelId,
        reminder_hours_before: reminderHoursBefore
      });
      setTitle('');
      setStartTime('');
      setEndTime('');
      setIsOpen(false);
      if (onTaskAdded) onTaskAdded();
    } catch (err) {
      console.error("Failed to add task", err);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  };

  const todayStr = new Date().toISOString().split('T')[0];

  const getPriorityIcon = (prio) => {
    switch(prio) {
      case 'urgent': return '❗';
      case 'high': return '🔴';
      case 'medium': return '🟡';
      case 'low': return '🔵';
      default: return '⚪';
    }
  };

  const getPriorityLabel = (prio) => {
    if (prio === 'none') return 'No priority';
    return prio.charAt(0).toUpperCase() + prio.slice(1);
  };

  const getChannelName = (id) => {
    const c = channels.find(x => x.id === parseInt(id));
    return c ? c.name : 'Unassigned';
  };

  if (!isOpen) {
    return (
      <button className="add-task-trigger" onClick={() => setIsOpen(true)}>
        + Add task
      </button>
    );
  }

  return (
    <div className="add-task-bar active" ref={containerRef}>
      <input 
        autoFocus
        type="text" 
        className="add-task-input" 
        placeholder="Task name" 
        value={title}
        onChange={e => setTitle(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      
      <div className="add-task-toolbar">
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', background: 'var(--color-surface)', padding: '2px 8px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <PlayCircle size={14} style={{ color: 'var(--color-text-muted)' }} />
            <input 
              type="time" 
              value={startTime} 
              onChange={e => setStartTime(e.target.value)} 
              className="time-input" 
              title="Start Time"
              style={{ background: 'transparent', border: 'none', color: 'var(--color-text)', fontSize: '13px', outline: 'none' }}
            />
          </div>
          <span style={{ color: 'var(--color-border)' }}>|</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <StopCircle size={14} style={{ color: 'var(--color-text-muted)' }} />
            <input 
              type="time" 
              value={endTime} 
              onChange={e => setEndTime(e.target.value)} 
              className="time-input" 
              title="End Time"
              style={{ background: 'transparent', border: 'none', color: 'var(--color-text)', fontSize: '13px', outline: 'none' }}
            />
          </div>
        </div>
        
        <div className="toolbar-actions">
          {/* Add Button */}
          <button className="btn btn-primary" style={{ padding: '4px 12px', fontSize: '12px' }} onClick={handleSubmit}>Add</button>
          {/* Date Picker */}
          <div className="toolbar-item">
            <button onClick={() => {setShowDatePicker(!showDatePicker); setShowPriorityPicker(false); setShowChannelPicker(false);}}>
              📅 {plannedDate === todayStr ? 'Today' : plannedDate || 'Someday'}
            </button>
            {showDatePicker && (
              <div className="popover date-popover">
                <div className="popover-shortcuts">
                  <div onClick={() => {setPlannedDate(todayStr); setShowDatePicker(false);}}>📅 Today</div>
                  <div onClick={() => {
                    const d = new Date(); d.setDate(d.getDate() + 7);
                    setPlannedDate(d.toISOString().split('T')[0]); setShowDatePicker(false);
                  }}>📆 In the next week</div>
                  <div onClick={() => {setPlannedDate(null); setShowDatePicker(false);}}>⏳ Someday</div>
                </div>
                <div className="popover-divider"></div>
                <div className="popover-calendar">
                  <label>Schedule exact date</label>
                  <input 
                    type="date" 
                    min={todayStr}
                    value={plannedDate || ''}
                    onChange={(e) => {
                      setPlannedDate(e.target.value);
                      setShowDatePicker(false);
                    }}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Channel Picker with create option */}
          <div className="toolbar-item">
            <button onClick={() => {setShowChannelPicker(!showChannelPicker); setShowPriorityPicker(false); setShowDatePicker(false);}}>
              # {channelId ? getChannelName(channelId) : 'Unassigned'}
            </button>
            {showChannelPicker && (
              <div className="popover channel-popover" style={{ padding: '8px', minWidth: '180px' }}>
                <div style={{ fontSize: '11px', color: '#888', marginBottom: '8px' }}>Assign to channel:</div>
                <input 
                  type="text" 
                  autoFocus
                  placeholder="Search..." 
                  value={channelSearch}
                  onChange={e => setChannelSearch(e.target.value)}
                  style={{ width: '100%', marginBottom: '8px', background: 'transparent', border: 'none', borderBottom: '1px solid #444', color: '#fff', outline: 'none' }}
                />
                <div className="popover-item" onClick={() => {setChannelId(null); setShowChannelPicker(false);}}>
                  # Unassigned {channelId === null && '✓'}
                </div>
                {channels.filter(c => c.name.toLowerCase().includes(channelSearch.toLowerCase())).map(c => (
                  <div key={c.id} className="popover-item" onClick={() => {setChannelId(c.id); setShowChannelPicker(false);}}>
                    <span style={{ color: c.color || '#10B981', marginRight: '4px' }}>#</span> {c.name} {channelId === c.id && '✓'}
                  </div>
                ))}
                {channelSearch && !channels.find(c => c.name.toLowerCase() === channelSearch.toLowerCase()) && (
                  <div className="popover-item" style={{ color: '#10B981' }} onClick={async () => {
                    try {
                      const res = await api.post('/api/channels', { name: channelSearch.toLowerCase(), color: '#10B981' });
                      setChannelId(res.data?.id || res.id);
                      setShowChannelPicker(false);
                      setChannelSearch('');
                      if (onTaskAdded) onTaskAdded(); // refresh channels list from parent
                    } catch (e) {
                      console.error("Failed to create channel", e);
                    }
                  }}>
                    + Create "{channelSearch.toLowerCase()}"
                  </div>
                )}
                <div className="popover-divider"></div>
                <div className="popover-item" style={{ color: '#3b82f6', fontSize: '11px', cursor: 'pointer' }} onClick={() => {setShowManageChannels(true); setShowChannelPicker(false);}}>
                  Manage channels
                </div>
              </div>
            )}
          </div>

          {/* Priority Picker */}
          <div className="toolbar-item">
            <button onClick={() => {setShowPriorityPicker(!showPriorityPicker); setShowDatePicker(false); setShowChannelPicker(false); setShowReminderPicker(false);}}>
              {getPriorityIcon(priority)}
            </button>
            {showPriorityPicker && (
              <div className="popover priority-popover">
                <div className="popover-header">Set priority</div>
                <div className="popover-item" onClick={() => {setPriority('urgent'); setShowPriorityPicker(false);}}>❗ Urgent</div>
                <div className="popover-item" onClick={() => {setPriority('high'); setShowPriorityPicker(false);}}>🔴 High</div>
                <div className="popover-item" onClick={() => {setPriority('medium'); setShowPriorityPicker(false);}}>🟡 Medium</div>
                <div className="popover-item" onClick={() => {setPriority('low'); setShowPriorityPicker(false);}}>🔵 Low</div>
                <div className="popover-item" onClick={() => {setPriority('none'); setShowPriorityPicker(false);}}>⚪ No priority {priority === 'none' && '✓'}</div>
              </div>
            )}
          </div>

          {/* Reminder Picker */}
          <div className="toolbar-item">
            <button onClick={() => {setShowReminderPicker(!showReminderPicker); setShowPriorityPicker(false); setShowDatePicker(false); setShowChannelPicker(false);}}>
              🔔 {reminderHoursBefore ? `${reminderHoursBefore}hr before` : 'No reminder'}
            </button>
            {showReminderPicker && (
              <div className="popover priority-popover">
                <div className="popover-header">Remind me before start time</div>
                <div className="popover-item" onClick={() => {setReminderHoursBefore(1); setShowReminderPicker(false);}}>1 hour before {reminderHoursBefore === 1 && '✓'}</div>
                <div className="popover-item" onClick={() => {setReminderHoursBefore(2); setShowReminderPicker(false);}}>2 hours before {reminderHoursBefore === 2 && '✓'}</div>
                <div className="popover-item" onClick={() => {setReminderHoursBefore(3); setShowReminderPicker(false);}}>3 hours before {reminderHoursBefore === 3 && '✓'}</div>
                <div className="popover-item" onClick={() => {setReminderHoursBefore(null); setShowReminderPicker(false);}}>None {reminderHoursBefore === null && '✓'}</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {showManageChannels && (
        <ManageChannelsModal 
          channels={channels} 
          onClose={() => setShowManageChannels(false)} 
          onUpdated={onTaskAdded}
        />
      )}
    </div>
  );
}

function ManageChannelsModal({ channels, onClose, onUpdated }) {
  const [localChannels, setLocalChannels] = useState([...channels]);
  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName] = useState('');
  const [editColor, setEditColor] = useState('');
  const [draggedIdx, setDraggedIdx] = useState(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);

  useEffect(() => {
    setLocalChannels([...channels]);
  }, [channels]);

  const handleDragStart = (e, index) => {
    setDraggedIdx(index);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e, index) => {
    e.preventDefault();
    if (draggedIdx === null || draggedIdx === index) return;
    
    const newChannels = [...localChannels];
    const draggedItem = newChannels[draggedIdx];
    
    newChannels.splice(draggedIdx, 1);
    newChannels.splice(index, 0, draggedItem);
    
    setDraggedIdx(index);
    setLocalChannels(newChannels);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setDraggedIdx(null);
    try {
      const channelIds = localChannels.map(c => c.id);
      await api.patch('/api/channels/reorder', { channel_ids: channelIds });
      if (onUpdated) onUpdated();
    } catch (err) {
      console.error("Failed to reorder", err);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/api/channels/${id}`);
      setDeleteConfirmId(null);
      if (onUpdated) onUpdated();
    } catch (err) {
      console.error(err);
    }
  };

  const startEdit = (c) => {
    setEditingId(c.id);
    setEditName(c.name);
    setEditColor(c.color || '#10B981');
  };

  const saveEdit = async (id) => {
    try {
      await api.put(`/api/channels/${id}`, { name: editName, color: editColor });
      setEditingId(null);
      if (onUpdated) onUpdated();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="task-modal-overlay" onClick={(e) => { if (e.target.className === 'task-modal-overlay') onClose(); }}>
      <div className="task-modal-content" style={{ width: '400px', position: 'relative' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ margin: 0, fontSize: '16px' }}>Manage Channels</h3>
          <button className="icon-btn" onClick={onClose}><X size={18} /></button>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {localChannels.map((c, index) => (
            <div 
              key={c.id} 
              draggable={editingId !== c.id}
              onDragStart={(e) => handleDragStart(e, index)}
              onDragOver={(e) => handleDragOver(e, index)}
              onDrop={handleDrop}
              style={{
                display: 'flex', alignItems: 'center', gap: '8px', 
                padding: '8px', background: 'var(--color-surface)',
                borderRadius: '6px', border: '1px solid var(--color-border)',
                opacity: draggedIdx === index ? 0.5 : 1
              }}
            >
              <div style={{ cursor: editingId === c.id ? 'default' : 'grab', color: 'var(--color-text-muted)', display: 'flex' }}>
                <GripVertical size={16} />
              </div>
              
              {editingId === c.id ? (
                <div style={{ display: 'flex', gap: '8px', flex: 1, alignItems: 'center' }}>
                  <input type="color" value={editColor} onChange={e => setEditColor(e.target.value)} style={{ width: '24px', height: '24px', padding: 0, border: 'none', background: 'none' }} />
                  <input type="text" value={editName} onChange={e => setEditName(e.target.value)} autoFocus style={{ flex: 1, background: 'var(--color-bg)', border: '1px solid var(--color-border)', color: '#fff', padding: '4px 8px', borderRadius: '4px' }} />
                  <button className="icon-btn" onClick={() => saveEdit(c.id)} style={{ color: '#10B981' }}><Check size={16} /></button>
                  <button className="icon-btn" onClick={() => setEditingId(null)} style={{ color: '#ef4444' }}><X size={16} /></button>
                </div>
              ) : (
                <div style={{ display: 'flex', gap: '8px', flex: 1, alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: c.color || '#10B981' }}></div>
                    <span>{c.name}</span>
                  </div>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    <button className="icon-btn" onClick={() => startEdit(c)}><Edit2 size={14} /></button>
                    <button className="icon-btn" onClick={() => setDeleteConfirmId(c.id)} style={{ color: '#ef4444' }}><Trash2 size={14} /></button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {deleteConfirmId && (
          <div style={{
            position: 'absolute', top: 0, left: 0, width: '100%', height: '100%',
            background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center',
            borderRadius: '12px', zIndex: 10
          }}>
            <div style={{ background: 'var(--color-surface)', padding: '24px', borderRadius: '8px', border: '1px solid var(--color-border)', width: '80%', textAlign: 'center' }}>
              <h4 style={{ marginTop: 0, marginBottom: '16px' }}>Delete Channel?</h4>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '14px', marginBottom: '24px' }}>Are you sure you want to delete this channel? Tasks in this channel will be orphaned.</p>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                <button className="btn btn-secondary" onClick={() => setDeleteConfirmId(null)}>Cancel</button>
                <button className="btn btn-primary" style={{ background: '#ef4444', borderColor: '#ef4444' }} onClick={() => handleDelete(deleteConfirmId)}>Delete</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AddTaskBar;
