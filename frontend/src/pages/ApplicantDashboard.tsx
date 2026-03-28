import { useState, useEffect, useRef } from 'react'
import { useAuthStore } from '../store/authStore'
import api from '../api/client'
import Navbar from '../components/Navbar'
import Sidebar from '../components/Sidebar'
import StatCard from '../components/StatCard'
import ScorePill from '../components/ScorePill'
import SkillTag from '../components/SkillTag'

const sidebarItems = [
  { id: 'overview', label: 'Overview', icon: '▦' },
  { id: 'jobs', label: 'Browse Jobs', icon: '🔍' },
  { id: 'resume', label: 'My Resume', icon: '📄' },
  { id: 'applications', label: 'Applications', icon: '📋' },
]

export default function ApplicantDashboard() {
  const { user } = useAuthStore()
  const [tab, setTab] = useState('overview')
  const [jobs, setJobs] = useState<any[]>([])
  const [resumes, setResumes] = useState<any[]>([])
  const [applications, setApplications] = useState<any[]>([])
  const [uploading, setUploading] = useState(false)
  const [applying, setApplying] = useState<string | null>(null)
  const [toast, setToast] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetchAll()
  }, [])

  const fetchAll = async () => {
    try { const r = await api.get('/jobs'); setJobs(r.data) } catch {}
    try { const r = await api.get('/resumes/my'); setResumes(r.data) } catch {}
    try { const r = await api.get('/applications/my'); setApplications(r.data) } catch {}
  }

  const showToast = (msg: string) => {
    setToast(msg)
    setTimeout(() => setToast(''), 3000)
  }

  const uploadResume = async (file: File) => {
    setUploading(true)
    const fd = new FormData()
    fd.append('file', file)
    try {
      await api.post('/resumes/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      await fetchAll()
      showToast('Resume uploaded successfully!')
    } catch {
      showToast('Upload failed. Try again.')
    } finally {
      setUploading(false)
    }
  }

  const applyForJob = async (jobId: string) => {
    if (!resumes.length) {
      showToast('Please upload your resume first!')
      setTab('resume')
      return
    }
    setApplying(jobId)
    try {
      await api.post('/applications/apply', { job_id: jobId, resume_id: resumes[0].id })
      await fetchAll()
      showToast('Application submitted! ML score calculated.')
      setTab('applications')
    } catch (e: any) {
      showToast(e.response?.data?.detail || 'Error applying')
    } finally {
      setApplying(null) }
  }

  const appliedJobIds = applications.map((a: any) => a.job_id)

  const statusColors: Record<string, string> = {
    applied: 'bg-blue-400/10 text-blue-400 border-blue-400/20',
    shortlisted: 'bg-green-400/10 text-green-400 border-green-400/20',
    interview: 'bg-purple-400/10 text-purple-400 border-purple-400/20',
    selected: 'bg-emerald-400/10 text-emerald-400 border-emerald-400/20',
    rejected: 'bg-red-400/10 text-red-400 border-red-400/20',
  }

  return (
    <div className="min-h-screen bg-bg flex flex-col">
      <Navbar role="applicant" />

      {/* Toast */}
      {toast && (
        <div className="fixed bottom-6 right-6 z-50 bg-card border border-border rounded-xl px-4 py-3 text-sm font-medium shadow-lg">
          {toast}
        </div>
      )}

      <div className="flex flex-1">
        <Sidebar items={sidebarItems} active={tab} onSelect={setTab} role="applicant" />

        <main className="flex-1 p-6 overflow-auto">

          {/* OVERVIEW */}
          {tab === 'overview' && (
            <div className="max-w-4xl">
              <h1 className="text-xl font-semibold mb-5">My Dashboard</h1>
              <div className="grid grid-cols-3 gap-4 mb-6">
                <StatCard label="Applications" value={applications.length} color="text-ap-accent" icon="📋" />
                <StatCard label="Resumes" value={resumes.length} color="text-hr-accent" icon="📄" />
                <StatCard label="Jobs Available" value={jobs.length} color="text-warn" icon="💼" />
              </div>

              {applications.length > 0 && (
                <div className="bg-card border border-border rounded-2xl overflow-hidden">
                  <div className="px-5 py-4 border-b border-border flex items-center justify-between">
                    <h2 className="font-semibold text-sm">Recent Applications</h2>
                    <button onClick={() => setTab('applications')} className="text-xs text-ap-accent hover:underline">View all</button>
                  </div>
                  <div className="divide-y divide-border">
                    {applications.slice(0, 3).map((app: any) => (
                      <div key={app.id} className="px-5 py-4 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <ScorePill score={app.match_score} size="sm" />
                          <div>
                            <p className="text-xs text-muted">ML Match Score</p>
                            <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${statusColors[app.status] || ''}`}>
                              {app.status}
                            </span>
                          </div>
                        </div>
                        <div className="flex gap-1 flex-wrap justify-end max-w-xs">
                          {app.strong_skills?.slice(0, 3).map((s: string) => <SkillTag key={s} skill={s} type="strong" />)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {resumes.length === 0 && (
                <div className="mt-4 bg-blue-400/5 border border-blue-400/20 rounded-2xl p-5 flex items-center gap-4">
                  <span className="text-2xl">💡</span>
                  <div>
                    <p className="font-medium text-sm">Upload your resume to get started</p>
                    <p className="text-xs text-muted mt-0.5">Our ML engine will analyze your skills and match you with jobs</p>
                  </div>
                  <button onClick={() => setTab('resume')} className="ml-auto shrink-0 text-sm bg-ap-accent text-black font-semibold px-4 py-2 rounded-xl hover:opacity-90">
                    Upload Now
                  </button>
                </div>
              )}
            </div>
          )}

          {/* BROWSE JOBS */}
          {tab === 'jobs' && (
            <div className="max-w-4xl">
              <h1 className="text-xl font-semibold mb-5">Browse Jobs</h1>
              <div className="space-y-3">
                {jobs.map((job: any) => (
                  <div key={job.id} className="bg-card border border-border rounded-2xl p-5 hover:border-ap-accent/30 transition">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap mb-1">
                          <h3 className="font-semibold">{job.title}</h3>
                          <span className="text-xs bg-surface border border-border px-2 py-0.5 rounded-full text-muted">{job.job_type}</span>
                          {appliedJobIds.includes(job.id) && (
                            <span className="text-xs bg-green-400/10 text-green-400 border border-green-400/20 px-2 py-0.5 rounded-full">Applied</span>
                          )}
                        </div>
                        <p className="text-sm text-muted mb-1">{job.company} · {job.location || 'Remote'}</p>
                        {job.salary_range && <p className="text-xs text-warn mb-3">{job.salary_range} · {job.min_experience_years}y experience</p>}
                        <p className="text-sm text-gray-400 mb-3 line-clamp-2">{job.description}</p>
                        <div className="flex flex-wrap gap-1.5">
                          {job.required_skills?.map((s: string) => <SkillTag key={s} skill={s} type="strong" />)}
                          {job.preferred_skills?.map((s: string) => <SkillTag key={s} skill={s} type="neutral" />)}
                        </div>
                      </div>
                      <button
                        onClick={() => applyForJob(job.id)}
                        disabled={appliedJobIds.includes(job.id) || applying === job.id}
                        className={`shrink-0 text-sm font-semibold px-4 py-2 rounded-xl transition ${
                          appliedJobIds.includes(job.id)
                            ? 'bg-green-400/10 text-green-400 border border-green-400/30 cursor-default'
                            : 'bg-ap-accent text-black hover:opacity-90 disabled:opacity-50'
                        }`}
                      >
                        {appliedJobIds.includes(job.id) ? '✓ Applied' : applying === job.id ? 'Applying...' : 'Apply Now'}
                      </button>
                    </div>
                  </div>
                ))}
                {jobs.length === 0 && <div className="py-16 text-center text-muted">No jobs available right now</div>}
              </div>
            </div>
          )}

          {/* RESUME */}
          {tab === 'resume' && (
            <div className="max-w-3xl">
              <h1 className="text-xl font-semibold mb-5">My Resume</h1>

              <div
                onClick={() => !uploading && fileRef.current?.click()}
                className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition mb-5 ${
                  uploading ? 'border-ap-accent/50 bg-ap-accent/5' : 'border-border hover:border-ap-accent/50 hover:bg-surface'
                }`}
              >
                <div className="text-3xl mb-3">{uploading ? '⏳' : '📤'}</div>
                <p className="font-medium">{uploading ? 'Uploading & Parsing...' : 'Click to upload resume'}</p>
                <p className="text-sm text-muted mt-1">PDF or DOCX · Max 10MB</p>
                <input ref={fileRef} type="file" accept=".pdf,.docx,.doc" className="hidden"
                  onChange={e => e.target.files?.[0] && uploadResume(e.target.files[0])} />
              </div>

              {resumes.map((resume: any) => (
                <div key={resume.id} className="bg-card border border-border rounded-2xl p-5 mb-3">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <p className="font-medium">{resume.file_name}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${
                          resume.is_parsed === 'done'
                            ? 'bg-green-400/10 text-green-400 border-green-400/20'
                            : 'bg-yellow-400/10 text-yellow-400 border-yellow-400/20'
                        }`}>
                          {resume.is_parsed === 'done' ? 'Parsed' : 'Processing'}
                        </span>
                        <span className="text-xs text-muted">{resume.extracted_experience_years}y experience detected</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-ap-accent">{resume.extracted_skills?.length || 0}</p>
                      <p className="text-xs text-muted">skills found</p>
                    </div>
                  </div>

                  {resume.extracted_skills?.length > 0 && (
                    <div>
                      <p className="text-xs text-muted font-medium uppercase tracking-wider mb-2">Extracted Skills</p>
                      <div className="flex flex-wrap gap-1.5">
                        {resume.extracted_skills.map((s: string) => <SkillTag key={s} skill={s} type="neutral" />)}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* APPLICATIONS */}
          {tab === 'applications' && (
            <div className="max-w-4xl">
              <h1 className="text-xl font-semibold mb-5">My Applications</h1>
              <div className="space-y-3">
                {applications.map((app: any, idx: number) => (
                  <div key={app.id} className="bg-card border border-border rounded-2xl p-5">
                    <div className="flex items-start justify-between gap-4 mb-4">
                      <div className="flex items-center gap-3">
                        <ScorePill score={app.match_score} size="lg" />
                        <div>
                          <p className="font-medium text-sm">Application #{idx + 1}</p>
                          <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${statusColors[app.status] || 'bg-surface text-muted border-border'}`}>
                            {app.status}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-3 mb-3">
                      {app.strong_skills?.length > 0 && (
                        <div>
                          <p className="text-xs text-muted font-medium mb-1.5">Strong Skills</p>
                          <div className="flex flex-wrap gap-1">
                            {app.strong_skills.map((s: string) => <SkillTag key={s} skill={s} type="strong" />)}
                          </div>
                        </div>
                      )}
                      {app.weak_skills?.length > 0 && (
                        <div>
                          <p className="text-xs text-muted font-medium mb-1.5">Needs Work</p>
                          <div className="flex flex-wrap gap-1">
                            {app.weak_skills.map((s: string) => <SkillTag key={s} skill={s} type="weak" />)}
                          </div>
                        </div>
                      )}
                      {app.missing_skills?.length > 0 && (
                        <div>
                          <p className="text-xs text-muted font-medium mb-1.5">Missing Skills</p>
                          <div className="flex flex-wrap gap-1">
                            {app.missing_skills.map((s: string) => <SkillTag key={s} skill={s} type="missing" />)}
                          </div>
                        </div>
                      )}
                    </div>

                    {app.ai_recommendation && (
                      <div className="bg-surface border border-border rounded-xl p-3.5">
                        <p className="text-xs text-muted font-medium uppercase tracking-wider mb-1.5">AI Feedback</p>
                        <p className="text-sm text-gray-300 leading-relaxed">{app.ai_recommendation}</p>
                      </div>
                    )}
                  </div>
                ))}
                {applications.length === 0 && (
                  <div className="py-16 text-center">
                    <p className="text-muted mb-3">No applications yet</p>
                    <button onClick={() => setTab('jobs')} className="text-sm bg-ap-accent text-black font-semibold px-4 py-2 rounded-xl hover:opacity-90">
                      Browse Jobs
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}