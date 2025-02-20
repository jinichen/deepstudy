'use client'

import ReactMarkdown from 'react-markdown'
import { ResearchResponse } from '@/types/research'
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ChevronLeft } from "lucide-react"
import { useEffect, useState } from 'react'

interface ResearchReportProps {
  report: ResearchResponse
  onBack: () => void
}

interface CodeProps {
  inline?: boolean
  children?: React.ReactNode
  className?: string
}

export default function ResearchReport({ report, onBack }: ResearchReportProps) {
  const [showReferences, setShowReferences] = useState(false);
  
  // 检查报告内容中是否已经包含参考文献部分
  useEffect(() => {
    if (!report.detailed_analysis?.full_report) return;
    
    const fullReport = report.detailed_analysis.full_report.toLowerCase();
    const hasReferencesSection = 
      fullReport.includes('# 参考文献') || 
      fullReport.includes('## 参考文献') || 
      fullReport.includes('### 参考文献') ||
      fullReport.includes('## 9. 参考文献') ||  // 添加这个匹配
      fullReport.includes('# 9. 参考文献') ||   // 添加这个匹配
      fullReport.includes('# references') ||
      fullReport.includes('## references') ||
      fullReport.includes('### references') ||
      fullReport.includes('参考资料') ||
      fullReport.includes('引用资料');
    
    setShowReferences(!hasReferencesSection);
  }, [report.detailed_analysis?.full_report]);

  // 在组件中添加日志
  console.log('Received report:', report);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Button
          onClick={onBack}
          variant="outline"
          className="mb-8 flex items-center gap-2"
        >
          <ChevronLeft className="h-4 w-4" />
          返回
        </Button>

        <article className="prose prose-lg dark:prose-invert max-w-none">
          {report.detailed_analysis?.full_report ? (
            <ReactMarkdown
              components={{
                h1: ({node, ...props}) => (
                  <h1 className="text-4xl font-bold mt-16 mb-8 pb-4 border-b text-foreground/90" {...props} />
                ),
                h2: ({node, ...props}) => (
                  <h2 className="text-3xl font-bold mt-12 mb-6 text-foreground/90" {...props} />
                ),
                h3: ({node, ...props}) => (
                  <h3 className="text-2xl font-bold mt-8 mb-4 text-foreground/90" {...props} />
                ),
                p: ({node, ...props}) => (
                  <p className="my-4 leading-7 text-foreground/80 text-justify" {...props} />
                ),
                ul: ({node, ...props}) => (
                  <ul className="my-6 ml-6 list-disc space-y-2" {...props} />
                ),
                ol: ({node, ...props}) => (
                  <ol className="my-6 ml-6 list-decimal space-y-2" {...props} />
                ),
                li: ({node, ...props}) => (
                  <li className="pl-2 text-foreground/80 mb-2" {...props} />
                ),
                blockquote: ({node, ...props}) => (
                  <blockquote className="my-6 pl-6 border-l-4 border-muted italic text-foreground/80" {...props} />
                ),
                // 添加表格支持
                table: ({node, ...props}) => (
                  <div className="overflow-x-auto my-6">
                    <table className="w-full border-collapse" {...props} />
                  </div>
                ),
                thead: ({node, ...props}) => <thead className="bg-muted/50" {...props} />,
                tbody: ({node, ...props}) => <tbody {...props} />,
                tr: ({node, ...props}) => <tr className="border-b border-muted" {...props} />,
                th: ({node, ...props}) => (
                  <th className="px-4 py-2 text-left font-medium text-foreground" {...props} />
                ),
                td: ({node, ...props}) => (
                  <td className="px-4 py-2 text-foreground/80" {...props} />
                ),
                // code: ({inline, className, children, ...props}: CodeProps) => {
                //   const match = /language-(\w+)/.exec(className || '');
                //   return inline ? (
                //     <code className="px-1.5 py-0.5 mx-0.5 bg-muted rounded text-sm font-mono" {...props}>
                //       {children}
                //     </code>
                //   ) : (
                //     <pre className="p-0 my-6 bg-muted rounded-lg overflow-hidden">
                //       <code 
                //         className={`block p-4 text-sm font-mono overflow-x-auto ${match ? `language-${match[1]}` : ''}`} 
                //         {...props}
                //       >
                //         {children}
                //       </code>
                //     </pre>
                //   )
                // },
                strong: ({node, ...props}) => (
                  <strong className="font-bold text-primary" {...props} />
                ),
                em: ({node, ...props}) => (
                  <em className="italic text-purple-600 dark:text-purple-400" {...props} />
                ),
                a: ({node, ...props}) => (
                  <a 
                    className="text-primary hover:text-primary/80 transition-colors underline"
                    target="_blank"
                    rel="noopener noreferrer"
                    {...props}
                  />
                ),
                pre: ({node, ...props}) => (
                  <pre className="whitespace-pre-wrap bg-muted p-4 rounded-lg my-6" {...props} />
                ),
              }}
            >
              {report.detailed_analysis.full_report}
            </ReactMarkdown>
          ) : (
            <div className="text-center text-muted-foreground">
              <p>报告生成中...</p>
            </div>
          )}
        </article>

        <div className="mt-16 space-y-12">
          {report.conclusions && report.conclusions.length > 0 && (
            <section>
              <h2 className="text-3xl font-bold mb-8 text-foreground/90">主要结论</h2>
              <div className="space-y-6">
                {report.conclusions.map((conclusion, index) => (
                  <Card key={index}>
                    <CardContent className="flex items-start gap-6 p-6">
                      <div className="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-full bg-primary/10 text-primary font-medium text-lg">
                        {index + 1}
                      </div>
                      <p className="flex-1 text-foreground/80 text-lg leading-relaxed">{conclusion}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </section>
          )}

          {report.references && report.references.length > 0 && showReferences && (
            <section>
              <h2 className="text-3xl font-bold mb-8 text-foreground/90">参考文献</h2>
              <div className="space-y-4">
                {report.references.map((ref, index) => (
                  <Card key={index} className="group hover:shadow-md transition-shadow">
                    <CardContent className="p-0">
                      <a
                        href={ref.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-6"
                      >
                        <div className="flex items-start gap-6">
                          <span className="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-full bg-primary/10 text-primary font-medium text-lg">
                            {index + 1}
                          </span>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-baseline gap-2">
                              <h3 className="text-lg font-medium text-foreground group-hover:text-primary transition-colors">
                                {ref.title}
                              </h3>
                              {ref.credibility && (
                                <span className="text-sm font-medium text-primary">
                                  (Credibility Score: {ref.credibility.toFixed(1)})
                                </span>
                              )}
                            </div>
                            <div className="mt-2 flex items-center gap-4 text-sm text-muted-foreground">
                              <span className="truncate">{ref.url}</span>
                              {ref.type && (
                                <Badge variant="outline" className="text-xs">
                                  {ref.type}
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                      </a>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  )
}