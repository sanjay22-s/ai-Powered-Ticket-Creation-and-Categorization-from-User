/**
 * Color-coded priority badge: Critical = dark red, High = red, Medium = yellow, Low = green.
 */
interface PriorityBadgeProps {
  priority: string
  className?: string
}

const priorityStyles: Record<string, string> = {
  Critical: 'bg-red-900 text-white',
  High: 'bg-red-500 text-white',
  Medium: 'bg-amber-400 text-amber-900',
  Low: 'bg-emerald-500 text-white',
}

export function PriorityBadge({ priority, className = '' }: PriorityBadgeProps) {
  const style = priorityStyles[priority] || 'bg-slate-200 text-slate-700'
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${style} ${className}`}>
      {priority}
    </span>
  )
}
