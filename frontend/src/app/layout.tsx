import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI Research Report Generator',
  description: 'Generate comprehensive research reports using AI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh">
      <body>
        {children}
      </body>
    </html>
  )
} 