'use client'
import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { api } from '@/lib/api'
import { severityBadge, scoreColor } from '@/lib/utils'

export default function JobDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [job, setJob] = useState<any>(null)
  const [pages, setPages] = useState<any[]>([])
  const [selectedPage, setSelectedPage] = useState<any>(null)
  const [violations, setViolations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.jobs.get(id), api.pages.list(id)])
      .then(([j, p]) => { setJob(j); setPages(p) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [id])

  const viewViolations = async (page: any) => {
    setSelectedPage(page)
    const v = await api.pages.violations(page.id).catch(() => [])
    setViolations(v)
  }

  if (loading) return <div className="text-center py-12 text-gray-500">Loading...</div>
  if (!job) return <div className="text-center py-12 text-red-500">Job not found</div>

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{job.site_name || job.url}</h1>
          <p className="text-gray-500 text-sm mt-1">{job.url}</p>
        </div>
        <div className="text-right">
          <div className={`text-4xl font-bold ${scoreColor(job.compliance_score)}`}>
            {job.compliance_score !== null ? `${job.compliance_score}%` : '—'}
          </div>
          <div className="text-sm text-gray-500">Compliance Score</div>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Pages Crawled', value: job.pages_crawled },
          { label: 'Total Violations', value: job.total_violations },
          { label: 'Critical', value: job.critical_violations },
        ].map(card => (
          <div key={card.label} className="bg-white rounded-lg shadow p-4 text-center">
            <div className="text-3xl font-bold text-gray-900">{card.value}</div>
            <div className="text-sm text-gray-500">{card.label}</div>
          </div>
        ))}
      </div>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <h2 className="text-lg font-semibold px-5 py-4 border-b">Pages</h2>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {['URL', 'Title', 'Score', 'Violations', 'Critical', ''].map(h => (
                <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {pages.map(page => (
              <tr key={page.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-700 max-w-xs truncate">{page.url}</td>
                <td className="px-4 py-3 text-sm text-gray-700">{page.title || '—'}</td>
                <td className={`px-4 py-3 text-sm font-bold ${scoreColor(page.compliance_score)}`}>
                  {page.compliance_score !== null ? `${page.compliance_score}%` : '—'}
                </td>
                <td className="px-4 py-3 text-sm text-gray-700">{page.violation_count}</td>
                <td className="px-4 py-3 text-sm font-bold text-red-600">{page.critical_count}</td>
                <td className="px-4 py-3 text-sm">
                  <button onClick={() => viewViolations(page)} className="text-indigo-600 hover:underline text-xs">View Violations</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {selectedPage && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <h2 className="text-lg font-semibold px-5 py-4 border-b">Violations for: {selectedPage.url}</h2>
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {['WCAG', 'Level', 'Severity', 'Description', 'Fix'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {violations.map(v => (
                <tr key={v.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-mono font-bold">{v.wcag_criterion}</td>
                  <td className="px-4 py-3 text-sm">{v.wcag_level}</td>
                  <td className="px-4 py-3 text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${severityBadge(v.severity)}`}>{v.severity}</span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700 max-w-xs">{v.description}</td>
                  <td className="px-4 py-3 text-sm text-gray-600 max-w-xs">{v.fix_suggestion}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {violations.length === 0 && <div className="text-center py-8 text-gray-500">No violations found for this page</div>}
        </div>
      )}
    </div>
  )
}
