export default function TaskCard({ task, isAdmin, onStatusChange, onDelete, onEvaluate }) {
  const statusColors = {
    todo: 'bg-gray-700 text-gray-300',
    in_progress: 'bg-amber-900/50 text-amber-300',
    done: 'bg-emerald-900/50 text-emerald-300'
  }
  const statusLabels = { todo: 'Todo', in_progress: 'In Progress', done: 'Done' }
  const nextStatus = { todo: 'in_progress', in_progress: 'done', done: 'todo' }

  return (
    <div className={`bg-gray-900 border rounded-lg p-4 ${task.is_overdue ? 'border-red-500/50' : 'border-gray-700'}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusColors[task.status]}`}>
              {statusLabels[task.status]}
            </span>
            {task.is_overdue && <span className="text-xs text-red-400">⚠ Overdue</span>}
            {task.evaluation && (
              <span className="text-xs bg-blue-900/40 text-blue-300 px-2 py-0.5 rounded-full">
                Score: {task.evaluation.composite_score}
              </span>
            )}
          </div>
          <h3 className="text-sm font-medium text-white">{task.title}</h3>
          {task.description && <p className="text-xs text-gray-400 mt-1 line-clamp-2">{task.description}</p>}
          <div className="flex gap-3 mt-2 text-xs text-gray-500">
            {task.assignee_name && <span>👤 {task.assignee_name}</span>}
            {task.due_date && <span>📅 {new Date(task.due_date).toLocaleDateString()}</span>}
          </div>
        </div>
        <div className="flex gap-1.5 shrink-0">
          <button
            onClick={() => onStatusChange(task.id, nextStatus[task.status])}
            className="text-xs px-2 py-1 rounded bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors"
          >
            →
          </button>
          {isAdmin && task.status === 'done' && (
            <button
              onClick={() => onEvaluate(task)}
              className="text-xs px-2 py-1 rounded bg-blue-900/50 hover:bg-blue-800/50 text-blue-300 transition-colors"
            >
              {task.evaluation ? 'Re-eval' : 'Eval'}
            </button>
          )}
          {isAdmin && (
            <button
              onClick={() => onDelete(task.id)}
              className="text-xs px-2 py-1 rounded bg-red-900/30 hover:bg-red-900/50 text-red-400 transition-colors"
            >
              ✕
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
