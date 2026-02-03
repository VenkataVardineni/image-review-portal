"""
Training script for the image classifier model
Place your training images in the following structure:
data/
  train/
    safe_animal/
    safe_landscape/
    safe_portrait/
    safe_food/
    safe_object/
    violence_weapon/
    inappropriate/
    violence_blood/
  validation/
    (same structure)
"""
import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 10
DATA_DIR = "./data"
TRAIN_DIR = os.path.join(DATA_DIR, "train")
VAL_DIR = os.path.join(DATA_DIR, "validation")
MODEL_PATH = "./models/image_classifier.h5"

# Class labels
CLASS_LABELS = [
    "safe_animal",
    "safe_landscape",
    "safe_portrait",
    "safe_food",
    "safe_object",
    "violence_weapon",
    "inappropriate",
    "violence_blood",
]

def create_model():
    """Create the model architecture"""
    # Load pre-trained MobileNetV2
    base_model = MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model
    base_model.trainable = False
    
    # Add custom head
    inputs = keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    x = base_model(inputs, training=False)
    x = keras.layers.GlobalAveragePooling2D()(x)
    x = keras.layers.Dropout(0.2)(x)
    x = keras.layers.Dense(128, activation='relu')(x)
    x = keras.layers.Dropout(0.2)(x)
    outputs = keras.layers.Dense(len(CLASS_LABELS), activation='softmax')(x)
    
    model = keras.Model(inputs, outputs)
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def train():
    """Train the model"""
    # Check if data directory exists
    if not os.path.exists(TRAIN_DIR):
        logger.error(f"Training directory not found: {TRAIN_DIR}")
        logger.info("Please create the following structure:")
        logger.info("data/train/{class_name}/")
        logger.info("data/validation/{class_name}/")
        return
    
    # Create models directory
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        fill_mode='nearest'
    )
    
    # No augmentation for validation
    val_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input
    )
    
    # Create data generators
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )
    
    val_generator = None
    if os.path.exists(VAL_DIR):
        val_generator = val_datagen.flow_from_directory(
            VAL_DIR,
            target_size=(IMG_SIZE, IMG_SIZE),
            batch_size=BATCH_SIZE,
            class_mode='categorical'
        )
    
    # Create model
    model = create_model()
    model.summary()
    
    # Callbacks
    callbacks = [
        keras.callbacks.ModelCheckpoint(
            MODEL_PATH,
            save_best_only=True,
            monitor='val_accuracy' if val_generator else 'accuracy',
            mode='max'
        ),
        keras.callbacks.EarlyStopping(
            monitor='val_accuracy' if val_generator else 'accuracy',
            patience=5,
            restore_best_weights=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss' if val_generator else 'loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7
        )
    ]
    
    # Train model
    logger.info("Starting training...")
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=val_generator,
        callbacks=callbacks,
        verbose=1
    )
    
    logger.info(f"Training complete! Model saved to {MODEL_PATH}")
    logger.info(f"Final accuracy: {max(history.history['accuracy']):.2f}")
    if val_generator:
        logger.info(f"Final validation accuracy: {max(history.history['val_accuracy']):.2f}")

if __name__ == "__main__":
    train()

