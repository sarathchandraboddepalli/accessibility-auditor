const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

export const api = {
  jobs: {
    list: () => apiFetch<any[]>('/api/v1/jobs/'),
    create: (data: any) => apiFetch<any>('/api/v1/jobs/', { method: 'POST', body: JSON.stringify(data) }),
    get: (id: string) => apiFetch<any>(`/api/v1/jobs/${id}`),
  },
  pages: {
    list: (jobId: string) => apiFetch<any[]>(`/api/v1/pages/job/${jobId}`),
    violations: (pageId: string) => apiFetch<any[]>(`/api/v1/pages/${pageId}/violations`),
  },
}
