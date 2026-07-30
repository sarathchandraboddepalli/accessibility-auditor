'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ReportsPage() {
  const [jobs, setJobs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => { api.jobs.list().then(j => setJobs(j.filter((j: any) => j.status === 'completed'))).finally(() => setLoading(false)) }, [])

  return (
    <div className="max-w-7xl mx-auto space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">Audit Reports</h1>
      {loading ? <div className="text-center py-12 text-gray-500">Loading...</div> : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {['Site', 'Score', 'Violations', 'Downloads'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {jobs.map(job => (
                <tr key={job.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">{job.site_name || job.url}</td>
                  <td className="px-4 py-3 text-sm font-bold text-green-600">{job.compliance_score}%</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{job.total_violations}</td>
                  <td className="px-4 py-3 text-sm space-x-3">
                    <a href={`${API_BASE}/api/v1/reports/${job.id}/html`} target="_blank" className="text-indigo-600 hover:underline">HTML</a>
                    <a href={`${API_BASE}/api/v1/reports/${job.id}/pdf`} target="_blank" className="text-indigo-600 hover:underline">PDF</a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {jobs.length === 0 && <div className="text-center py-12 text-gray-500">No completed audits found</div>}
        </div>
      )}
    </div>
  )
}
