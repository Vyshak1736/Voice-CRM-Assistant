# Voice-Based CRM PWA

A Progressive Web Application that converts sales representatives' voice input into structured CRM data using speech-to-text and NLP extraction.

## Features

- Voice recording and transcription
- Structured data extraction (customer details, interaction metadata)
- PWA with offline support
- Android APK generation via Trusted Web Activity
- Evaluation dashboard with test results
- REST API backend

## Tech Stack

### Frontend
- React (Web)
- Progressive Web Application
- Web Speech API / Whisper
- Tailwind CSS
- Service Worker

### Backend
- Python FastAPI
- OpenAI GPT / Local LLM for data extraction
- Whisper for speech-to-text
- SQLite/PostgreSQL

## Project Structure

```
├── frontend/          # React PWA
├── backend/           # FastAPI backend
├── apk-generator/     # Android APK build scripts
├── evaluation/        # Test results and dashboard
└── docs/             # Documentation
```

## Quick Start

### Frontend
```bash
cd frontend
npm install
npm start
```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### APK Generation
```bash
cd apk-generator
./build-apk.sh
```

## API Endpoints

- `POST /api/transcribe` - Convert speech to text
- `POST /api/extract` - Extract structured data from text
- `GET /api/health` - Health check

## Evaluation

Access the evaluation dashboard at `/evaluation` to view test results and performance metrics.
