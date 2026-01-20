import React from 'react';
import { Copy, Check } from 'lucide-react';
import { useState } from 'react';

const TranscriptionDisplay = ({ text }) => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  return (
    <div className="relative">
      <div className="flex justify-between items-start mb-3">
        <h4 className="text-lg font-medium text-gray-800">Transcribed Text</h4>
        <button
          onClick={copyToClipboard}
          className="flex items-center space-x-2 px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4 text-green-600" />
              <span className="text-green-600">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4 text-gray-600" />
              <span className="text-gray-600">Copy</span>
            </>
          )}
        </button>
      </div>
      
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
          {text}
        </p>
      </div>
      
      <div className="mt-3 flex items-center space-x-4 text-sm text-gray-500">
        <span>Word count: {text.split(/\s+/).filter(word => word.length > 0).length}</span>
        <span>Character count: {text.length}</span>
      </div>
    </div>
  );
};

export default TranscriptionDisplay;
