# ML Model Training Guide

## Overview

The Image Review Portal now uses a deep learning model (MobileNetV2 with transfer learning) for accurate image classification. The model can distinguish between:
- Safe content (animals, landscapes, portraits, food, objects)
- Violent content (weapons, blood)
- Inappropriate content (NSFW)

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Prepare your training data:**
Create the following directory structure:
```
data/
  train/
    safe_animal/        # Dog, cat, pet images
    safe_landscape/     # Nature, outdoor scenes
    safe_portrait/      # People, portraits
    safe_food/          # Food items
    safe_object/        # General safe objects
    violence_weapon/    # Guns, knives, weapons
    inappropriate/      # NSFW content
    violence_blood/     # Violent/bloody content
  validation/
    (same structure as train/)
```

3. **Collect training images:**
- Minimum 50-100 images per class for training
- 20-30 images per class for validation
- More data = better accuracy

## Training the Model

Run the training script:
```bash
python train_model.py
```

The script will:
- Load images from `data/train/` and `data/validation/`
- Use data augmentation to improve generalization
- Train using transfer learning (MobileNetV2 base)
- Save the best model to `models/image_classifier.h5`

## Training Parameters

You can modify these in `train_model.py`:
- `EPOCHS`: Number of training epochs (default: 10)
- `BATCH_SIZE`: Batch size (default: 32)
- `IMG_SIZE`: Input image size (default: 224x224)

## Using the Trained Model

The model is automatically loaded when the backend starts. Set:
```bash
MOCK_CLASSIFIER=true
```

The backend will use the ML model for predictions. If the model file doesn't exist, it will create a new untrained model (which will need training).

## Model Architecture

- **Base**: MobileNetV2 (pre-trained on ImageNet)
- **Transfer Learning**: Frozen base + custom classification head
- **Output**: 8 classes with softmax activation
- **Input**: 224x224 RGB images

## Improving Accuracy

1. **More training data**: Collect more diverse images
2. **Data augmentation**: Already enabled in training script
3. **Fine-tuning**: Unfreeze base model layers for advanced training
4. **Hyperparameter tuning**: Adjust learning rate, batch size, etc.

## Quick Start with Sample Data

If you don't have training data yet, you can:
1. Download public datasets (ImageNet subsets, etc.)
2. Use web scraping (respecting copyright)
3. Start with a small dataset and iteratively improve

## Notes

- The model uses transfer learning, so it works well even with limited data
- First training may take 10-30 minutes depending on your data size
- The model will automatically fall back to heuristics if it fails to load

