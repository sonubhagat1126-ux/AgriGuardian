"""
SmartEdge AgriGuardian — YOLO11 Classification Model Training Pipeline
=======================================================================
File: modules/leaf_detection/train_yolo.py

Trains a production-grade YOLO11 classification model (yolo11n-cls) on the
partitioned 70/20/10 split PlantVillage dataset.
Enables strong image augmentations, AdamW optimizer, label smoothing,
and outputs best weights in PyTorch (.pt), ONNX, and TFLite formats.

Execution:
  python modules/leaf_detection/train_yolo.py
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Ensure we can import ultralytics
try:
    from ultralytics import YOLO
except ImportError:
    logger.error("ultralytics package is required. Please run pip install ultralytics first.")
    sys.exit(1)


# ── Configuration Constants ──────────────────────────────────────────────────
IMAGE_SIZE = 224
BATCH_SIZE = 16
EPOCHS = 15  # Configured to 15 for quick background training run

PATIENCE = 3 # Early stopping patience

HERE = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(HERE, "PlantVillage_YOLO")
MODEL_OUT_DIR = os.path.join(HERE, "model")


def main():
    logger.info("=" * 60)
    logger.info("  SmartEdge AgriGuardian — YOLO11 Classification Training")
    logger.info("=" * 60)
    logger.info(f"Dataset directory: {DATASET_DIR}")
    
    if not os.path.exists(DATASET_DIR):
        logger.error(
            f"Split dataset folder '{DATASET_DIR}' not found. "
            "Please run split_dataset.py first."
        )
        sys.exit(1)

    os.makedirs(MODEL_OUT_DIR, exist_ok=True)

    # 1. Initialize YOLO11 Classification Model
    # We use yolo11n-cls (Nano) for low-latency CPU deployment on Snapdragon devices
    logger.info("Loading pre-trained YOLO11n-cls weights...")
    model = YOLO("yolo11n-cls.pt")

    # 2. Run Model Training with Configured Parameters
    logger.info("Starting model training pipeline...")
    results = model.train(
        data=DATASET_DIR,
        epochs=EPOCHS,
        imgsz=IMAGE_SIZE,
        batch=BATCH_SIZE,
        patience=PATIENCE,
        optimizer="AdamW",
        lr0=0.001,
        weight_decay=0.01,
        device="cpu",      # Force CPU execution for board environment
        workers=2,
        cache=True,        # Cache images in RAM to speed up CPU loaders
        # Data Augmentations (Strong parameters to prevent overfitting)
        hsv_h=0.015,       # Hue shift
        hsv_s=0.07,        # Saturation adjustment
        hsv_v=0.4,         # Brightness adjustment
        degrees=20.0,      # Rotation ±20 degrees
        translate=0.1,     # Translate ±10%
        scale=0.2,         # Scale/Zoom ±20%
        fliplr=0.5,        # Horizontal flip (50% probability)
        flipud=0.5,        # Vertical flip (50% probability)
    )

    
    logger.info("Training completed. Evaluating metrics...")

    # 3. Evaluate Validation Metrics
    metrics = model.val()
    
    top1_acc = metrics.top1
    top5_acc = metrics.top5
    logger.info("=" * 60)
    logger.info("  VALIDATION PERFORMANCE METRICS")
    logger.info("=" * 60)
    logger.info(f"  Top-1 Accuracy: {top1_acc * 100:.2f}%")
    logger.info(f"  Top-5 Accuracy: {top5_acc * 100:.2f}%")
    logger.info("=" * 60)

    # 4. Export Model in Target Formats
    # ONNX is the preferred deployment format for Qualcomm AI Hub
    logger.info("Exporting model to ONNX format...")
    try:
        onnx_path = model.export(format="onnx", imgsz=IMAGE_SIZE)
        logger.info(f"Exported ONNX model path: {onnx_path}")
    except Exception as e:
        logger.error(f"Failed to export model to ONNX: {e}")

    # Export to TFLite format (handled gracefully as it is OS-restricted in Ultralytics)
    logger.info("Exporting model to TFLite format...")
    try:
        tflite_path = model.export(format="tflite", imgsz=IMAGE_SIZE)
        logger.info(f"Exported TFLite model path: {tflite_path}")
    except Exception as e:
        logger.warning(
            f"LiteRT/TFLite export is not supported on this host OS platform: {e}. "
            "Proceeding with PyTorch (.pt) and ONNX formats."
        )


    # Copy files to our standard model output directory
    best_weights_pt = os.path.join(results.save_dir, "weights", "best.pt")
    best_weights_onnx = os.path.join(results.save_dir, "weights", "best.onnx")
    
    # We copy them to modules/leaf_detection/model/ for runtime execution
    if os.path.exists(best_weights_pt):
        shutil_dest_pt = os.path.join(MODEL_OUT_DIR, "best.pt")
        import shutil
        shutil.copy2(best_weights_pt, shutil_dest_pt)
        logger.info(f"Saved PyTorch weights checkpoint to: {shutil_dest_pt}")
        
    if os.path.exists(best_weights_onnx):
        shutil_dest_onnx = os.path.join(MODEL_OUT_DIR, "best.onnx")
        shutil.copy2(best_weights_onnx, shutil_dest_onnx)
        logger.info(f"Saved ONNX checkpoint to: {shutil_dest_onnx}")


if __name__ == "__main__":
    main()
