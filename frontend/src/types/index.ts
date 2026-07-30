export interface AuditJob {
  id: string
  url: string
  site_name: string | null
  status: string
  max_pages: number
  pages_crawled: number
  total_violations: number
  critical_violations: number
  compliance_score: number | null
  error_message: string | null
  created_at: string
}

export interface AuditPage {
  id: string
  job_id: string
  url: string
  title: string | null
  violation_count: number
  critical_count: number
  warning_count: number
  compliance_score: number | null
}

export interface Violation {
  id: string
  page_id: string
  wcag_criterion: string
  wcag_level: string
  severity: string
  description: string
  element: string | null
  fix_suggestion: string | null
}
