import { useState, useEffect } from 'react';
import { getFullReport } from '../services/api';
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement, LineElement,
  PointElement, ArcElement, Title, Tooltip, Legend, Filler,
} from 'chart.js';
import { Bar, Line, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale, LinearScale, BarElement, LineElement,
  PointElement, ArcElement, Title, Tooltip, Legend, Filler,
);

const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { labels: { color: '#94a3b8', font: { size: 12 } } } },
  scales: {
    x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.05)' } },
    y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.05)' } },
  },
};

function StatChip({ icon, label, value }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <h3>{label}</h3>
      <div className="stat-value">{value ?? '—'}</div>
    </div>
  );
}

function Analytics() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await getFullReport();
        setReport(data);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return (
      <div className="tab-content">
        <header className="top-header"><h2>Analytics</h2></header>
        <div className="skeleton-list">{[1,2,3].map(i => <div key={i} className="skeleton-item tall" />)}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="tab-content">
        <header className="top-header"><h2>Analytics</h2></header>
        <div className="error-banner">⚠️ {error}</div>
      </div>
    );
  }

  const { daily, weekly, monthly } = report;

  // ── Chart data ──────────────────────────────────────────────────
  const hourlyData = {
    labels: daily.hourly_breakdown.labels.filter((_, i) => daily.hourly_breakdown.data[i] > 0 || (i >= 6 && i <= 22)).slice(0, 17),
    datasets: [{
      label: 'Focus Minutes',
      data: daily.hourly_breakdown.data.filter((_, i) => daily.hourly_breakdown.labels[i] && i >= 6 && i <= 22),
      backgroundColor: 'rgba(99,102,241,0.7)',
      borderRadius: 6,
    }],
  };

  const weeklyData = {
    labels: weekly.labels,
    datasets: [
      {
        label: 'Focus Hours',
        data: weekly.focus_hours,
        borderColor: '#6366f1',
        backgroundColor: 'rgba(99,102,241,0.15)',
        fill: true,
        tension: 0.4,
        yAxisID: 'y',
      },
      {
        label: 'Pomodoros',
        data: weekly.pomodoros,
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245,158,11,0.15)',
        fill: true,
        tension: 0.4,
        yAxisID: 'y1',
      },
    ],
  };

  const weeklyOptions = {
    ...chartDefaults,
    scales: {
      ...chartDefaults.scales,
      y:  { ...chartDefaults.scales.y, position: 'left',  title: { display: true, text: 'Hours', color: '#64748b' } },
      y1: { ...chartDefaults.scales.y, position: 'right', title: { display: true, text: 'Pomodoros', color: '#64748b' }, grid: { drawOnChartArea: false } },
    },
  };

  const distColors = ['#6366f1','#8b5cf6','#f59e0b','#10b981','#ef4444','#06b6d4'];
  const doughnutData = monthly.project_distribution.length > 0 ? {
    labels: monthly.project_distribution.map(d => d.type),
    datasets: [{
      data: monthly.project_distribution.map(d => d.percentage),
      backgroundColor: distColors,
      borderColor: '#0f172a',
      borderWidth: 2,
    }],
  } : null;

  return (
    <div className="tab-content">
      <header className="top-header">
        <h2>Analytics</h2>
        <span className="muted">Last 30 days · Live from Supabase</span>
      </header>

      {/* Summary stats */}
      <div className="stats-grid">
        <StatChip icon="🕐" label="Focus Today"     value={`${daily.total_hours}h`} />
        <StatChip icon="🍅" label="Pomodoros Today" value={daily.pomodoros_completed} />
        <StatChip icon="📋" label="Tasks Done Today" value={daily.tasks_completed} />
        <StatChip icon="🔥" label="Current Streak"  value={`${daily.streak}d`} />
        <StatChip icon="📅" label="This Week"        value={`${Math.round(weekly.total_this_week / 60 * 10) / 10}h`} />
        <StatChip icon="🏆" label="Monthly Focus"   value={`${monthly.total_focus_hours}h`} />
        <StatChip icon="✅" label="Monthly Completions" value={monthly.commitments_completed} />
        <StatChip icon="⏱" label="Avg Daily"        value={`${weekly.avg_daily_minutes}m`} />
      </div>

      {/* Charts */}
      <div className="charts-grid">
        {/* Daily hourly breakdown */}
        <div className="chart-card">
          <h3>⏰ Today's Focus by Hour</h3>
          <div className="chart-wrap" style={{ height: 200 }}>
            <Bar
              data={hourlyData}
              options={{ ...chartDefaults, plugins: { ...chartDefaults.plugins, legend: { display: false } } }}
            />
          </div>
        </div>

        {/* Weekly trends */}
        <div className="chart-card">
          <h3>📈 Weekly Focus Trend</h3>
          <div className="chart-wrap" style={{ height: 200 }}>
            <Line data={weeklyData} options={weeklyOptions} />
          </div>
        </div>

        {/* Monthly distribution */}
        <div className="chart-card">
          <h3>🥧 Commitment Types (30d)</h3>
          <div className="chart-wrap" style={{ height: 200 }}>
            {doughnutData ? (
              <Doughnut
                data={doughnutData}
                options={{ ...chartDefaults, scales: undefined, plugins: { legend: { position: 'right', labels: { color: '#94a3b8' } } } }}
              />
            ) : (
              <div className="empty-state"><span>📭</span><p>Complete some commitments to see distribution.</p></div>
            )}
          </div>
        </div>

        {/* Weekly focus hours bar */}
        <div className="chart-card">
          <h3>📊 Daily Focus Hours (This Week)</h3>
          <div className="chart-wrap" style={{ height: 200 }}>
            <Bar
              data={{
                labels: weekly.labels,
                datasets: [{
                  label: 'Hours',
                  data: weekly.focus_hours,
                  backgroundColor: weekly.focus_hours.map(h => h > 0 ? 'rgba(99,102,241,0.8)' : 'rgba(99,102,241,0.2)'),
                  borderRadius: 6,
                }],
              }}
              options={{ ...chartDefaults, plugins: { ...chartDefaults.plugins, legend: { display: false } } }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Analytics;
