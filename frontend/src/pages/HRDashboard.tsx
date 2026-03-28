import { useState, useEffect } from 'react'
import { useAuthStore } from '../store/authStore'
import api from '../api/client'
import Navbar from '../components/Navbar'
import Sidebar from '../components/Sidebar'
import StatCard from '../components/StatCard'
import ScorePill from '../components/ScorePill'
import SkillTag from '../components/SkillTag'

const sidebarItems = [
  { id: 'overview', label: 'Overview', icon: '▦' },
  { id: 'jobs', label: 'Job Postings', icon: '💼' },
  { id: 'applicants', label: 'Applicants', icon: '👥' },
]

export default function HRDashboard() {
  const { user } = useAuthStore()
  const [tab, setTab] = useState('overview')
  const [jobs, setJobs] = useState<any[]>([])
  const [applications, setApplications] = useState<any[]>([])
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [selectedApp, setSelectedApp] = useState<any | null>(null)
  const [form, setForm] = useState({
    title: '', company: user?.company || '',
    location: '', job_type: 'full-time',
    description: '', requirements: '',
    required_skills: '', preferred_skills: '',
    min_experience_years: '0', salary_range: ''
  })

  useEffect(() => { fetchJobs() }, [])

  const fetchJobs = async () => {
    try { const r = await api.get('/jobs'); setJobs(r.data) } catch {}
  }

  const fetchApplicants = async (jobId: string) => {
    try {
      const r = await api.get(`/applications/job/${jobId}`)
      setApplications(r.data)
      setSelectedJobId(jobId)
      setTab('applicants')
    } catch {}
  }

  const createJob = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/jobs', {
        ...form,
        required_skills: form.required_skills.split(',').map(s => s.trim()).filter(Boolean),
        preferred_skills: form.preferred_skills.split(',').map(s => s.trim()).filter(Boolean),
      })
      setShowForm(false)
      setForm({ title: '', company: user?.company || '', location: '', job_type: 'full-time', description: '', requirements: '', required_skills: '', preferred_skills: '', min_experience_years: '0', salary_range: '' })
      fetchJobs()
    } catch {}
  }

  const updateStatus = async (appId: string, status: string) => {
    try {
      await api.patch(`/applications/${appId}/status`, { status })
      if (selectedJobId) fetchApplicants(selectedJobId)
    } catch {}
  }

  const statusColors: Record<string, string> = {
    applied: 'bg-blue-400/10 text-blue-400',
    under_review: 'bg-yellow-400/10 text-yellow-400',
    shortlisted: 'bg-green-400/10 text-green-400',
    interview: 'bg-purple-400/10 text-purple-400',
    selected: 'bg-emerald-400/10 text-emerald-400',
    rejected: 'bg-red-400/10 text-red-400',
  }

  return (
    <div className="min-h-screen bg-bg flex flex-col">
      <Navbar role="hr" />
      <div className="flex flex-1">
        <Sidebar items={sidebarItems} active={tab} onSelect={setTab} role="hr" />

        <main className="flex-1 p-6 overflow-auto">

          {/* OVERVIEW */}
          {tab === 'overview' && (
            <div className="max-w-5xl">
              <h1 className="text-xl font-semibold mb-5">Dashboard Overview</h1>
              <div className="grid grid-cols-3 gap-4 mb-6">
                <StatCard label="Active Jobs" value={jobs.filter(j => j.is_active).length} color="text-hr-accent" icon="💼" />
                <StatCard label="Total Applicants" value={applications.length} color="text-ap-accent" icon="👥" />
                <StatCard label="Company" value={user?.company || '—'} color="text-warn" icon="🏢" />
              </div>

              <div className="bg-card border border-border rounded-2xl overflow-hidden">
                <div className="px-5 py-4 border-b border-border flex items-center justify-between">
                  <h2 className="font-semibold text-sm">Recent Jobs</h2>
                  <button onClick={() => setTab('jobs')} className="text-xs text-hr-accent hover:underline">View all</button>
                </div>
                {jobs.length === 0 ? (
                  <div className="py-12 text-center text-muted text-sm">No jobs posted yet</div>
                ) : (
                  <div className="divide-y divide-border">
                    {jobs.slice(0, 4).map(job => (
                      <div key={job.id} className="px-5 py-4 flex items-center justify-between hover:bg-card2 transition">
                        <div>
                          <p className="font-medium text-sm">{job.title}</p>
                          <p className="text-xs text-muted mt-0.5">{job.company} · {job.location || 'Remote'} · {job.salary_range || 'Salary TBD'}</p>
                        </div>
                        <button
                          onClick={() => fetchApplicants(job.id)}
                          className="text-xs bg-hr-accent/10 text-hr-accent border border-hr-accent/30 px-3 py-1.5 rounded-lg hover:bg-hr-accent/20 transition font-medium"
                        >
                          View Applicants
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* JOBS */}
          {tab === 'jobs' && (
            <div className="max-w-5xl">
              <div className="flex items-center justify-between mb-5">
                <h1 className="text-xl font-semibold">Job Postings</h1>
                <button
                  onClick={() => setShowForm(!showForm)}
                  className="text-sm bg-hr-accent text-black font-semibold px-4 py-2 rounded-xl hover:opacity-90 transition"
                >
                  + Post New Job
                </button>
              </div>

              {showForm && (
                <div className="bg-card border border-border rounded-2xl p-5 mb-5">
                  <h3 className="font-semibold text-sm mb-4">New Job Description</h3>
                  <form onSubmit={createJob} className="grid grid-cols-2 gap-3">
                    {[
                      { placeholder: 'Job Title *', key: 'title', full: true, required: true },
                      { placeholder: 'Company', key: 'company' },
                      { placeholder: 'Location', key: 'location' },
                      { placeholder: 'Min Experience Years', key: 'min_experience_years' },
                      { placeholder: 'Salary Range (e.g. 15-25 LPA)', key: 'salary_range' },
                      { placeholder: 'Required Skills (comma separated)', key: 'required_skills', full: true },
                      { placeholder: 'Preferred Skills (comma separated)', key: 'preferred_skills', full: true },
                    ].map(f => (
                      <input
                        key={f.key}
                        placeholder={f.placeholder}
                        value={(form as any)[f.key]}
                        onChange={e => setForm({...form, [f.key]: e.target.value})}
                        required={f.required}
                        className={`bg-surface border border-border rounded-xl px-4 py-2.5 text-sm focus:border-hr-accent transition ${f.full ? 'col-span-2' : ''}`}
                      />
                    ))}
                    <textarea
                      placeholder="Job Description *"
                      value={form.description}
                      onChange={e => setForm({...form, description: e.target.value})}
                      required
                      className="col-span-2 bg-surface border border-border rounded-xl px-4 py-2.5 text-sm h-24 resize-none focus:border-hr-accent transition"
                    />
                    <div className="col-span-2 flex gap-2">
                      <button type="submit" className="bg-hr-accent text-black font-semibold px-5 py-2 rounded-xl text-sm hover:opacity-90">Post Job</button>
                      <button type="button" onClick={() => setShowForm(false)} className="bg-surface border border-border px-5 py-2 rounded-xl text-sm hover:bg-card transition">Cancel</button>
                    </div>
                  </form>
                </div>
              )}

              <div className="space-y-3">
                {jobs.map(job => (
                  <div key={job.id} className="bg-card border border-border rounded-2xl p-5 hover:border-border transition">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap mb-1">
                          <h3 className="font-semibold">{job.title}</h3>
                          <span className="text-xs bg-surface border border-border px-2 py-0.5 rounded-full text-muted">{job.job_type}</span>
                        </div>
                        <p className="text-sm text-muted mb-3">{job.company} · {job.location || 'Remote'} · {job.salary_range || 'Salary TBD'} · {job.min_experience_years}y exp</p>
                        <div className="flex flex-wrap gap-1.5">
                          {job.required_skills?.map((s: string) => (
                            <SkillTag key={s} skill={s} type="strong" />
                          ))}
                          {job.preferred_skills?.map((s: string) => (
                            <SkillTag key={s} skill={s} type="neutral" />
                          ))}
                        </div>
                      </div>
                      <button
                        onClick={() => fetchApplicants(job.id)}
                        className="shrink-0 text-sm bg-hr-accent text-black font-semibold px-4 py-2 rounded-xl hover:opacity-90 transition"
                      >
                        View Applicants
                      </button>
                    </div>
                  </div>
                ))}
                {jobs.length === 0 && (
                  <div className="py-16 text-center text-muted">No jobs posted yet. Click "Post New Job" to get started!</div>
                )}
              </div>
            </div>
          )}

          {/* APPLICANTS */}
          {tab === 'applicants' && (
            <div className="max-w-5xl">
              <div className="flex items-center gap-3 mb-5">
                <h1 className="text-xl font-semibold">Applicants</h1>
                <span className="text-xs bg-surface border border-border px-2.5 py-1 rounded-full text-muted">{applications.length} found</span>
              </div>

              {!selectedJobId ? (
                <div className="py-16 text-center text-muted">Select a job from "Job Postings" to view applicants</div>
              ) : applications.length === 0 ? (
                <div className="py-16 text-center text-muted">No applicants for this job yet</div>
              ) : (
                <div className="space-y-3">
                  {applications.map((app, idx) => (
                    <div key={app.id} className="bg-card border border-border rounded-2xl p-5">
                      <div className="flex items-start justify-between gap-4 mb-4">
                        <div className="flex items-center gap-3">
                          <ScorePill score={app.match_score} size="lg" />
                          <div>
                            <p className="font-medium text-sm">Applicant #{idx + 1}</p>
                            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusColors[app.status] || 'bg-surface text-muted'}`}>
                              {app.status}
                            </span>
                          </div>
                        </div>
                        <div className="flex gap-1.5 flex-wrap">
                          {['shortlisted', 'interview', 'selected', 'rejected'].map(s => (
                            <button
                              key={s}
                              onClick={() => updateStatus(app.id, s)}
                              className={`text-xs px-3 py-1.5 rounded-lg border transition font-medium ${
                                app.status === s
                                  ? 'bg-hr-accent text-black border-hr-accent'
                                  : 'border-border text-muted hover:text-white hover:border-muted'
                              }`}
                            >
                              {s}
                            </button>
                          ))}
                        </div>
                      </div>

                      <div className="grid grid-cols-3 gap-3 mb-3">
                        {app.strong_skills?.length > 0 && (
                          <div>
                            <p className="text-xs text-muted mb-1.5 font-medium">Strong</p>
                            <div className="flex flex-wrap gap-1">
                              {app.strong_skills.map((s: string) => <SkillTag key={s} skill={s} type="strong" />)}
                            </div>
                          </div>
                        )}
                        {app.weak_skills?.length > 0 && (
                          <div>
                            <p className="text-xs text-muted mb-1.5 font-medium">Partial</p>
                            <div className="flex flex-wrap gap-1">
                              {app.weak_skills.map((s: string) => <SkillTag key={s} skill={s} type="weak" />)}
                            </div>
                          </div>
                        )}
                        {app.missing_skills?.length > 0 && (
                          <div>
                            <p className="text-xs text-muted mb-1.5 font-medium">Missing</p>
                            <div className="flex flex-wrap gap-1">
                              {app.missing_skills.map((s: string) => <SkillTag key={s} skill={s} type="missing" />)}
                            </div>
                          </div>
                        )}
                      </div>

                      {app.ai_recommendation && (
                        <div className="bg-surface border border-border rounded-xl p-3.5">
                          <p className="text-xs text-muted font-medium uppercase tracking-wider mb-1.5">AI Recommendation</p>
                          <p className="text-sm text-gray-300 leading-relaxed">{app.ai_recommendation}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  )
}