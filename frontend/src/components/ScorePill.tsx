interface ScorePillProps {
  score: number
  size?: 'sm' | 'md' | 'lg'
}

export default function ScorePill({ score, size = 'md' }: ScorePillProps) {
  const color = score >= 70
    ? 'text-green-400 bg-green-400/10 border-green-400/30'
    : score >= 50
    ? 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30'
    : 'text-red-400 bg-red-400/10 border-red-400/30'

  const sizeClass = size === 'sm'
    ? 'text-sm px-3 py-1'
    : size === 'lg'
    ? 'text-2xl px-5 py-2'
    : 'text-lg px-4 py-2'

  return (
    <span className={`font-bold rounded-xl border ${color} ${sizeClass} inline-block`}>
      {score}%
    </span>
  )
}