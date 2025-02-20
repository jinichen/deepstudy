'use client';

import React from 'react';
import { X } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

interface ErrorDisplayProps {
  message: string;
  onClose: () => void;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ message, onClose }) => {
  return (
    <Alert variant="destructive" className="mb-6 relative">
      <AlertTitle className="text-lg">错误</AlertTitle>
      <AlertDescription className="mt-2">{message}</AlertDescription>
      <button 
        onClick={onClose}
        className="absolute top-3 right-3 p-1 rounded-md hover:bg-destructive/20 transition-colors"
        aria-label="关闭"
      >
        <X size={18} />
      </button>
    </Alert>
  );
};