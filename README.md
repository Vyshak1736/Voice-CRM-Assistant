# Voice CRM PWA - Django Backend

 **Voice-based Progressive Web Application for sales CRM automation** with Django REST Framework backend.

## Features

- **Voice Recording** - Real-time audio capture with visual feedback
- **Speech-to-Text** - Convert spoken words to text (mock implementation)
- **Data Extraction** - Extract customer details and interaction metadata
- **PWA Support** - Installable on mobile devices with offline support
- **JSON Output** - Structured data ready for CRM integration
- **Admin Interface** - Visual data management
- **Authentication Ready** - Built-in user system

## Tech Stack

### Frontend
- **React 18** - Modern JavaScript framework
- **Progressive Web Application** - Service worker with offline support
- **Web Audio API** - Browser-based recording
- **Tailwind CSS** - Utility-first styling

### Backend
- **Django 4.2.7** - Modern web framework
- **Django REST Framework** - API development
- **SQLite** - Lightweight database
- **Django CORS Headers** - Cross-origin support

## Project Structure

```
├── backend/           # Django backend
│   ├── api/          # API app (models, views, serializers)
│   ├── voice_crm/    # Django project configuration
│   ├── manage.py     # Django management script
│   └── requirements-django-simple.txt
├── demo/             # Standalone HTML demo
│   └── index.html    # Working demo with voice recording
├── frontend/         # React PWA (optional)
│   ├── src/          # React components
│   ├── public/       # PWA manifest and service worker
│   └── package.json  # Dependencies
├── .gitignore        # Git ignore file
└── README.md         # Project documentation
```

## Quick Start

### Backend (Django)
```bash
cd backend
pip install -r requirements-django-simple.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8000
```

### Frontend Demo
```bash
# Open demo/index.html in browser
# No installation required - works immediately
```

### React Frontend (Optional)
```bash
cd frontend
npm install
npm start
```

## Access Points

- **API Base**: `http://localhost:8000/api/`
- **Admin Panel**: `http://localhost:8000/admin/`
- **Demo**: Open `demo/index.html` in browser

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health/` | GET | Health check |
| `/api/transcribe/` | POST | Audio to text conversion |
| `/api/extract/` | POST | Structured data extraction |

## API Usage

### Health Check
```bash
curl http://localhost:8000/api/health/
```

### Data Extraction
```bash
curl -X POST http://localhost:8000/api/extract/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I spoke with customer Amit Verma today. His phone number is 9988776655. He stays in Kolkata."
  }'
```

## Database Models

### Customer
- `full_name` - Customer name
- `phone` - Phone number
- `address` - Street address
- `city` - City name
- `locality` - Area/locality

### Interaction
- `customer` - Foreign key to customer
- `summary` - Interaction summary
- `transcription` - Full transcription text

## Admin Interface

Access the Django admin panel at `http://localhost:8000/admin/` to:
- View and manage customers
- View interaction history
- Manage database records
- Add/edit data manually

## Demo Features

The demo HTML (`demo/index.html`) provides:
-  Voice recording interface
-  Real-time transcription display
-  Structured JSON output
-  Customer information cards
-  Responsive design

## Example Output

```json
{
  "customer": {
    "full_name": "Amit Verma",
    "phone": "9988776655",
    "address": "45 Park Street",
    "city": "Kolkata",
    "locality": "Salt Lake"
  },
  "interaction": {
    "summary": "We discussed demo and next steps",
    "created_at": "2026-01-20T10:30:00Z"
  }
}
```

## Development

### Adding New Features
1. Update models in `backend/api/models.py`
2. Create migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`
4. Update views/serializers as needed

### Custom Styling
- Frontend: Modify `frontend/src/App.css`
- Demo: Modify styles in `demo/index.html`

## License

MIT License

---

**Built with  for sales teams everywhere**