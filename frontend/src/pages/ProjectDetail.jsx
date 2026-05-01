import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../utils/api'
import { useAuth } from '../context/AuthContext'
import Modal from '../components/Modal'
import TaskCard from '../components/TaskCard'

export default function ProjectDetail() {
  const { id } = useParams()
  const { isAdmin } = useAuth()
  const navigate = useNavigate()

  const [project, setProject] = useState(null)
  const [tasks, setTasks] = useState([])
  const [allUsers, setAllUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('tasks')

  // Modals
  const [showAddMember, setShowAddMember] = useState(false)
  const [showCreateTask, setShowCreateTask] = useState(false)
  const [showEval, setShowEval] = useState(null) // task object
  const [addUserId, setAddUserId] = useState('')
  const [taskForm, setTaskForm] = useState({ title: '', description: '', due_date: '', assigned_to: '' })
  const [evalForm, setEvalForm] = useState({ accuracy_score: 3, completeness_score: 3, comments: '' })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const load = () => {
    Promise.all([
      api.get(`/projects/${id}`),
      api.get(`/tasks?project_id=${id}`),
      isAdmin ? api.get('/projects/users') : Promise.resolve({ data: { users: [] } })
    ]).then(([p, t, u]) => {
      setProject(p.data.project)
      setTasks(t.data.tasks)
      setAllUsers(u.data.users)
    }).catch(err => {
      if (err.response?.status === 403) navigate('/projects')
    }).finally(() => setLoading(false))
  }

  useEffect(load, [id])

  const handleAddMember = async (e) => {
    e.preventDefault()
    setSaving(true); setError('')
    try {
      await api.post(`/projects/${id}/members`, { user_id: parseInt(addUserId) })
      setShowAddMember(false); setAddUserId(''); load()
    } catch (err) { setError(err.response?.data?.error || 'Failed') }
    finally { setSaving(false) }
  }

  const handleRemoveMember = async (userId) => {
    if (!confirm('Remove this member?')) return
    await api.delete(`/projects/${id}/members/${userId}`)
    load()
  }

  const handleCreateTask = async (e) => {
    e.preventDefault()
    setSaving(true); setError('')
    try {
      await api.post('/tasks', { ...taskForm, project_id: parseInt(id), assigned_to: taskForm.assigned_to ? parseInt(taskForm.assigned_to) : null })
      setShowCreateTask(false)
      setTaskForm({ title: '', description: '', due_date: '', assigned_to: '' })
      load()
    } catch (err) { setError(err.response?.data?.error || 'Failed') }
    finally { setSaving(false) }
  }

  const handleStatusChange = async (taskId, status) => {
    await api.patch(`/tasks/${taskId}/status`, { status })
    load()
  }

  const handleDeleteTask = async (taskId) => {
    if (!confirm('Delete this task?')) return
    await api.delete(`/tasks/${taskId}`)
    load()
  }

  const handleEvaluate = async (e) => {
    e.preventDefault()
    setSaving(true); setError('')
    try {
      await api.post(`/tasks/${showEval.id}/evaluate`, evalForm)
      setShowEval(null)
      load()
    } catch (err) { setError(err.response?.data?.error || 'Failed') }
    finally { setSaving(false) }
  }

  const openEvalModal = (task) => {
    setShowEval(task)
    setEvalForm({
      accuracy_score: task.evaluation?.accuracy_score ?? 3,
      completeness_score: task.evaluation?.completeness_score ?? 3,
      comments: task.evaluation?.comments ?? ''
    })
    setError('')
  }

  if (loading) return <div className="flex justify-center py-20"><div className="w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full animate-spin"/></div>
  if (!project) return null

  const nonMembers = allUsers.filter(u => !project.members?.some(m => m.user_id === u.id))

  return (
    <div className="animate-slide-up">
      {/* Header */}
      <div className="flex items-start justify-between mb-5">
        <div>
          <button onClick={() => navigate('/projects')} className="text-xs text-slate-500 hover:text-slate-300 mb-2 flex items-center gap-1">
            ← Projects
          </button>
          <h1 className="text-2xl font-bold text-slate-100">{project.name}</h1>
          {project.description && <p className="text-slate-500 text-sm mt-1">{project.description}</p>}
        </div>
        {isAdmin && (
          <div className="flex gap-2">
            <button onClick={() => setShowAddMember(true)} className="btn-secondary text-xs">+ Member</button>
            <button onClick={() => { setError(''); setShowCreateTask(true) }} className="btn-primary text-xs">+ Task</button>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-4 bg-surface-1 p-1 rounded-lg border border-surface-3 w-fit">
        {['tasks', 'members'].map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all capitalize ${
              tab === t ? 'bg-brand-500 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {t} {t === 'tasks' ? `(${tasks.length})` : `(${project.members?.length ?? 0})`}
          </button>
        ))}
      </div>

      {/* Tasks tab */}
      {tab === 'tasks' && (
        <div>
          {tasks.length === 0 ? (
            <div className="card text-center py-12">
              <div className="text-4xl mb-2">📋</div>
              <div className="text-slate-400">No tasks yet</div>
              {isAdmin && <button onClick={() => setShowCreateTask(true)} className="btn-primary mt-3 text-xs">Add first task</button>}
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {tasks.map(task => (
                <TaskCard
                  key={task.id}
                  task={task}
                  isAdmin={isAdmin}
                  onStatusChange={handleStatusChange}
                  onDelete={handleDeleteTask}
                  onEvaluate={openEvalModal}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Members tab */}
      {tab === 'members' && (
        <div className="flex flex-col gap-2">
          {project.members?.map(m => (
            <div key={m.id} className="card flex items-center justify-between py-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-brand-500/15 border border-brand-500/20 flex items-center justify-center">
                  <span className="text-brand-500 text-sm font-bold">{m.user_name?.[0]?.toUpperCase()}</span>
                </div>
                <div>
                  <div className="text-sm font-medium text-slate-200">{m.user_name}</div>
                  <div className="text-xs text-slate-500">{m.user_email}</div>
                </div>
              </div>
              {isAdmin && m.user_id !== project.owner_id && (
                <button onClick={() => handleRemoveMember(m.user_id)} className="btn-danger text-xs py-1 px-3">Remove</button>
              )}
              {m.user_id === project.owner_id && (
                <span className="text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded-full">Owner</span>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Add Member Modal */}
      <Modal open={showAddMember} onClose={() => setShowAddMember(false)} title="Add Member">
        <form onSubmit={handleAddMember} className="flex flex-col gap-4">
          <div>
            <label className="label">Select User</label>
            <select className="input-field" value={addUserId} onChange={e => setAddUserId(e.target.value)} required>
              <option value="">— select user —</option>
              {nonMembers.map(u => <option key={u.id} value={u.id}>{u.name} ({u.email})</option>)}
            </select>
          </div>
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <div className="flex gap-2 justify-end">
            <button type="button" onClick={() => setShowAddMember(false)} className="btn-secondary">Cancel</button>
            <button type="submit" className="btn-primary" disabled={saving || !addUserId}>{saving ? 'Adding...' : 'Add'}</button>
          </div>
        </form>
      </Modal>

      {/* Create Task Modal */}
      <Modal open={showCreateTask} onClose={() => setShowCreateTask(false)} title="Create Task" size="lg">
        <form onSubmit={handleCreateTask} className="flex flex-col gap-4">
          <div>
            <label className="label">Title</label>
            <input className="input-field" placeholder="Task title" value={taskForm.title}
              onChange={e => setTaskForm(f => ({ ...f, title: e.target.value }))} required />
          </div>
          <div>
            <label className="label">Description</label>
            <textarea className="input-field resize-none" rows={3} placeholder="Details..."
              value={taskForm.description} onChange={e => setTaskForm(f => ({ ...f, description: e.target.value }))} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Due Date</label>
              <input type="datetime-local" className="input-field" value={taskForm.due_date}
                onChange={e => setTaskForm(f => ({ ...f, due_date: e.target.value }))} />
            </div>
            <div>
              <label className="label">Assign To</label>
              <select className="input-field" value={taskForm.assigned_to}
                onChange={e => setTaskForm(f => ({ ...f, assigned_to: e.target.value }))}>
                <option value="">Unassigned</option>
                {project.members?.map(m => <option key={m.user_id} value={m.user_id}>{m.user_name}</option>)}
              </select>
            </div>
          </div>
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <div className="flex gap-2 justify-end">
            <button type="button" onClick={() => setShowCreateTask(false)} className="btn-secondary">Cancel</button>
            <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Creating...' : 'Create Task'}</button>
          </div>
        </form>
      </Modal>

      {/* Evaluation Modal */}
      <Modal open={!!showEval} onClose={() => setShowEval(null)} title="Evaluate Task" size="lg">
        {showEval && (
          <form onSubmit={handleEvaluate} className="flex flex-col gap-4">
            <div className="p-3 bg-surface-2 rounded-lg border border-surface-3">
              <div className="text-sm font-medium text-slate-200">{showEval.title}</div>
              <div className="text-xs text-slate-500 mt-0.5">Completed task • {showEval.assignee_name || 'Unassigned'}</div>
            </div>

            {/* Score sliders */}
            {[
              { key: 'accuracy_score', label: 'Accuracy Score', desc: 'How correct and precise was the output?' },
              { key: 'completeness_score', label: 'Completeness Score', desc: 'Were all requirements addressed?' }
            ].map(({ key, label, desc }) => (
              <div key={key}>
                <div className="flex items-center justify-between mb-1">
                  <div>
                    <label className="label mb-0">{label}</label>
                    <div className="text-[10px] text-slate-500">{desc}</div>
                  </div>
                  <div className="text-xl font-bold font-mono text-brand-500">{evalForm[key]}</div>
                </div>
                <input
                  type="range" min="0" max="5" step="0.5"
                  className="w-full accent-brand-500"
                  value={evalForm[key]}
                  onChange={e => setEvalForm(f => ({ ...f, [key]: parseFloat(e.target.value) }))}
                />
                <div className="flex justify-between text-[10px] text-slate-600 mt-0.5">
                  <span>0 — Poor</span><span>2.5 — Average</span><span>5 — Excellent</span>
                </div>
              </div>
            ))}

            <div className="p-3 bg-brand-500/5 border border-brand-500/15 rounded-lg text-sm text-center">
              Composite Score: <span className="font-bold font-mono text-brand-500">
                {((evalForm.accuracy_score * 0.6 + evalForm.completeness_score * 0.4)).toFixed(2)}
              </span> / 5
            </div>

            <div>
              <label className="label">Comments / Feedback</label>
              <textarea className="input-field resize-none" rows={3}
                placeholder="Qualitative feedback on this task completion..."
                value={evalForm.comments}
                onChange={e => setEvalForm(f => ({ ...f, comments: e.target.value }))} />
            </div>

            {error && <p className="text-red-400 text-sm">{error}</p>}
            <div className="flex gap-2 justify-end">
              <button type="button" onClick={() => setShowEval(null)} className="btn-secondary">Cancel</button>
              <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Saving...' : showEval.evaluation ? 'Update Evaluation' : 'Submit Evaluation'}</button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  )
}
