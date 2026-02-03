# Setup Guide - Image Review Portal

Complete step-by-step guide to set up and run the Image Review Portal application.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **pip** - Usually comes with Python
- **npm** - Comes with Node.js
- **Git** - [Download Git](https://git-scm.com/downloads)

### Verify Installations

```bash
python3 --version  # Should show 3.10 or higher
node --version      # Should show 18.x or higher
npm --version       # Should show 9.x or higher
git --version       # Should show git version
```

## 🚀 Installation Steps

### Step 1: Clone the Repository

```bash
git clone https://github.com/VenkataVardineni/image-review-portal.git
cd image-review-portal
```

### Step 2: Set Up Backend

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create a virtual environment (recommended):**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn (web framework)
- TensorFlow and Keras (ML framework)
- SQLAlchemy (database ORM)
- Pillow and NumPy (image processing)
- Other dependencies

**Note:** TensorFlow installation may take a few minutes.

4. **Verify backend setup:**
```bash
python -c "import fastapi, tensorflow; print('Backend dependencies installed successfully!')"
```

### Step 3: Set Up Frontend

1. **Navigate to frontend directory:**
```bash
cd ../frontend
```

2. **Install Node.js dependencies:**
```bash
npm install
```

This will install:
- React and React DOM
- TypeScript
- Vite (build tool)
- Axios (HTTP client)
- Lucide React (icons)

3. **Verify frontend setup:**
```bash
npm list --depth=0
```

### Step 4: Set Up ML Model (Optional but Recommended)

The application can work with or without a trained ML model. For best results, train the model:

1. **Create training data structure:**
```bash
cd ../backend
python setup_training_data.py
```

This creates directories for:
- `data/train/` - Training images
- `data/validation/` - Validation images
- `models/` - Saved models

2. **Add training images:**
   - Place images in appropriate class folders
   - Example: `data/train/safe_animal/dog1.jpg`
   - Minimum: 50-100 images per class for training

3. **Train the model:**
```bash
python train_model.py
```

Training will:
- Take 10-30 minutes (depending on data size)
- Save model to `models/image_classifier.h5`
- Show training progress and accuracy

**Note:** If you skip training, the app will use heuristics-based classification.

### Step 5: Configure Environment Variables

Create a `.env` file in the backend directory (optional):

```bash
cd backend
touch .env
```

Add configuration (optional - defaults work for development):
```env
MOCK_CLASSIFIER=true
DATABASE_URL=sqlite:///./moderation.db
FLAGGED_CLASSES=inappropriate,nsfw,violence
MODEL_PATH=./models/image_classifier.h5
```

## 🏃 Running the Application

### Option 1: Run Both Services Manually

**Terminal 1 - Backend:**
```bash
cd backend
MOCK_CLASSIFIER=true python -m uvicorn main:app --reload --port 8001
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete.
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

### Option 2: Run with Docker Compose

1. **Update docker-compose.yml** (if using external classifier):
```yaml
classifier:
  image: your-classifier-image:latest
```

2. **Build and start services:**
```bash
docker-compose up --build
```

3. **Access the application:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8001

## ✅ Verify Installation

### 1. Check Backend Health

```bash
curl http://localhost:8001/health
```

Expected response:
```json
{"status":"healthy","service":"image-review-portal-api"}
```

### 2. Check Frontend

Open browser: http://localhost:3000

You should see:
- Image Review Portal header
- Drag-and-drop upload area
- Empty history table

### 3. Test Image Upload

1. Upload a test image (any JPG/PNG)
2. You should see:
   - Image preview
   - Predicted label
   - Confidence score
   - Safe/Flagged status
   - Timestamp

## 🔧 Common Setup Issues

### Issue: Python dependencies fail to install

**Solution:**
```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies one by one
pip install fastapi uvicorn
pip install tensorflow
pip install -r requirements.txt
```

### Issue: TensorFlow installation errors

**Solution:**
- Ensure Python 3.10-3.11 (TensorFlow 2.15 supports these)
- Try: `pip install tensorflow==2.15.0`
- On Apple Silicon: May need additional setup

### Issue: Node modules installation fails

**Solution:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Issue: Port already in use

**Solution:**
```bash
# Find process using port
lsof -i :8001  # Backend
lsof -i :3000  # Frontend

# Kill process or change port
# Backend: Change port in uvicorn command
# Frontend: Change port in vite.config.ts
```

### Issue: ML model not found

**Solution:**
- The app will use heuristics if model is missing
- Train the model: `python train_model.py`
- Or set `MOCK_CLASSIFIER=false` to use external API

### Issue: CORS errors

**Solution:**
- Ensure backend CORS allows frontend origin
- Check `main.py` CORS settings
- Verify frontend is calling correct API URL

## 📦 Production Deployment

### Backend Production Setup

1. **Set environment variables:**
```bash
export MOCK_CLASSIFIER=true
export DATABASE_URL=postgresql://user:pass@localhost/dbname
```

2. **Run with production server:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

### Frontend Production Build

1. **Build for production:**
```bash
cd frontend
npm run build
```

2. **Serve with Nginx:**
```bash
# Copy dist/ to nginx html directory
# Configure nginx.conf
# Start nginx
```

### Docker Production

1. **Build images:**
```bash
docker-compose build
```

2. **Run in detached mode:**
```bash
docker-compose up -d
```

3. **View logs:**
```bash
docker-compose logs -f
```

## 🧪 Testing the Setup

### Test 1: Upload a Safe Image
- Upload a dog photo
- Should classify as `safe_animal`
- Status should be **SAFE**

### Test 2: Upload a Portrait
- Upload a person photo
- Should classify as `safe_portrait`
- Status should be **SAFE**

### Test 3: Check History
- Upload multiple images
- Check history table shows all events
- Verify timestamps and labels

### Test 4: API Endpoints
```bash
# Health check
curl http://localhost:8001/health

# Get history
curl http://localhost:8001/history?limit=10

# Upload image (use Postman or frontend)
```

## 📚 Next Steps

After setup is complete:

1. **Train the ML model** (see [ML_SETUP.md](ML_SETUP.md))
2. **Customize flagged classes** in environment variables
3. **Add more training data** to improve accuracy
4. **Configure production database** (PostgreSQL recommended)
5. **Set up monitoring and logging**

## 🆘 Getting Help

If you encounter issues:

1. Check the logs:
   - Backend: Terminal running uvicorn
   - Frontend: Browser console (F12)
   - Docker: `docker-compose logs`

2. Verify all prerequisites are installed correctly

3. Check environment variables are set correctly

4. Review the [README.md](README.md) for architecture details

5. Open an issue on GitHub with:
   - Error messages
   - Steps to reproduce
   - System information (OS, Python/Node versions)

## ✨ Success!

If you see the Image Review Portal interface and can upload images, your setup is complete! 🎉

Start moderating images and explore the features:
- Upload images via drag-and-drop
- View classification results
- Check moderation history
- Train and improve the ML model

