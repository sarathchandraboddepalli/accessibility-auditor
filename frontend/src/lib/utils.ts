export function scoreColor(score: number | null) {
  if (score === null) return 'text-gray-500'
  if (score >= 80) return 'text-green-600'
  if (score >= 60) return 'text-yellow-600'
  return 'text-red-600'
}

export function severityBadge(severity: string) {
  const colors: Record<string, string> = {
    critical: 'bg-red-100 text-red-800',
    serious: 'bg-orange-100 text-orange-800',
    moderate: 'bg-yellow-100 text-yellow-800',
    minor: 'bg-blue-100 text-blue-800',
  }
  return colors[severity] || 'bg-gray-100 text-gray-800'
}

export function statusBadge(status: string) {
  const colors: Record<string, string> = {
    pending: 'bg-gray-100 text-gray-800',
    running: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}
