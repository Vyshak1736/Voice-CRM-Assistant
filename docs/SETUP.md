# Voice CRM PWA - Setup and Installation Guide

## Overview

This guide will help you set up the Voice CRM Progressive Web Application that converts sales representatives' voice input into structured CRM data.

## System Requirements

### Frontend (React PWA)
- Node.js 16+ 
- npm or yarn
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Backend (Python FastAPI)
- Python 3.8+
- pip package manager
- 4GB+ RAM (for ML models)

### APK Generation (Optional)
- Java 8+
- Android SDK
- Bubblewrap CLI (installed via npm)

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Ezy-helpers-project
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Download Language Models
```bash
# Download spaCy English model
python -m spacy download en_core_web_sm

# Whisper will download models automatically on first run
```

#### Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

#### Start Backend Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`

### 3. Frontend Setup

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Start Development Server
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

### 4. Test the Application

1. Open `http://localhost:3000` in your browser
2. Click the microphone button to start recording
3. Speak a customer interaction (e.g., "I spoke with customer Amit Verma today...")
4. View the transcribed text and extracted JSON data
5. Check the evaluation dashboard at `/evaluation`

## Detailed Setup

### Backend Configuration

#### Environment Variables
Create a `.env` file in the backend directory:

```env
# OpenAI API Key (optional - for enhanced NLP)
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///crm_data.db

# Whisper Model Configuration
WHISPER_MODEL=base  # Options: tiny, base, small, medium, large

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### Database Setup
The application uses SQLite by default. The database will be created automatically on first run.

#### Speech-to-Text Models
- **Whisper**: Automatically downloads models on first use
- **spaCy**: Download with `python -m spacy download en_core_web_sm`

### Frontend Configuration

#### PWA Configuration
The PWA is configured in `public/manifest.json` and `public/sw.js`.

#### Tailwind CSS
Tailwind is configured in `tailwind.config.js` and `postcss.config.js`.

### APK Generation (Android App)

#### Prerequisites
1. **Install Java 8+**
   ```bash
   # On macOS
   brew install openjdk@11
   
   # On Ubuntu
   sudo apt update
   sudo apt install openjdk-11-jdk
   ```

2. **Install Android SDK**
   - Download from https://developer.android.com/studio
   - Set ANDROID_HOME environment variable
   ```bash
   export ANDROID_HOME=/path/to/android/sdk
   export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
   ```

3. **Install Bubblewrap CLI**
   ```bash
   npm install -g @bubblewrap/cli
   ```

#### Build APK
```bash
cd apk-generator
chmod +x build-apk.sh
./build-apk.sh
```

The APK will be generated in `./output/VoiceCRM-Debug.apk`

## Testing and Evaluation

### Run Automated Tests
```bash
cd evaluation
pip install -r requirements.txt
python test_runner.py
```

### Test Results
- Results are saved to the database
- Excel export is generated with detailed analysis
- View results in the evaluation dashboard

## API Documentation

### Endpoints

#### Transcribe Audio
```
POST /api/transcribe
Content-Type: multipart/form-data

Response:
{
  "transcription": "Transcribed text here"
}
```

#### Extract Structured Data
```
POST /api/extract
Content-Type: application/json

Request:
{
  "text": "Customer interaction text here"
}

Response:
{
  "customer": {
    "full_name": "John Doe",
    "phone": "1234567890",
    "address": "123 Main St",
    "city": "Mumbai",
    "locality": "Bandra"
  },
  "interaction": {
    "summary": "Discussed product demo",
    "created_at": "2026-01-20T10:30:00Z"
  }
}
```

#### Evaluation Results
```
GET /api/evaluation/results

Response:
{
  "results": [...],
  "stats": {
    "total": 10,
    "passed": 8,
    "failed": 2,
    "accuracy": 80.0
  }
}
```

## Deployment

### Frontend (PWA)
1. Build the production version:
   ```bash
   cd frontend
   npm run build
   ```
2. Deploy the `build` folder to any static hosting service (Vercel, Netlify, etc.)

### Backend (FastAPI)
1. Install production server:
   ```bash
   pip install gunicorn
   ```
2. Run with Gunicorn:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Docker Deployment
```dockerfile
# Dockerfile example
FROM python:3.9-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### Common Issues

#### Backend Issues
- **Model Loading Errors**: Ensure sufficient RAM and disk space
- **CORS Errors**: Check ALLOWED_ORIGINS in environment
- **Database Errors**: Ensure write permissions for database file

#### Frontend Issues
- **Microphone Access**: Enable HTTPS for production
- **PWA Installation**: Check manifest.json configuration
- **Service Worker**: Clear browser cache if issues persist

#### APK Generation Issues
- **Android SDK Path**: Verify ANDROID_HOME environment variable
- **Java Version**: Ensure Java 8+ is installed
- **Bubblewrap Errors**: Check network connectivity for dependencies

### Performance Optimization

#### Backend
- Use GPU for Whisper models if available
- Implement caching for frequent requests
- Use connection pooling for database

#### Frontend
- Implement lazy loading for components
- Optimize bundle size with code splitting
- Use CDN for static assets

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check test results for validation
4. Create GitHub issues for bugs

## License

This project is licensed under the MIT License.
