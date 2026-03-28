interface StatCardProps {
  label: string
  value: string | number
  color?: string
  icon?: string
}

export default function StatCard({ label, value, color = 'text-white', icon }: StatCardProps) {
  return (
    <div className="bg-card border border-border rounded-2xl p-5 flex items-center gap-4">
      {icon && (
        <div className="w-10 h-10 rounded-xl bg-surface flex items-center justify-center text-lg">
          {icon}
        </div>
      )}
      <div>
        <p className="text-xs text-muted uppercase tracking-widest font-medium mb-1">{label}</p>
        <p className={`text-2xl font-bold ${color}`}>{value}</p>
      </div>
    </div>
  )
}