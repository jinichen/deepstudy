'use client';

import { useState } from 'react';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import ResearchForm from '@/components/ResearchForm';
import ResearchReport from '@/components/ResearchReport';
import { ErrorDisplay } from '@/components/ErrorDisplay';
import { ResearchResponse, ResearchRequest } from '@/types/research';

export default function Home() {
  const [report, setReport] = useState<ResearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: ResearchRequest) => {
    setLoading(true);
    setError(null);
    try {
      console.log('Submitting research request:', data);
      const response = await fetch('/api/generate-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || '生成报告时出错，请重试');
      }
      
      const result = await response.json();
      console.log('Received report:', result);
      setReport(result);
    } catch (error) {
      console.error('Error:', error);
      setError(error instanceof Error ? error.message : '生成报告时出错，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ErrorBoundary>
      <main className="min-h-screen bg-background">
        <div className="max-w-7xl mx-auto p-4">
          {error && (
            <ErrorDisplay 
              message={error}
              onClose={() => setError(null)}
            />
          )}
          
          {!report && (
            <div className="space-y-8 py-8 px-4">
              <div className="text-center space-y-4">
                <h2 className="text-2xl font-bold text-foreground">
                  今天想研究什么主题？
                </h2>
                <p className="text-muted-foreground">
                  输入你感兴趣的研究主题
                </p>
              </div>
              
              <div className="max-w-2xl mx-auto">
                <ResearchForm 
                  onSubmit={handleSubmit}
                  loading={loading}
                />
              </div>
            </div>
          )}
          
          {report && (
            <ResearchReport 
              report={report} 
              onBack={() => {
                setReport(null);
                setError(null);
              }}
            />
          )}
        </div>
      </main>
    </ErrorBoundary>
  );
}