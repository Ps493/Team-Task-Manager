export default function ScoreBar({ value, max = 5, color = 'brand' }) {
  const pct = value != null ? (value / max) * 100 : 0
  const colors = {
    brand: 'bg-blue-500',
    emerald: 'bg-emerald-500',
  }
  return (
    <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
      <div
        className={`h-full ${colors[color] || 'bg-blue-500'} rounded-full transition-all duration-500`}
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}
