import { Component, ErrorInfo, ReactNode } from 'react';
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(_: Error): State {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center min-h-screen p-4">
          <div className="max-w-md w-full">
            <Alert variant="destructive">
              <AlertTitle className="text-xl font-bold mb-2">出现了一些问题</AlertTitle>
              <AlertDescription className="text-sm mb-4">
                应用程序遇到了未预期的错误。请尝试刷新页面。
              </AlertDescription>
              <Button 
                className="mt-4 w-full"
                onClick={() => this.setState({ hasError: false })}>
                <RefreshCw className="mr-2 h-4 w-4" /> 重试
              </Button>
            </Alert>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}