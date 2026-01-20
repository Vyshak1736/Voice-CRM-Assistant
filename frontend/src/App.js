import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Mic, MicOff, FileText, Settings, BarChart3 } from 'lucide-react';
import VoiceRecorder from './components/VoiceRecorder';
import TranscriptionDisplay from './components/TranscriptionDisplay';
import JsonOutput from './components/JsonOutput';
import EvaluationDashboard from './components/EvaluationDashboard';
import './App.css';

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [extractedData, setExtractedData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Register service worker for PWA
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then(registration => console.log('SW registered'))
        .catch(error => console.log('SW registration failed'));
    }
  }, []);

  const handleTranscriptionComplete = async (text) => {
    setTranscription(text);
    setIsLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/extract', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });
      
      const data = await response.json();
      setExtractedData(data);
    } catch (error) {
      console.error('Error extracting data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-bold text-gray-800">Voice CRM Assistant</h1>
              </div>
              <div className="flex items-center space-x-4">
                <Link to="/" className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-gray-900">
                  <FileText className="w-4 h-4 mr-2" />
                  Record
                </Link>
                <Link to="/evaluation" className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-gray-900">
                  <BarChart3 className="w-4 h-4 mr-2" />
                  Evaluation
                </Link>
              </div>
            </div>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={
            <main className="max-w-4xl mx-auto py-8 px-4">
              <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                <h2 className="text-2xl font-semibold mb-4">Voice Recording</h2>
                <VoiceRecorder
                  isRecording={isRecording}
                  setIsRecording={setIsRecording}
                  onTranscriptionComplete={handleTranscriptionComplete}
                />
              </div>

              {transcription && (
                <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                  <h3 className="text-xl font-semibold mb-4">Transcription</h3>
                  <TranscriptionDisplay text={transcription} />
                </div>
              )}

              {isLoading && (
                <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <span className="ml-3">Extracting structured data...</span>
                  </div>
                </div>
              )}

              {extractedData && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-xl font-semibold mb-4">Extracted Data</h3>
                  <JsonOutput data={extractedData} />
                </div>
              )}
            </main>
          } />
          
          <Route path="/evaluation" element={<EvaluationDashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
