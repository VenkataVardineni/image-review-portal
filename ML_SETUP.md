# ML Model Setup - Quick Start

## What Changed

The application now uses a **real ML model** (MobileNetV2 with transfer learning) instead of heuristics to classify images. This can accurately distinguish between:
- **Dogs vs Guns** (and other objects)
- **Safe vs Violent/Inappropriate content**

## Quick Setup

### 1. Create Training Data Structure
```bash
cd backend
python setup_training_data.py
```

This creates the directory structure for your training images.

### 2. Add Training Images

Place your images in the created directories:
```
data/train/safe_animal/        # Add dog, cat images here
data/train/violence_weapon/    # Add gun, knife images here
data/train/safe_landscape/     # Add nature images
... (other classes)
```

**Minimum recommended:**
- 50-100 images per class for training
- 20-30 images per class for validation

### 3. Train the Model
```bash
python train_model.py
```

Training will:
- Take 10-30 minutes (depending on data size)
- Save the model to `models/image_classifier.h5`
- Show training progress and accuracy

### 4. Use the Model

The backend automatically uses the ML model when `MOCK_CLASSIFIER=true`:
```bash
MOCK_CLASSIFIER=true python -m uvicorn main:app --reload
```

## Getting Training Data

### Option 1: Use Public Datasets
- **ImageNet**: https://www.image-net.org/
- **Kaggle**: Search for "weapon detection", "dog classification"
- **Google Open Images**: https://storage.googleapis.com/openimages/web/index.html

### Option 2: Collect Your Own
- Use web scraping (respect copyright)
- Take your own photos
- Use stock photo sites

### Option 3: Start Small
- Begin with 20-30 images per class
- Train a basic model
- Add more data iteratively to improve

## Model Architecture

- **Base Model**: MobileNetV2 (pre-trained on ImageNet)
- **Transfer Learning**: Custom classification head
- **Input Size**: 224x224 RGB images
- **Output**: 8 classes with confidence scores

## Testing

Once trained, upload images through the web interface:
- Dog photos → Should classify as `safe_animal`
- Gun photos → Should classify as `violence_weapon`
- Nature photos → Should classify as `safe_landscape`

## Troubleshooting

**Model not found error:**
- Train the model first using `train_model.py`
- Or set `MOCK_CLASSIFIER=false` to use external classifier API

**Low accuracy:**
- Add more training data
- Ensure balanced classes (similar number of images per class)
- Check image quality and diversity

**Training takes too long:**
- Reduce `EPOCHS` in `train_model.py`
- Use smaller batch size
- Reduce image resolution (not recommended)

## Next Steps

1. Collect training data for your use case
2. Train the model
3. Test with real images
4. Iterate and improve!

The model will automatically distinguish between dogs, guns, and other objects once trained.

