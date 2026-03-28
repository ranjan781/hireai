type SkillType = 'strong' | 'weak' | 'missing' | 'neutral'

interface SkillTagProps {
  skill: string
  type?: SkillType
}

const styles: Record<SkillType, string> = {
  strong: 'bg-green-400/10 text-green-400 border-green-400/20',
  weak: 'bg-yellow-400/10 text-yellow-400 border-yellow-400/20',
  missing: 'bg-red-400/10 text-red-400 border-red-400/20',
  neutral: 'bg-surface text-muted border-border',
}

export default function SkillTag({ skill, type = 'neutral' }: SkillTagProps) {
  return (
    <span className={`text-xs px-2.5 py-1 rounded-lg border font-medium ${styles[type]}`}>
      {skill}
    </span>
  )
}