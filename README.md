# Image Review Portal

A modern web-based content moderation tool that enables content moderators to quickly triage user-uploaded images for potential policy violations using automatic AI-powered labeling.

## Overview

The Image Review Portal is a full-stack application that combines:
- **Backend**: FastAPI gateway that integrates with an image classifier API
- **Frontend**: Modern React application with drag-and-drop image upload
- **Database**: Persistent storage for moderation event logging

## Features

- 🖼️ **Drag-and-Drop Image Upload**: Intuitive interface for uploading images
- 🤖 **AI-Powered Classification**: Automatic image labeling via classifier API
- ⚠️ **Smart Flagging**: Automatic "safe" or "flagged" status based on configurable rules
- 📊 **Moderation History**: View and track all moderated images with timestamps
- 🎨 **Modern UI**: Beautiful, responsive design with real-time feedback
- 🐳 **Docker Support**: Easy deployment with Docker Compose

## Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Frontend   │─────▶│   Backend   │─────▶│ Classifier  │
│  (React)    │      │  (FastAPI)  │      │    API      │
└─────────────┘      └─────────────┘      └─────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │  Database   │
                     │  (SQLite)   │
                     └─────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker Compose

1. **Update the classifier service** in `docker-compose.yml` with your actual classifier image:
   ```yaml
   classifier:
     image: your-classifier-image:latest
   ```

2. **Start all services**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001
   - Classifier API: http://localhost:8000

### Local Development

#### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Configuration

### Environment Variables

**Backend**:
- `CLASSIFIER_API_URL`: URL of the classifier API (default: `http://localhost:8000/classify`)
- `DATABASE_URL`: Database connection string (default: `sqlite:///./moderation.db`)
- `FLAGGED_CLASSES`: Comma-separated list of classes that should be flagged (default: `inappropriate,nsfw,violence`)

**Frontend**:
- `VITE_API_URL`: Backend API URL (default: `http://localhost:8001`)

## API Endpoints

### `POST /moderate`
Upload an image for moderation.

**Request**: Multipart form data with `file` field

**Response**:
```json
{
  "id": 1,
  "filename": "image.jpg",
  "label": "landscape",
  "confidence": 0.95,
  "status": "safe",
  "timestamp": "2024-02-03T10:30:00"
}
```

### `GET /history?limit=50&offset=0`
Get moderation history with pagination.

**Response**:
```json
{
  "events": [...],
  "total": 100
}
```

### `GET /health`
Health check endpoint.

## How It Works

1. **Image Upload**: Moderator uploads an image via drag-and-drop or file selection
2. **Classification**: Backend forwards the image to the classifier API
3. **Rule Application**: Backend applies configured rules to determine "safe" or "flagged" status
4. **Storage**: Moderation event is logged to the database
5. **Display**: Results are shown immediately with thumbnail, label, confidence, and status
6. **History**: All moderation events are tracked and displayed in the history table

## Moderation Rules

Images are automatically flagged if their predicted label contains any of the configured flagged classes (case-insensitive). For example:
- Label: "inappropriate_content" → Status: **flagged**
- Label: "nsfw_image" → Status: **flagged**
- Label: "landscape" → Status: **safe**

## Database Schema

```sql
CREATE TABLE moderation_events (
    id INTEGER PRIMARY KEY,
    filename VARCHAR,
    label VARCHAR,
    confidence FLOAT,
    status VARCHAR,  -- "safe" or "flagged"
    timestamp DATETIME,
    image_path VARCHAR
);
```

## Development

### Project Structure

```
image-review-portal/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Backend container
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main React component
│   │   ├── App.css          # Styles
│   │   └── main.tsx         # Entry point
│   ├── package.json         # Node dependencies
│   └── Dockerfile           # Frontend container
├── docker-compose.yml       # Multi-container setup
└── README.md               # This file
```

## License

MIT

## Support

For issues and questions, please open an issue on the repository.

