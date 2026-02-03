# Image Review Portal

A modern, AI-powered web application for content moderation that enables moderators to quickly triage and review user-uploaded images for potential policy violations. Built with FastAPI, React, and deep learning.

## 🎯 Overview

The Image Review Portal is a comprehensive content moderation tool that combines:
- **Deep Learning Classification**: Custom ML model using MobileNetV2 transfer learning
- **Real-time Image Analysis**: Instant classification and flagging of uploaded images
- **Moderation Dashboard**: Beautiful, intuitive interface for content reviewers
- **Event Logging**: Complete audit trail of all moderation decisions
- **Rule-based Flagging**: Configurable rules for automatic content flagging

## ✨ Key Features

### 🖼️ Image Upload & Analysis
- **Drag-and-Drop Interface**: Intuitive file upload with visual feedback
- **Real-time Processing**: Instant image classification upon upload
- **Image Preview**: Thumbnail display with classification results
- **Multiple Format Support**: JPG, PNG, GIF, WebP

### 🤖 AI-Powered Classification
- **Deep Learning Model**: Custom-trained MobileNetV2 model for accurate classification
- **8 Content Categories**:
  - `safe_animal` - Dogs, cats, pets
  - `safe_landscape` - Nature, outdoor scenes
  - `safe_portrait` - People, portraits
  - `safe_food` - Food items
  - `safe_object` - General safe objects
  - `violence_weapon` - Guns, knives, weapons
  - `inappropriate` - NSFW, inappropriate content
  - `violence_blood` - Violent/bloody content
- **Confidence Scores**: Each prediction includes a confidence percentage
- **Fallback Heuristics**: Intelligent fallback when ML model is unavailable

### ⚠️ Smart Content Flagging
- **Automatic Detection**: Images are automatically flagged based on classification
- **Configurable Rules**: Customize which classes trigger flags
- **Safe Label Protection**: Explicit safe labels (portraits, animals, landscapes) are never flagged
- **Conservative Approach**: Defaults to safe when uncertain

### 📊 Moderation Dashboard
- **Real-time Results**: Immediate display of classification results
- **Detailed Information**: Shows filename, predicted label, confidence, and status
- **Visual Status Indicators**: Color-coded badges for safe/flagged status
- **Timestamp Tracking**: Every moderation event is timestamped

### 📜 History & Audit Trail
- **Complete History**: View all moderated images in a searchable table
- **Pagination Support**: Efficient handling of large moderation histories
- **Event Details**: Full information for each moderation event
- **Persistent Storage**: SQLite database for reliable data storage

### 🎨 Modern User Interface
- **Beautiful Design**: Gradient backgrounds, smooth animations, modern UI
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Real-time Feedback**: Loading states, error handling, success messages
- **Accessible**: Clear visual indicators and intuitive navigation

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │  React + TypeScript + Vite
│   (Port 3000)   │  Modern UI with drag-and-drop
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│   Backend       │  FastAPI + Python
│   (Port 8001)   │  Image processing & API
└────────┬────────┘
         │
         ├───▶ ML Classifier (MobileNetV2)
         │     Custom-trained model
         │
         └───▶ SQLite Database
               Event logging & history
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **TensorFlow/Keras**: Deep learning framework for image classification
- **MobileNetV2**: Pre-trained model for transfer learning
- **SQLAlchemy**: Database ORM for data persistence
- **Pillow**: Image processing library
- **NumPy**: Numerical computing

### Frontend
- **React 18**: Modern UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **Axios**: HTTP client for API calls
- **Lucide React**: Beautiful icon library

### Infrastructure
- **Docker**: Containerization for easy deployment
- **Docker Compose**: Multi-container orchestration
- **SQLite**: Lightweight database for development
- **Nginx**: Web server for frontend (production)

## 📁 Project Structure

```
image-review-portal/
├── backend/
│   ├── main.py                 # FastAPI application & API endpoints
│   ├── ml_classifier.py        # ML model wrapper & prediction logic
│   ├── train_model.py          # Model training script
│   ├── setup_training_data.py  # Helper to create data directories
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Backend container definition
│   ├── data/                   # Training data directory
│   │   ├── train/              # Training images by class
│   │   └── validation/        # Validation images by class
│   └── models/                 # Saved ML models
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # Main React component
│   │   ├── App.css             # Component styles
│   │   ├── main.tsx            # Application entry point
│   │   └── index.css           # Global styles
│   ├── package.json            # Node dependencies
│   ├── vite.config.ts          # Vite configuration
│   ├── Dockerfile              # Frontend container definition
│   └── nginx.conf              # Nginx configuration
│
├── docker-compose.yml           # Multi-container setup
├── README.md                    # This file
├── SETUP.md                     # Detailed setup instructions
├── ML_SETUP.md                  # ML model training guide
└── FLAGGING_GUIDE.md            # Content flagging documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ 
- Node.js 18+
- pip and npm

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/VenkataVardineni/image-review-portal.git
cd image-review-portal
```

2. **Set up the backend:**
```bash
cd backend
pip install -r requirements.txt
```

3. **Set up the frontend:**
```bash
cd ../frontend
npm install
```

4. **Start the backend:**
```bash
cd ../backend
MOCK_CLASSIFIER=true python -m uvicorn main:app --reload --port 8001
```

5. **Start the frontend:**
```bash
cd ../frontend
npm run dev
```

6. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

For detailed setup instructions, see [SETUP.md](SETUP.md).

## 🧠 Machine Learning Model

### Model Architecture
- **Base Model**: MobileNetV2 (pre-trained on ImageNet)
- **Transfer Learning**: Custom classification head
- **Input Size**: 224x224 RGB images
- **Output**: 8 classes with confidence scores

### Training the Model
1. Prepare training data (see [ML_SETUP.md](ML_SETUP.md))
2. Run training script:
```bash
cd backend
python train_model.py
```
3. Model saved to `models/image_classifier.h5`

### Using the Model
The model is automatically loaded when `MOCK_CLASSIFIER=true`. It will:
- Classify images into 8 categories
- Provide confidence scores
- Fall back to heuristics if model is unavailable

## 🔌 API Endpoints

### `POST /moderate`
Upload an image for moderation.

**Request**: Multipart form data with `file` field

**Response**:
```json
{
  "id": 1,
  "filename": "image.jpg",
  "label": "safe_portrait",
  "confidence": 0.92,
  "status": "safe",
  "timestamp": "2024-02-03T10:30:00"
}
```

### `GET /history?limit=50&offset=0`
Get moderation history with pagination.

**Response**:
```json
{
  "events": [
    {
      "id": 1,
      "filename": "image.jpg",
      "label": "violence_weapon",
      "confidence": 0.88,
      "status": "flagged",
      "timestamp": "2024-02-03T10:30:00"
    }
  ],
  "total": 100
}
```

### `GET /health`
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "service": "image-review-portal-api"
}
```

## ⚙️ Configuration

### Environment Variables

**Backend:**
- `MOCK_CLASSIFIER`: Enable ML classifier (default: `false`, set to `true` to use)
- `CLASSIFIER_API_URL`: External classifier API URL (default: `http://localhost:8000/classify`)
- `DATABASE_URL`: Database connection string (default: `sqlite:///./moderation.db`)
- `FLAGGED_CLASSES`: Comma-separated flagged classes (default: `inappropriate,nsfw,violence`)
- `MODEL_PATH`: Path to ML model file (default: `./models/image_classifier.h5`)

**Frontend:**
- `VITE_API_URL`: Backend API URL (default: `http://localhost:8001`)

## 🐳 Docker Deployment

### Using Docker Compose

1. **Update classifier service** (if using external classifier):
```yaml
classifier:
  image: your-classifier-image:latest
```

2. **Start all services:**
```bash
docker-compose up -d
```

3. **Access the application:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8001

## 📊 How It Works

1. **Image Upload**: User drags and drops or selects an image file
2. **Image Processing**: Backend receives the image and preprocesses it
3. **ML Classification**: 
   - If ML model is available: Uses trained MobileNetV2 model
   - If model unavailable: Falls back to intelligent heuristics
4. **Rule Application**: Determines "safe" or "flagged" based on:
   - Predicted label (weapons, inappropriate content → flagged)
   - Safe labels (portraits, animals, landscapes → always safe)
   - Configurable flagged classes
5. **Database Storage**: Moderation event saved to SQLite database
6. **Response**: Results displayed immediately with thumbnail, label, confidence, status
7. **History**: Event added to searchable moderation history

## 🔒 Content Flagging Rules

Images are automatically flagged if:
- Label contains flagged keywords: `inappropriate`, `nsfw`, `violence`
- Examples: `violence_weapon`, `inappropriate_content`, `violence_blood`

Images are always safe if:
- Label is explicitly safe: `safe_portrait`, `safe_animal`, `safe_landscape`, `safe_food`, `safe_object`
- Examples: Normal portraits, pet photos, nature scenes

## 📈 Database Schema

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

## 🧪 Development

### Running in Development Mode

**Backend:**
```bash
cd backend
MOCK_CLASSIFIER=true uvicorn main:app --reload --port 8001
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### Building for Production

**Backend:**
```bash
cd backend
docker build -t image-review-backend .
```

**Frontend:**
```bash
cd frontend
npm run build
docker build -t image-review-frontend .
```

## 📝 Documentation

- [SETUP.md](SETUP.md) - Detailed setup and installation guide
- [ML_SETUP.md](ML_SETUP.md) - Machine learning model training guide
- [FLAGGING_GUIDE.md](FLAGGING_GUIDE.md) - Content flagging behavior documentation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 👤 Author

Built as part of the Image Review Portal project.

## 🙏 Acknowledgments

- MobileNetV2 model architecture
- FastAPI framework
- React community
- TensorFlow/Keras for deep learning capabilities
