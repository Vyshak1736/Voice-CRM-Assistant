from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from django.http import HttpResponse
from .models import Customer, Interaction, TestResult
from .serializers import CustomerSerializer, InteractionSerializer, TestResultSerializer
from .utils import DataExtractor, EvaluationManager
import re
import json
import os
import tempfile
import whisper
from datetime import datetime
import pydub
from pydub import AudioSegment
import pandas as pd


class HealthView(APIView):
    """Health check endpoint"""
    def get(self, request):
        return Response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "framework": "Django REST Framework"
        })


class TranscriptionView(APIView):
    """
    Transcribe audio to text using OpenAI Whisper
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        audio_file = request.FILES.get("audio")

        if not audio_file:
            return Response(
                {"error": "Audio file is required. Use form-data with key 'audio'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        temp_path = None

        try:
            # Determine file extension
            original_name = audio_file.name.lower()
            if original_name.endswith((".webm", ".weba")):
                suffix = ".webm"
            elif original_name.endswith(".wav"):
                suffix = ".wav"
            elif original_name.endswith(".mp3"):
                suffix = ".mp3"
            elif original_name.endswith(".m4a"):
                suffix = ".m4a"
            else:
                return Response(
                    {"error": "Unsupported audio format"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Save uploaded file
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                for chunk in audio_file.chunks():
                    temp_file.write(chunk)
                temp_file.flush()  # Ensure data is written to disk
                temp_path = temp_file.name

            # Validate saved file
            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                return Response(
                    {"error": "Uploaded file is empty or invalid"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            print(f"Processing audio file: {temp_path}")
            print(f"File size: {os.path.getsize(temp_path)} bytes")
            
            # Wait a moment for file system to sync
            import time
            time.sleep(0.1)
            
            model = whisper.load_model("base")

            # Try direct transcription first (Whisper handles most formats)
            try:
                print(f"Attempting direct transcription of {temp_path}")
                result = model.transcribe(
                    temp_path,
                    language="en",
                    fp16=False
                )
                print("Transcription successful!")
                    
            except Exception as whisper_error:
                print(f"Whisper transcription failed: {whisper_error}")
                import traceback
                traceback.print_exc()
                
                # Check if it's an FFmpeg issue
                error_str = str(whisper_error).lower()
                ffmpeg_keywords = ['ffmpeg', 'pydub.exceptions.AudioProcessingException', 'failed to load audio', 'ffmpeg not found']
                if any(keyword in error_str for keyword in ffmpeg_keywords):
                    print(f"FFmpeg-related error detected: {whisper_error}")
                    return Response(
                        {
                            "error": "Audio processing failed - FFmpeg not installed",
                            "details": "Please install FFmpeg. See AUDIO_PROCESSING_FIX.md for instructions.",
                            "help": "Windows: choco install ffmpeg | Mac: brew install ffmpeg | Linux: sudo apt-get install ffmpeg"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                return Response(
                    {
                        "error": "Audio processing failed", 
                        "details": str(whisper_error)
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            transcription = result.get("text", "").strip()

            if not transcription:
                print("No speech detected in audio - transcription result is empty")
                return Response(
                    {"error": "No speech detected in audio", "details": "Please speak clearly and record for at least 2-3 seconds"},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )

            return Response(
                {"transcription": transcription},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "error": "Transcription failed",
                    "details": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        finally:
            # Cleanup temp file
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)


class ExtractionView(APIView):
    """Extract structured data from text endpoint"""
    parser_classes = [JSONParser]
    
    def __init__(self):
        self.extractor = DataExtractor()
    
    def post(self, request):
        try:
            text = request.data.get('text', '')
            if not text:
                return Response(
                    {"error": "No text provided"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Extract customer data using enhanced extractor
            extracted_data = self.extractor.extract_customer_data(text)
            
            # Save to database
            customer_data = {k: v for k, v in extracted_data['customer'].items() if v}
            customer = Customer.objects.create(**customer_data)
            
            interaction_data = extracted_data['interaction']
            interaction = Interaction.objects.create(
                customer=customer,
                summary=interaction_data['summary'],
                transcription=text
            )
            
            # Return structured data
            response_data = {
                "customer": CustomerSerializer(customer).data,
                "interaction": {
                    "summary": interaction.summary,
                    "created_at": interaction.created_at.isoformat()
                },
                "confidence_scores": extracted_data.get('confidence_scores', {})
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def extract_customer_data(self, text):
        """Extract structured customer data from text using regex patterns"""
        
        # Initialize result
        result = {
            "customer": {
                "full_name": "",
                "phone": "",
                "address": "",
                "city": "",
                "locality": ""
            },
            "interaction": {
                "summary": "",
                "created_at": datetime.now().isoformat()
            }
        }
        
        # Extract name (simple pattern for "customer X" or "X called")
        name_patterns = [
            r'customer\s+([A-Za-z]+\s+[A-Za-z]+)',
            r'([A-Za-z]+\s+[A-Za-z]+)\s+called',
            r'spoke\s+with\s+([A-Za-z]+\s+[A-Za-z]+)',
            r'met\s+with\s+([A-Za-z]+\s+[A-Za-z]+)',
            r'called\s+([A-Za-z]+\s+[A-Za-z]+)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["customer"]["full_name"] = match.group(1).strip()
                break
        
        # Extract phone number (Indian format)
        phone_patterns = [
            r'phone\s+(?:number\s+)?([0-9\s]{10,15})',
            r'number\s+is\s+([0-9\s]{10,15})',
            r'contact\s+([0-9\s]{10,15})',
            r'([0-9]{10})',
            r'([0-9\s]{10})'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                phone = re.sub(r'\s', '', match.group(1))
                if len(phone) >= 10:
                    result["customer"]["phone"] = phone[-10:]  # Take last 10 digits
                    break
        
        # Extract address
        address_patterns = [
            r'at\s+([0-9]+\s+[^,]+)',
            r'address\s+is\s+([^,]+)',
            r'located\s+at\s+([^,]+)',
            r'([^,]+\s+(?:Street|Road|Lane|Avenue|Sector|Block))'
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["customer"]["address"] = match.group(1).strip()
                break
        
        # Extract city
        city_patterns = [
            r'in\s+([A-Za-z]+)[,.]',
            r'([A-Za-z]+)\s+city',
            r'([A-Za-z]+)\s+area'
        ]
        
        # Common Indian cities
        indian_cities = ['mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'kolkata', 'pune', 
                        'ahmedabad', 'jaipur', 'surat', 'lucknow', 'kanpur', 'nagpur', 'indore', 
                        'thane', 'bhopal', 'visakhapatnam', 'pimpri', 'patna', 'vadodara', 'ghaziabad',
                        'ludhiana', 'agra', 'nashik', 'faridabad', 'meerut', 'rajkot', 'kalyan',
                        'vasai', 'varanasi', 'srinagar', 'aurangabad', 'dhanbad', 'amritsar',
                        'navi mumbai', 'allahabad', 'ranchi', 'howrah', 'coimbatore', 'jabalpur',
                'gwalior', 'vijayawada', 'jodhpur', 'madurai', 'raipur', 'kota', 'chandigarh',
                'guwahati', 'solapur', 'hubli', 'tiruchirappalli', 'bareilly', 'mysore',
                'tirupur', 'gurgaon', 'aligarh', 'jalandhar', 'bhubaneswar', 'salem',
                'mira', 'thane', 'mathura', 'bhiwandi', 'saharanpur', 'gorakhpur',
                'bikaner', 'amravati', 'noida', 'jamshedpur', 'bhilai', 'cuttack',
                'firozabad', 'kochi', 'nellore', 'bhavnagar', 'tirupati', 'kurnool',
                'rajahmundry', 'tumkur', 'kishanganj', 'erode', 'bokaro', 'south dumdum',
                'bellary', 'patiala', 'gurgaon', 'noida', 'faridabad', 'ghaziabad']
        
        # First try specific patterns
        for pattern in city_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                city = match.group(1).strip().lower()
                if city in indian_cities or len(city) > 3:
                    result["customer"]["city"] = city.title()
                    break
        
        # If no pattern matched, try to find any Indian city in text
        if not result["customer"]["city"]:
            text_lower = text.lower()
            for city in indian_cities:
                if city in text_lower:
                    result["customer"]["city"] = city.title()
                    break
        
        # Extract locality/area
        locality_patterns = [
            r'([A-Za-z]+\s+(?:Layout|Colony|Nagar|Enclave|Park|Garden|Hills|Lake|Circle|Square))',
            r'([A-Za-z]+\s+(?:Sector|Block|Phase|Zone))',
            r'in\s+([A-Za-z]+\s+(?:Layout|Colony|Nagar))'
        ]
        
        for pattern in locality_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["customer"]["locality"] = match.group(1).strip()
                break
        
        # Extract interaction summary (everything after key phrases)
        summary_patterns = [
            r'(?:discussed|talked about|we|they)\s+(.+)',
            r'(?:next steps|follow up|meeting|demo|pricing|contract|agreement)\s*(.+)',
            r'(?:interested in|wants to|needs to|will)\s+(.+)'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                summary = match.group(1).strip()
                # Clean up summary
                summary = re.sub(r'\.+$', '', summary)  # Remove trailing periods
                result["interaction"]["summary"] = summary
                break
        
        return result


class EvaluationResultsView(APIView):
    """Get evaluation results endpoint"""
    
    def get(self, request):
        try:
            results = TestResult.objects.all()
            serializer = TestResultSerializer(results, many=True)
            
            # Calculate statistics
            total_tests = results.count()
            passed_tests = results.filter(passed=True).count()
            failed_tests = total_tests - passed_tests
            accuracy = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            stats = {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "accuracy": round(accuracy, 1)
            }
            
            return Response({
                "stats": stats,
                "results": serializer.data
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DebugAudioView(APIView):
    """Debug endpoint for audio processing testing"""
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        try:
            audio_file = request.FILES.get('audio')
            if not audio_file:
                return Response(
                    {"error": "No audio file provided"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            
            
            debug_info = {
                "file_info": {
                    "name": audio_file.name,
                    "size": audio_file.size,
                    "content_type": audio_file.content_type
                },
                "processing_steps": []
            }
            
            # Save to temp file
            suffix = '.webm' if audio_file.name.lower().endswith('.webm') or audio_file.name.lower().endswith('.weba') else '.wav'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                for chunk in audio_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            debug_info["processing_steps"].append(f"Saved to: {temp_file_path}")
            
            # Check file exists
            if os.path.exists(temp_file_path):
                debug_info["processing_steps"].append(f"✅ File exists, size: {os.path.getsize(temp_file_path)} bytes")
            else:
                debug_info["processing_steps"].append("❌ File not found")
                return Response(debug_info)
            
            # Try to load with pydub
            try:
                audio = AudioSegment.from_file(temp_file_path)
                debug_info["processing_steps"].append(f"✅ Loaded with pydub")
                debug_info["audio_info"] = {
                    "duration_seconds": len(audio) / 1000.0,
                    "channels": audio.channels,
                    "frame_rate": audio.frame_rate,
                    "sample_width": audio.sample_width
                }
                
                # Try conversion
                wav_path = temp_file_path.rsplit('.', 1)[0] + '.wav'
                audio = audio.set_channels(1)
                audio = audio.set_frame_rate(16000)
                audio.export(wav_path, format='wav', parameters=['-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1'])
                
                if os.path.exists(wav_path):
                    debug_info["processing_steps"].append(f"✅ Converted to WAV: {os.path.getsize(wav_path)} bytes")
                    os.unlink(wav_path)
                else:
                    debug_info["processing_steps"].append("❌ WAV conversion failed")
                    
            except Exception as e:
                debug_info["processing_steps"].append(f"❌ Pydub error: {str(e)}")
            
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            
            return Response(debug_info)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EvaluationRunView(APIView):
    """Run evaluation tests endpoint"""
    
    def __init__(self):
        self.evaluation_manager = EvaluationManager()
    
    def post(self, request):
        try:
            # Run comprehensive evaluation
            evaluation_results = self.evaluation_manager.run_evaluation()
            
            return Response({
                "message": f"Evaluation completed. {evaluation_results['passed_tests']}/{evaluation_results['total_tests']} tests passed.",
                "accuracy": evaluation_results['accuracy'],
                "total_tests": evaluation_results['total_tests'],
                "passed_tests": evaluation_results['passed_tests'],
                "failed_tests": evaluation_results['failed_tests'],
                "results": evaluation_results['results']
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """Export evaluation results to Excel"""
        try:
            filename = self.evaluation_manager.export_to_excel()
            if filename:
                return Response({
                    "message": "Evaluation results exported successfully",
                    "filename": filename
                })
            else:
                return Response(
                    {"error": "Failed to export results"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
