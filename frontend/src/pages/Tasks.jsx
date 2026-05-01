import { useEffect, useState } from 'react'
import api from '../utils/api'
import { useAuth } from '../context/AuthContext'
import TaskCard from '../components/TaskCard'
import Modal from '../components/Modal'

export default function Tasks() {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [showEval, setShowEval] = useState(null)
  const [evalForm, setEvalForm] = useState({ accuracy_score: 3, completeness_score: 3, comments: '' })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const { isAdmin } = useAuth()

  const load = () => {
    api.get('/tasks').then(r => setTasks(r.data.tasks)).catch(console.error).finally(() => setLoading(false))
  }
  useEffect(load, [])

  const handleStatusChange = async (taskId, status) => {
    await api.patch(`/tasks/${taskId}/status`, { status }); load()
  }
  const handleDelete = async (taskId) => {
    if (!confirm('Delete this task?')) return
    await api.delete(`/tasks/${taskId}`); load()
  }
  const openEval = (task) => {
    setShowEval(task)
    setEvalForm({ accuracy_score: task.evaluation?.accuracy_score ?? 3, completeness_score: task.evaluation?.completeness_score ?? 3, comments: task.evaluation?.comments ?? '' })
  }
  const handleEvaluate = async (e) => {
    e.preventDefault(); setSaving(true); setError('')
    try {
      await api.post(`/tasks/${showEval.id}/evaluate`, evalForm)
      setShowEval(null); load()
    } catch (err) { setError(err.response?.data?.error || 'Failed') }
    finally { setSaving(false) }
  }

  if (loading) return <div className="flex justify-center py-20"><div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"/></div>

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-6">All Tasks</h1>
      {tasks.length === 0 ? (
        <div className="text-center py-20 text-gray-500">No tasks found.</div>
      ) : (
        <div className="flex flex-col gap-3">
          {tasks.map(task => (
            <TaskCard key={task.id} task={task} isAdmin={isAdmin}
              onStatusChange={handleStatusChange} onDelete={handleDelete} onEvaluate={openEval} />
          ))}
        </div>
      )}

      <Modal open={!!showEval} onClose={() => setShowEval(null)} title="Evaluate Task" size="lg">
        {showEval && (
          <form onSubmit={handleEvaluate} className="flex flex-col gap-4">
            <div className="bg-gray-800 rounded-lg p-3 text-sm text-white">{showEval.title}</div>
            {[{ key: 'accuracy_score', label: 'Accuracy' }, { key: 'completeness_score', label: 'Completeness' }].map(({ key, label }) => (
              <div key={key}>
                <div className="flex justify-between mb-1">
                  <label className="text-xs text-gray-400">{label} Score</label>
                  <span className="font-mono text-blue-400 text-sm font-bold">{evalForm[key]}</span>
                </div>
                <input type="range" min="0" max="5" step="0.5" className="w-full accent-blue-500"
                  value={evalForm[key]} onChange={e => setEvalForm(f => ({ ...f, [key]: parseFloat(e.target.value) }))} />
              </div>
            ))}
            <div className="text-center text-sm text-gray-300">
              Composite: <span className="text-blue-400 font-mono font-bold">
                {(evalForm.accuracy_score * 0.6 + evalForm.completeness_score * 0.4).toFixed(2)}
              </span>
            </div>
            <textarea className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 resize-none" rows={3}
              placeholder="Comments..." value={evalForm.comments} onChange={e => setEvalForm(f => ({ ...f, comments: e.target.value }))} />
            {error && <p className="text-red-400 text-sm">{error}</p>}
            <div className="flex gap-2 justify-end">
              <button type="button" onClick={() => setShowEval(null)} className="px-4 py-2 rounded-lg bg-gray-800 text-gray-300 text-sm">Cancel</button>
              <button type="submit" disabled={saving} className="px-4 py-2 rounded-lg bg-blue-600 text-white text-sm disabled:opacity-50">
                {saving ? 'Saving...' : 'Submit'}
              </button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  )
}
