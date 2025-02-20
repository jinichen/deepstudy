declare module 'markdown-to-jsx' {
  import { ComponentType, ReactNode } from 'react'

  interface MarkdownOptions {
    overrides?: {
      [key: string]: {
        component: ComponentType<any>
        props?: Record<string, any>
      }
    }
    wrapper?: ComponentType<any> | string
    forceWrapper?: boolean
    forceBlock?: boolean
    createElement?: typeof React.createElement
    [key: string]: any
  }

  interface MarkdownProps {
    children: string
    options?: MarkdownOptions
    className?: string
  }

  const Markdown: ComponentType<MarkdownProps>
  export default Markdown
} 