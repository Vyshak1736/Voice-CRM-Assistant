import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Square, AlertCircle } from 'lucide-react';

const VoiceRecorder = ({ isRecording, setIsRecording, onTranscriptionComplete }) => {
  const [audioURL, setAudioURL] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const timerRef = useRef(null);

  const startRecording = async () => {
    try {
      setError(''); // Clear any previous errors
      setRecordingTime(0);
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: true
      });
      
      streamRef.current = stream;
      
      // Try to use webm with opus codec, fallback to default webm (like demo)
      let selectedMimeType = 'audio/webm;codecs=opus';
      if (!MediaRecorder.isTypeSupported(selectedMimeType)) {
        selectedMimeType = 'audio/webm';
      }
      if (!MediaRecorder.isTypeSupported(selectedMimeType)) {
        selectedMimeType = 'audio/ogg';
      }
      
      console.log('Using MIME type:', selectedMimeType);
      
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: selectedMimeType
      });
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        console.log('Audio chunk available, size:', event.data.size, 'type:', event.data.type);
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        try {
          console.log('Recording stopped, processing audio...');
          console.log('Audio chunks collected:', audioChunksRef.current.length);
          
          // Create blob exactly like demo
          const audioBlob = new Blob(audioChunksRef.current, { 
            type: selectedMimeType 
          });
          
          console.log('Audio blob created:', audioBlob);
          console.log('Blob size:', audioBlob.size, 'bytes');
          console.log('Blob type:', audioBlob.type);
          
          const audioUrl = URL.createObjectURL(audioBlob);
          setAudioURL(audioUrl);
          
          // Stop all tracks (like demo)
          stream.getTracks().forEach(track => track.stop());
          
          // Send to backend for transcription (like demo)
          await transcribeAudio(audioBlob);
          
        } catch (error) {
          console.error('Error processing audio:', error);
          setError('Failed to process audio recording');
          setIsProcessing(false);
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      console.log('MediaRecorder started');
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setError('Please allow microphone access to use this feature.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      console.log('Stopping MediaRecorder');
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsProcessing(true);
      
      // Clear timer
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  };

  const transcribeAudio = async (audioBlob) => {
    try {
      console.log('Starting transcription...');
      setError(''); // Clear any previous errors
      
      const formData = new FormData();
      
      formData.append('audio', audioBlob, 'recording.webm');
      
      const url = 'http://127.0.0.1:8000/api/transcribe/';
      console.log('=== Calling transcription URL:', url);
      console.log('Blob type:', audioBlob.type);
      console.log('Blob size:', audioBlob.size);
      
      let response = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      console.log('Response status:', response.status);
      console.log('Response URL:', response.url);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Response error text:', errorText);
        throw new Error(`Transcription failed: ${response.status} ${errorText}`);
      }

      const result = await response.json();
      console.log('Transcription result:', result);
      onTranscriptionComplete(result.transcription);
      
    } catch (error) {
      console.error('Error transcribing audio:', error);
      setError(`Failed to transcribe audio: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isRecording]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col items-center space-y-4">
        <div className="relative">
          <button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isProcessing}
            className={`p-6 rounded-full transition-all duration-200 ${
              isRecording 
                ? 'bg-red-500 hover:bg-red-600 recording-indicator' 
                : 'bg-blue-500 hover:bg-blue-600'
            } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isRecording ? (
              <Square className="w-8 h-8 text-white" />
            ) : (
              <Mic className="w-8 h-8 text-white" />
            )}
          </button>
          
          {isRecording && (
            <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-red-500 font-medium">Recording {formatTime(recordingTime)}</span>
              </div>
            </div>
          )}
        </div>

        {isRecording && (
          <div className="audio-visualizer">
            {[...Array(5)].map((_, i) => (
              <div 
                key={i} 
                className="audio-bar"
                style={{
                  animationDelay: `${i * 0.1}s`,
                  height: `${20 + Math.random() * 30}px`
                }}
              ></div>
            ))}
          </div>
        )}

        <div className="text-center">
          <p className="text-gray-600">
            {isProcessing ? 'Processing audio...' : 
             isRecording ? 'Speak clearly into your microphone' :
             'Click the microphone to start recording'}
          </p>
        </div>

        {error && (
          <div className="flex items-center space-x-2 text-red-500 bg-red-50 p-3 rounded-lg">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">{error}</span>
          </div>
        )}
      </div>

      {audioURL && !isRecording && (
        <div className="mt-6">
          <audio controls className="w-full" src={audioURL}>
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
    </div>
  );
};

export default VoiceRecorder;
