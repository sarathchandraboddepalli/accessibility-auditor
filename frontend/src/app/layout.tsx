import type { Metadata } from 'next'
import './globals.css'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'GIGW Accessibility Auditor',
  description: 'WCAG 2.1 AA Compliance Scanner for Government Websites',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">
        <nav className="bg-indigo-800 text-white px-6 py-4 flex items-center gap-8">
          <span className="font-bold text-lg">GIGW Accessibility Auditor</span>
          <Link href="/dashboard" className="hover:text-indigo-200 text-sm">Dashboard</Link>
          <Link href="/jobs" className="hover:text-indigo-200 text-sm">Audit Jobs</Link>
          <Link href="/reports" className="hover:text-indigo-200 text-sm">Reports</Link>
        </nav>
        <main className="p-6">{children}</main>
      </body>
    </html>
  )
}
