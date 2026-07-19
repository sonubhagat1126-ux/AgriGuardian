"""
SmartEdge AgriGuardian — TFLite Model Training Pipeline
========================================================
File: modules/leaf_detection/train.py

Trains a custom deep learning classifier on the local PlantVillage dataset
using Transfer Learning with MobileNetV2 (pre-trained on ImageNet).
Converts the final trained Keras model into an optimized .tflite format
suitable for low-latency on-device inference on the Arduino UNO Q.

Dataset Location:
  Smartedge-Agrigaurdian-/PlantVillage/

Execution:
  python modules/leaf_detection/train.py
"""

import os
import sys
import logging
from typing import Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Ensure we can import tensorflow
try:
    import tensorflow as tf
    from tensorflow.keras import layers, models
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
except ImportError:
    logger.error(
        "TensorFlow is required to run the training script. "
        "Please install it using: pip install tensorflow"
    )
    sys.exit(1)


# ── Configuration Constants ──────────────────────────────────────────────────
IMAGE_SIZE: Tuple[int, int] = (224, 224)
BATCH_SIZE: int = 32
EPOCHS: int = 5
VAL_SPLIT: float = 0.2
LEARNING_RATE: float = 0.0001

# Path resolution relative to this file
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


# Search for the PlantVillage directory
DATASET_DIR = os.path.join(PROJECT_ROOT, "PlantVillage")
if not os.path.exists(DATASET_DIR):
    # Fallback to current working directory checking
    DATASET_DIR = os.path.abspath("./PlantVillage")

# Resolve duplicate nested directory if present
if os.path.exists(os.path.join(DATASET_DIR, "PlantVillage")):
    DATASET_DIR = os.path.join(DATASET_DIR, "PlantVillage")

MODEL_OUT_DIR = os.path.join(HERE, "model")
TFLITE_PATH = os.path.join(MODEL_OUT_DIR, "leaf_model.tflite")
LABELS_PATH = os.path.join(MODEL_OUT_DIR, "labels.txt")

# Subset directory path
SUBSET_DIR = os.path.join(HERE, "PlantVillage_subset")
MAX_IMAGES_PER_CLASS = 70


# ── Dataset Subsetting ────────────────────────────────────────────────────────

def prepare_subset(src_dir: str, dest_dir: str, limit: int) -> None:
    """
    Creates a balanced subset dataset by copying up to 'limit' images per class
    to a local directory. This speeds up CPU training significantly.
    """
    import shutil
    
    # Always rebuild the subset to ensure the limit is respected
    if os.path.exists(dest_dir):
        logger.info(f"Clearing old dataset subset directory at: {dest_dir}")
        shutil.rmtree(dest_dir)

    logger.info(f"Creating a balanced dataset subset (max {limit} images/class) at: {dest_dir}...")
    os.makedirs(dest_dir, exist_ok=True)
    
    classes = [d for d in os.listdir(src_dir) if os.path.isdir(os.path.join(src_dir, d))]
    
    for cls in classes:
        src_cls_dir = os.path.join(src_dir, cls)
        dest_cls_dir = os.path.join(dest_dir, cls)
        os.makedirs(dest_cls_dir, exist_ok=True)
        
        # Get files and copy up to limit
        files = [f for f in os.listdir(src_cls_dir) if os.path.isfile(os.path.join(src_cls_dir, f))]
        files_to_copy = files[:limit]
        
        for f in files_to_copy:
            shutil.copy2(os.path.join(src_cls_dir, f), os.path.join(dest_cls_dir, f))
            
    logger.info("Dataset subset creation complete.")


# ── Main Training Pipeline ────────────────────────────────────────────────────

def main():
    logger.info("=" * 60)
    logger.info("  SmartEdge AgriGuardian — Custom Model Training")
    logger.info("=" * 60)
    logger.info(f"Raw dataset source directory: {DATASET_DIR}")
    
    if not os.path.exists(DATASET_DIR):
        logger.error(
            f"Dataset folder '{DATASET_DIR}' not found. "
            "Please make sure the 'PlantVillage' folder containing disease subfolders "
            "is located in the root of the repository."
        )
        sys.exit(1)

    # Prepare local balanced subset
    prepare_subset(DATASET_DIR, SUBSET_DIR, MAX_IMAGES_PER_CLASS)

    # Create target model output directory
    os.makedirs(MODEL_OUT_DIR, exist_ok=True)

    # 1. Load Dataset from local subset directory
    logger.info(f"Loading dataset from subset directory: {SUBSET_DIR}...")
    train_ds = tf.keras.utils.image_dataset_from_directory(
        SUBSET_DIR,
        validation_split=VAL_SPLIT,
        subset="training",
        seed=123,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        SUBSET_DIR,
        validation_split=VAL_SPLIT,
        subset="validation",
        seed=123,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
    )

    class_names = train_ds.class_names
    num_classes = len(class_names)
    logger.info(f"Loaded {num_classes} classes: {class_names}")

    # Write class labels to text file
    with open(LABELS_PATH, "w") as f:
        for name in class_names:
            f.write(f"{name}\n")
    logger.info(f"Saved class labels mapping to: {LABELS_PATH}")

    # Configure datasets for performance (prefetching and caching)
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)


    # 2. Build Keras Model with Transfer Learning
    logger.info("Building MobileNetV2 model architecture...")
    
    # Preprocessing layer mapping (converts pixels [0, 255] to [-1, 1] for MobileNetV2)
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.2),
        layers.RandomZoom(0.1),
    ])

    # MobileNetV2 base model with frozen weights
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights="imagenet"
    )
    base_model.trainable = False

    # Complete model assembly
    inputs = tf.keras.Input(shape=(224, 224, 3))
    x = data_augmentation(inputs)
    x = preprocess_input(x)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)
    model = tf.keras.Model(inputs, outputs)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"]
    )
    
    model.summary()

    # 3. Phase 1: Train classification head (transfer learning)
    logger.info(f"Starting Phase 1 (Transfer Learning): training head for 3 epochs...")
    
    history_phase1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=3
    )

    # 4. Phase 2: Fine-Tuning (unfreeze base model top layers)
    logger.info("Starting Phase 2 (Fine-Tuning): unfreezing top layers of base model...")
    base_model.trainable = True
    
    # Freeze layers before index 115 to speed up backpropagation
    # unfreezes only the last convolution block and classification head
    for layer in base_model.layers[:115]:
        layer.trainable = False

    
    # We recompile the model with a very low learning rate (1e-5)
    # to fine-tune the feature extractor layers without destroying ImageNet pre-trained representations.
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"]
    )
    
    logger.info("Fine-tuning model summary:")
    model.summary()

    logger.info("Training with fine-tuning for another 7 epochs...")
    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", 
        patience=2, 
        restore_best_weights=True
    )
    
    history_phase2 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=7,
        callbacks=[early_stop]
    )
    logger.info("Two-stage training completed successfully.")

    # 5. Convert Model to TFLite
    logger.info("Converting Keras model to TensorFlow Lite (TFLite) format...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # Apply standard float16 quantization to optimize file size without losing accuracy
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.float16]
    
    tflite_model = converter.convert()

    # Save quantized .tflite model
    with open(TFLITE_PATH, "wb") as f:
        f.write(tflite_model)
        
    logger.info("=" * 60)
    logger.info(f"  SUCCESSFULLY GENERATED TFLITE MODEL")
    logger.info("=" * 60)
    logger.info(f"  TFLite Model saved to: {TFLITE_PATH} ({len(tflite_model) / (1024*1024):.2f} MB)")
    logger.info(f"  Labels mapping saved to: {LABELS_PATH}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
