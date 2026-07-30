'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { scoreColor, statusBadge } from '@/lib/utils'
import Link from 'next/link'

export default function DashboardPage() {
  const [jobs, setJobs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.jobs.list().then(setJobs).catch(console.error).finally(() => setLoading(false))
  }, [])

  const completed = jobs.filter(j => j.status === 'completed')
  const avgScore = completed.length > 0
    ? (completed.reduce((s, j) => s + (j.compliance_score || 0), 0) / completed.length).toFixed(1)
    : null
  const totalViolations = completed.reduce((s, j) => s + j.total_violations, 0)
  const criticalViolations = completed.reduce((s, j) => s + j.critical_violations, 0)

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Accessibility Audit Dashboard</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Sites Audited', value: completed.length, color: 'bg-indigo-500' },
          { label: 'Avg Compliance Score', value: avgScore ? `${avgScore}%` : '—', color: 'bg-green-500' },
          { label: 'Total Violations', value: totalViolations, color: 'bg-yellow-500' },
          { label: 'Critical Violations', value: criticalViolations, color: 'bg-red-500' },
        ].map(card => (
          <div key={card.label} className="bg-white rounded-lg shadow p-5">
            <div className={`text-3xl font-bold text-white ${card.color} rounded-md px-3 py-2 inline-block mb-2`}>{card.value}</div>
            <p className="text-sm text-gray-600 mt-1">{card.label}</p>
          </div>
        ))}
      </div>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-5 py-4 border-b flex items-center justify-between">
          <h2 className="text-lg font-semibold">Recent Audits</h2>
          <Link href="/jobs" className="text-indigo-600 hover:underline text-sm">New Audit</Link>
        </div>
        {loading ? <div className="text-center py-12 text-gray-500">Loading...</div> : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {['Site', 'URL', 'Score', 'Violations', 'Status'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {jobs.slice(0, 10).map(job => (
                <tr key={job.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium">
                    <Link href={`/jobs/${job.id}`} className="text-indigo-600 hover:underline">
                      {job.site_name || 'Unnamed'}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 max-w-xs truncate">{job.url}</td>
                  <td className={`px-4 py-3 text-sm font-bold ${scoreColor(job.compliance_score)}`}>
                    {job.compliance_score !== null ? `${job.compliance_score}%` : '—'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">{job.total_violations}</td>
                  <td className="px-4 py-3 text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusBadge(job.status)}`}>{job.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
