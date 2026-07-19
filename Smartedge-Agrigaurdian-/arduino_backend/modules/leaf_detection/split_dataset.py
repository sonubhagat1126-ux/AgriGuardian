"""
SmartEdge AgriGuardian — PlantVillage YOLO Partitioning Script
===============================================================
File: modules/leaf_detection/split_dataset.py

Splits the local PlantVillage dataset into Train (70%), Val (20%), and Test (10%)
subdirectories in the format expected by the YOLO11 Classification engine:

  PlantVillage_YOLO/
    train/
      class1/
      class2/
    val/
      class1/
      class2/
    test/
      class1/
      class2/

Automatic Class Balancing:
  Ensures a balanced dataset (max 100 train, 28 val, 14 test images per class)
  to speed up CPU-bound training and prevent class bias.
"""

import os
import shutil
import random
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Path configuration
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

DATASET_SRC = os.path.join(PROJECT_ROOT, "PlantVillage")
if os.path.exists(os.path.join(DATASET_SRC, "PlantVillage")):
    DATASET_SRC = os.path.join(DATASET_SRC, "PlantVillage")

DATASET_DEST = os.path.join(HERE, "PlantVillage_YOLO")

# Target image counts per class to satisfy 70/20/10 split
TRAIN_COUNT = 40
VAL_COUNT = 12
TEST_COUNT = 6
TOTAL_PER_CLASS = TRAIN_COUNT + VAL_COUNT + TEST_COUNT



def main():
    logger.info("=" * 60)
    logger.info("  SmartEdge AgriGuardian — YOLO Dataset Partitioner")
    logger.info("=" * 60)
    logger.info(f"Source directory: {DATASET_SRC}")
    logger.info(f"Output split directory: {DATASET_DEST}")
    
    if not os.path.exists(DATASET_SRC):
        logger.error(f"Source directory '{DATASET_SRC}' does not exist.")
        return

    # Clear old split directory if it exists
    if os.path.exists(DATASET_DEST):
        logger.info(f"Clearing old split directory at {DATASET_DEST}...")
        shutil.rmtree(DATASET_DEST)

    # Recreate directory structures
    for split in ["train", "val", "test"]:
        os.makedirs(os.path.join(DATASET_DEST, split), exist_ok=True)

    # Class folders scan
    classes = [d for d in os.listdir(DATASET_SRC) if os.path.isdir(os.path.join(DATASET_SRC, d))]
    logger.info(f"Discovered {len(classes)} classes.")

    # Seed random split for reproducibility
    random.seed(42)

    for cls in classes:
        src_cls_dir = os.path.join(DATASET_SRC, cls)
        
        # Get all valid image files
        all_files = [
            f for f in os.listdir(src_cls_dir)
            if os.path.isfile(os.path.join(src_cls_dir, f)) and f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        
        if len(all_files) < TOTAL_PER_CLASS:
            logger.warning(
                f"Class '{cls}' contains only {len(all_files)} images, "
                f"which is less than target {TOTAL_PER_CLASS}. Skipping class balancing for this category."
            )
            random.shuffle(all_files)
            # Adapt counts proportionally
            n = len(all_files)
            tr = int(n * 0.70)
            vl = int(n * 0.20)
            te = n - tr - vl
            train_files = all_files[:tr]
            val_files = all_files[tr:tr+vl]
            test_files = all_files[tr+vl:]
        else:
            # Select balanced subset
            selected_subset = random.sample(all_files, TOTAL_PER_CLASS)
            train_files = selected_subset[:TRAIN_COUNT]
            val_files = selected_subset[TRAIN_COUNT:TRAIN_COUNT+VAL_COUNT]
            test_files = selected_subset[TRAIN_COUNT+VAL_COUNT:]

        # Copy files to split directories
        for split, files in [("train", train_files), ("val", val_files), ("test", test_files)]:
            dest_cls_dir = os.path.join(DATASET_DEST, split, cls)
            os.makedirs(dest_cls_dir, exist_ok=True)
            for f in files:
                shutil.copy2(os.path.join(src_cls_dir, f), os.path.join(dest_cls_dir, f))
                
        logger.info(f"Class '{cls}': train={len(train_files)}, val={len(val_files)}, test={len(test_files)}")

    logger.info("=" * 60)
    logger.info("  SUCCESSFULLY PREPARED YOLO 70/20/10 SPLIT DATASET")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
