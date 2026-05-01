import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../utils/api'
import { useAuth } from '../context/AuthContext'
import ScoreBar from '../components/ScoreBar'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
const { user, isAdmin, loading: authLoading } = useAuth()

 useEffect(() => {
  if (!authLoading && user) {
    setLoading(true);

    api.get('/dashboard')
      .then(r => setData(r.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }
}, [authLoading, user]);

  if (loading) return <LoadingState />

  const { stats, evaluation, recent_evaluations } = data || {}

  return (
    <div className="animate-slide-up">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-100">
          Good {getGreeting()}, <span className="text-brand-500">{user?.name?.split(' ')[0]}</span>
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          {isAdmin ? 'Global overview of all projects and tasks' : 'Your project activity and evaluation scores'}
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
        <StatCard label="Total Tasks" value={stats?.total_tasks ?? 0} icon="📋" color="blue" />
        <StatCard label="Completed" value={stats?.completed_tasks ?? 0} icon="✅" color="green" />
        <StatCard
          label="Overdue"
          value={stats?.overdue_tasks ?? 0}
          icon="⚠️"
          color={stats?.overdue_tasks > 0 ? "red" : "gray"}
          onClick={() => navigate('/tasks?status=overdue')}
        />
        <StatCard label="Projects" value={stats?.total_projects ?? 0} icon="📁" color="purple" />
      </div>

      {/* Completion bar */}
      <div className="card mb-5">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-slate-300">Completion Rate</span>
          <span className="font-mono text-brand-500 text-sm font-bold">{stats?.completion_rate ?? 0}%</span>
        </div>
        <div className="h-2 bg-surface-3 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-brand-500 to-emerald-500 rounded-full transition-all duration-700"
            style={{ width: `${stats?.completion_rate ?? 0}%` }}
          />
        </div>
        <div className="flex gap-4 mt-3 text-xs text-slate-500">
          <span><span className="text-slate-400">{stats?.todo_tasks}</span> todo</span>
          <span><span className="text-amber-400">{stats?.in_progress_tasks}</span> in progress</span>
          <span><span className="text-emerald-400">{stats?.completed_tasks}</span> done</span>
        </div>
      </div>

      {/* Evaluation panel */}
      <div className="grid md:grid-cols-2 gap-4 mb-5">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-slate-200">Evaluation Scores</h2>
              <p className="text-xs text-slate-500 mt-0.5">RLHF-inspired task quality metrics</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold font-mono text-brand-500">
                {evaluation?.avg_composite_score ?? '—'}
              </div>
              <div className="text-[10px] text-slate-500 uppercase tracking-wider">avg composite</div>
            </div>
          </div>

          <div className="flex flex-col gap-3">
            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-slate-400">Accuracy Score</span>
                <span className="text-slate-300 font-mono">{evaluation?.avg_accuracy_score ?? '—'} / 5</span>
              </div>
              <ScoreBar value={evaluation?.avg_accuracy_score} max={5} color="brand" />
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-slate-400">Completeness Score</span>
                <span className="text-slate-300 font-mono">{evaluation?.avg_completeness_score ?? '—'} / 5</span>
              </div>
              <ScoreBar value={evaluation?.avg_completeness_score} max={5} color="emerald" />
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-surface-3 text-xs text-slate-500">
            <span className="text-slate-300 font-medium">{evaluation?.total_evaluated ?? 0}</span> tasks evaluated
          </div>
        </div>

        {/* Recent evaluations */}
        <div className="card">
          <h2 className="text-sm font-semibold text-slate-200 mb-3">Recent Evaluations</h2>
          {recent_evaluations?.length === 0 ? (
            <div className="text-center text-slate-500 text-sm py-6">No evaluations yet</div>
          ) : (
            <div className="flex flex-col gap-2">
              {recent_evaluations?.map(ev => (
                <div key={ev.id} className="flex items-center justify-between py-2 border-b border-surface-3 last:border-0">
                  <div className="min-w-0 flex-1">
                    <div className="text-xs text-slate-300 truncate">Task #{ev.task_id}</div>
                    <div className="text-[10px] text-slate-500">by {ev.evaluator_name}</div>
                  </div>
                  <div className="flex gap-2 ml-3">
                    <ScoreBadge label="A" value={ev.accuracy_score} />
                    <ScoreBadge label="C" value={ev.completeness_score} />
                    <div className="px-2 py-0.5 rounded bg-brand-500/15 text-brand-500 text-xs font-mono font-bold">
                      {ev.composite_score}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick actions */}
      <div className="flex gap-3">
        <button onClick={() => navigate('/projects')} className="btn-secondary flex-1 py-2.5 text-center">
          View Projects →
        </button>
        <button onClick={() => navigate('/tasks')} className="btn-secondary flex-1 py-2.5 text-center">
          View Tasks →
        </button>
      </div>
    </div>
  )
}

function StatCard({ label, value, icon, color, onClick }) {
  const colors = {
    blue: 'bg-blue-500/10 border-blue-500/20 text-blue-400',
    green: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400',
    red: 'bg-red-500/10 border-red-500/20 text-red-400',
    purple: 'bg-purple-500/10 border-purple-500/20 text-purple-400',
    gray: 'bg-surface-2 border-surface-3 text-slate-400',
  }
  return (
    <div
      className={`card ${colors[color]} cursor-pointer hover:scale-[1.02] transition-transform ${onClick ? 'cursor-pointer' : ''}`}
      onClick={onClick}
    >
      <div className="text-xl mb-1">{icon}</div>
      <div className="text-2xl font-bold font-mono">{value}</div>
      <div className="text-xs opacity-80 mt-0.5">{label}</div>
    </div>
  )
}

function ScoreBadge({ label, value }) {
  const color = value >= 4 ? 'text-emerald-400' : value >= 2.5 ? 'text-amber-400' : 'text-red-400'
  return (
    <div className="flex items-center gap-1 text-xs">
      <span className="text-slate-500">{label}:</span>
      <span className={`font-mono font-bold ${color}`}>{value}</span>
    </div>
  )
}

function LoadingState() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
    </div>
  )
}

function getGreeting() {
  const h = new Date().getHours()
  if (h < 12) return 'morning'
  if (h < 17) return 'afternoon'
  return 'evening'
}
