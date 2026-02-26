/**
 * Stat card for dashboard metrics.
 */
interface StatsCardProps {
  title: string
  value: number
  subtitle?: string
  accent?: 'blue' | 'green' | 'yellow' | 'red' | 'slate'
}

const accentClasses = {
  blue: 'bg-primary-50 text-primary-700 border-primary-200',
  green: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  yellow: 'bg-amber-50 text-amber-700 border-amber-200',
  red: 'bg-red-50 text-red-700 border-red-200',
  slate: 'bg-slate-50 text-slate-700 border-slate-200',
}

export function StatsCard({ title, value, subtitle, accent = 'slate' }: StatsCardProps) {
  return (
    <div className={`rounded-xl border p-5 ${accentClasses[accent]}`}>
      <p className="text-sm font-medium opacity-90">{title}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
      {subtitle && <p className="text-xs mt-1 opacity-80">{subtitle}</p>}
    </div>
  )
}
