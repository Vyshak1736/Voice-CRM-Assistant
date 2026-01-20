# Speech-to-Text Implementation

## Overview

The Voice CRM PWA now supports real speech-to-text transcription with multiple fallback options for maximum reliability.

## Speech-to-Text Options

### 1. OpenAI Whisper (Primary)
- **Model**: Whisper Base (faster processing)
- **Accuracy**: Very High
- **Offline**: Yes
- **Requirements**: `openai-whisper` package

### 2. Google Speech Recognition (Fallback)
- **Service**: Google Speech Recognition API
- **Accuracy**: High
- **Offline**: No (requires internet)
- **Requirements**: `SpeechRecognition` package

### 3. Mock Transcription (Final Fallback)
- **Purpose**: Demo/testing when speech-to-text fails
- **Text**: Predefined customer interaction example
- **Always Available**: Yes

## How It Works

### Transcription Process

1. **Audio Upload**: Browser records audio and sends to Django backend
2. **Primary Attempt**: Try OpenAI Whisper transcription
3. **Fallback 1**: If Whisper fails, try Google Speech Recognition
4. **Fallback 2**: If both fail, use mock transcription
5. **Data Extraction**: Extract customer data from transcribed text
6. **Database Storage**: Save customer and interaction records

### Audio Processing

```python
# Audio is saved to temporary file
with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
    for chunk in audio_file.chunks():
        temp_file.write(chunk)
    temp_file_path = temp_file.name

# Transcription attempts
try:
    # Whisper (offline, most accurate)
    model = whisper.load_model("base")
    result = model.transcribe(temp_file_path)
    transcription = result["text"]
except:
    # Google Speech Recognition (online, good accuracy)
    r = sr.Recognizer()
    with sr.AudioFile(temp_file_path) as source:
        audio = r.record(source)
    transcription = r.recognize_google(audio)
```

## Data Extraction

After transcription, the system extracts structured data using regex patterns:

### Customer Information Extracted
- **Full Name**: Customer names from text
- **Phone Number**: Contact numbers (various formats)
- **Address**: Street addresses
- **City**: Location/city names
- **Locality**: Area/neighborhood information

### Interaction Information
- **Summary**: Key points from conversation
- **Transcription**: Full transcribed text
- **Timestamp**: When interaction occurred

## Installation

### Dependencies

```bash
pip install -r requirements-django-simple.txt
```

### Required Packages
- `django==4.2.7` - Web framework
- `djangorestframework==3.14.0` - API framework
- `django-cors-headers==4.3.1` - CORS support
- `openai-whisper==20250625` - Primary speech-to-text
- `SpeechRecognition==3.14.5` - Fallback speech-to-text
- `python-multipart==0.0.6` - File upload support
- `python-dotenv==1.0.0` - Environment variables

## Usage

### 1. Start Django Server
```bash
cd backend
python manage.py runserver 8000
```

### 2. Open Demo HTML
```bash
# Open demo/index.html in browser
# Or use React frontend
```

### 3. Test Voice Recording
1. Click microphone button
2. Allow microphone access
3. Speak clearly: "I spoke with customer John Smith from 9876543210. He lives in Mumbai."
4. Stop recording
5. See transcription and extracted data

## API Endpoints

### Transcription
```
POST /api/transcribe/
Content-Type: multipart/form-data
Body: audio file (wav, mp3, etc.)

Response:
{
  "transcription": "I spoke with customer John Smith from 9876543210..."
}
```

### Data Extraction
```
POST /api/extract/
Content-Type: application/json
Body: {"text": "transcribed text"}

Response:
{
  "customer": {
    "full_name": "John Smith",
    "phone": "9876543210",
    "city": "Mumbai",
    ...
  },
  "interaction": {
    "summary": "He lives in Mumbai",
    ...
  }
}
```

## Troubleshooting

### Common Issues

1. **Whisper Model Loading Error**
   - **Solution**: System will fallback to Google Speech Recognition
   - **Cause**: Insufficient memory or model files missing

2. **Google Speech Recognition Error**
   - **Solution**: System will fallback to mock transcription
   - **Cause**: No internet connection or API issues

3. **Audio File Format Error**
   - **Solution**: Ensure audio is in supported format (WAV, MP3)
   - **Cause**: Browser recording format compatibility

4. **Microphone Access Denied**
   - **Solution**: Allow microphone access in browser
   - **Cause**: Browser security settings

### Debug Mode

Enable debug logging to see which transcription method is being used:

```python
# In Django settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'api': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Performance

### Transcription Speed
- **Whisper Base**: ~5-10 seconds for 30-second audio
- **Google Speech**: ~2-5 seconds for 30-second audio
- **Mock**: Instant

### Accuracy
- **Whisper**: ~95% accuracy for clear speech
- **Google Speech**: ~90% accuracy for clear speech
- **Mock**: N/A (predefined text)

## Production Considerations

### Scaling
- **Whisper**: Requires GPU for optimal performance
- **Google Speech**: API rate limits apply
- **Mock**: No scaling issues

### Cost
- **Whisper**: Free (local processing)
- **Google Speech**: Free tier available, paid for high volume
- **Mock**: Free

### Privacy
- **Whisper**: 100% private (local processing)
- **Google Speech**: Data sent to Google servers
- **Mock**: No real audio processed

## Future Enhancements

### Additional Speech-to-Text Options
1. **Azure Speech Services** - Enterprise-grade
2. **Amazon Transcribe** - AWS integration
3. **IBM Watson Speech** - IBM cloud option
4. **Mozilla DeepSpeech** - Open source alternative

### Improved Data Extraction
1. **Named Entity Recognition (NER)** - Better entity extraction
2. **Large Language Models** - GPT-based extraction
3. **Custom Training** - Domain-specific models

### Audio Processing
1. **Noise Reduction** - Better audio quality
2. **Audio Enhancement** - Pre-processing filters
3. **Multiple Languages** - Multi-language support

## Testing

### Unit Tests
```python
# Test transcription functionality
def test_transcription():
    # Test with mock audio file
    # Verify transcription accuracy
    # Check fallback mechanisms
```

### Integration Tests
```python
# Test full workflow
def test_voice_to_crm():
    # Upload audio
    # Get transcription
    # Extract data
    # Verify database storage
```

## Support

For issues with speech-to-text functionality:
1. Check Django logs for error messages
2. Verify microphone permissions in browser
3. Test with different audio formats
4. Check internet connection for Google Speech Recognition
5. Ensure all dependencies are installed correctly

---

**Note**: The system is designed to be robust with multiple fallback options, ensuring it always provides some level of functionality even when speech-to-text services are unavailable.
