interface SidebarItem {
  id: string
  label: string
  icon: string
  badge?: number
}

interface SidebarProps {
  items: SidebarItem[]
  active: string
  onSelect: (id: string) => void
  role: 'hr' | 'applicant'
}

export default function Sidebar({ items, active, onSelect, role }: SidebarProps) {
  const activeClass = role === 'hr'
    ? 'bg-green-400/10 text-green-400 border-l-2 border-green-400'
    : 'bg-blue-400/10 text-blue-400 border-l-2 border-blue-400'

  return (
    <div className="w-56 bg-surface border-r border-border flex flex-col py-4">
      {items.map(item => (
        <button
          key={item.id}
          onClick={() => onSelect(item.id)}
          className={`flex items-center gap-3 px-4 py-2.5 text-sm font-medium transition-all text-left mx-2 rounded-lg ${
            active === item.id
              ? activeClass
              : 'text-muted hover:text-white hover:bg-card'
          }`}
        >
          <span className="text-base w-5 text-center">{item.icon}</span>
          <span>{item.label}</span>
          {item.badge !== undefined && item.badge > 0 && (
            <span className="ml-auto bg-danger text-white text-xs px-1.5 py-0.5 rounded-full">
              {item.badge}
            </span>
          )}
        </button>
      ))}
    </div>
  )
}