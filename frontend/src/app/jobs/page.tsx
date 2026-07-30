'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { scoreColor, statusBadge } from '@/lib/utils'
import Link from 'next/link'

export default function JobsPage() {
  const [jobs, setJobs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [url, setUrl] = useState('')
  const [siteName, setSiteName] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const loadJobs = () => {
    api.jobs.list().then(setJobs).catch(console.error).finally(() => setLoading(false))
  }
  useEffect(() => { loadJobs() }, [])

  const createJob = async () => {
    if (!url.trim()) return
    setSubmitting(true)
    await api.jobs.create({ url: url.trim(), site_name: siteName.trim() || null, max_pages: 5 }).catch(console.error)
    setUrl(''); setSiteName('')
    setSubmitting(false)
    loadJobs()
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Audit Jobs</h1>
      <div className="bg-white rounded-lg shadow p-5">
        <h2 className="text-lg font-semibold mb-4">Start New Audit</h2>
        <div className="flex gap-3 flex-wrap">
          <input className="border rounded px-3 py-2 text-sm flex-1 min-w-64" placeholder="Website URL (e.g. https://ap.gov.in)" value={url} onChange={e => setUrl(e.target.value)} />
          <input className="border rounded px-3 py-2 text-sm w-48" placeholder="Site name (optional)" value={siteName} onChange={e => setSiteName(e.target.value)} />
          <button onClick={createJob} disabled={submitting || !url} className="bg-indigo-600 text-white px-4 py-2 rounded text-sm hover:bg-indigo-700 disabled:opacity-50">
            {submitting ? 'Starting...' : 'Start Audit'}
          </button>
        </div>
      </div>
      {loading ? <div className="text-center py-12 text-gray-500">Loading...</div> : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {['Site', 'URL', 'Pages', 'Score', 'Violations', 'Status', 'Report'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {jobs.map(job => (
                <tr key={job.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium">
                    <Link href={`/jobs/${job.id}`} className="text-indigo-600 hover:underline">{job.site_name || 'Unnamed'}</Link>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 max-w-xs truncate">{job.url}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{job.pages_crawled}</td>
                  <td className={`px-4 py-3 text-sm font-bold ${scoreColor(job.compliance_score)}`}>
                    {job.compliance_score !== null ? `${job.compliance_score}%` : '—'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">{job.total_violations}</td>
                  <td className="px-4 py-3 text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusBadge(job.status)}`}>{job.status}</span>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {job.status === 'completed' && (
                      <a href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/reports/${job.id}/pdf`}
                        target="_blank" className="text-indigo-600 hover:underline text-xs">PDF</a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {jobs.length === 0 && <div className="text-center py-12 text-gray-500">No audits yet. Start your first audit above.</div>}
        </div>
      )}
    </div>
  )
}
