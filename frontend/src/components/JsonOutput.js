import React, { useState } from 'react';
import { Copy, Check, Download } from 'lucide-react';

const JsonOutput = ({ data }) => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy JSON:', error);
    }
  };

  const downloadJson = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `crm-data-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const syntaxHighlight = (json) => {
    if (typeof json !== 'string') {
      json = JSON.stringify(json, null, 2);
    }
    
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
      let cls = 'json-number';
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = 'json-key';
        } else {
          cls = 'json-string';
        }
      } else if (/true|false/.test(match)) {
        cls = 'json-boolean';
      } else if (/null/.test(match)) {
        cls = 'json-null';
      }
      return '<span class="' + cls + '">' + match + '</span>';
    });
  };

  return (
    <div className="relative">
      <div className="flex justify-between items-start mb-3">
        <h4 className="text-lg font-medium text-gray-800">Extracted CRM Data</h4>
        <div className="flex space-x-2">
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
          <button
            onClick={downloadJson}
            className="flex items-center space-x-2 px-3 py-1 text-sm bg-blue-100 hover:bg-blue-200 text-blue-600 rounded-md transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Download</span>
          </button>
        </div>
      </div>
      
      <div className="json-output">
        <pre dangerouslySetInnerHTML={{ __html: syntaxHighlight(data) }} />
      </div>
      
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h5 className="font-medium text-blue-800 mb-2">Customer Information</h5>
          <div className="space-y-1 text-sm">
            <p><span className="font-medium">Name:</span> {data.customer?.full_name || 'N/A'}</p>
            <p><span className="font-medium">Phone:</span> {data.customer?.phone || 'N/A'}</p>
            <p><span className="font-medium">Address:</span> {data.customer?.address || 'N/A'}</p>
            <p><span className="font-medium">City:</span> {data.customer?.city || 'N/A'}</p>
            <p><span className="font-medium">Locality:</span> {data.customer?.locality || 'N/A'}</p>
          </div>
        </div>
        
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h5 className="font-medium text-green-800 mb-2">Interaction Details</h5>
          <div className="space-y-1 text-sm">
            <p><span className="font-medium">Summary:</span> {data.interaction?.summary || 'N/A'}</p>
            <p><span className="font-medium">Created:</span> {data.interaction?.created_at ? new Date(data.interaction.created_at).toLocaleString() : 'N/A'}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JsonOutput;
