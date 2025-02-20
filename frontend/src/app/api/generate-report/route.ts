import { NextResponse } from 'next/server'
import type { ResearchRequest } from '@/types/research'

export async function POST(request: Request) {
  try {
    const body: ResearchRequest = await request.json()
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    
    console.log('Sending request to:', `${apiUrl}/api/generate-report`)
    console.log('Request body:', JSON.stringify(body, null, 2))
    
    const response = await fetch(`${apiUrl}/api/generate-report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
      body: JSON.stringify(body),
      cache: 'no-store',
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('API Error:', {
        status: response.status,
        statusText: response.statusText,
        error: errorText
      })
      throw new Error(`API error: ${response.status} ${errorText}`)
    }

    const data = await response.json()
    console.log('Response received successfully')
    return NextResponse.json(data)
  } catch (error: any) {
    console.error('Error details:', {
      name: error?.name || 'Unknown Error',
      message: error?.message || 'Unknown error occurred',
      stack: error?.stack || 'No stack trace available'
    })
    return NextResponse.json(
      { error: '生成报告时出错，请确保后端服务正在运行' },
      { status: 500 }
    )
  }
} 