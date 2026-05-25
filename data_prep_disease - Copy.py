"""
Plant Disease Dataset Preparation Script.
Organizes a subset of the PlantVillage dataset into train/val/test splits,
applies image augmentation using ImageDataGenerator, and exports class mappings.
"""

import os
import json
import shutil
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from PIL import Image

# Configuration
BASE_DIR = '../datasets/plant_disease'
RAW_DIR = os.path.join(BASE_DIR, 'raw')
TRAIN_DIR = os.path.join(BASE_DIR, 'train')
VAL_DIR = os.path.join(BASE_DIR, 'val')
TEST_DIR = os.path.join(BASE_DIR, 'test')
MODELS_DIR = '../models'

CLASSES = ['Healthy', 'Bacterial_Spot', 'Early_Blight', 'Late_Blight', 'Leaf_Mold']
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32

def create_mock_images():
    """Generates a mock dataset if the raw PlantVillage dataset is missing."""
    print("Checking for raw dataset...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(script_dir, RAW_DIR)
    
    if os.path.exists(raw_path) and len(os.listdir(raw_path)) > 0:
        print("Raw dataset found.")
        return raw_path

    print("Raw dataset not found. Generating mock PlantVillage dataset for demonstration...")
    os.makedirs(raw_path, exist_ok=True)
    
    # Generate 40 images per class
    for cls in CLASSES:
        cls_dir = os.path.join(raw_path, cls)
        os.makedirs(cls_dir, exist_ok=True)
        for i in range(40):
            # Create a simple colored square with random noise
            img_array = np.random.randint(0, 255, (IMAGE_SIZE[0], IMAGE_SIZE[1], 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img.save(os.path.join(cls_dir, f'{cls}_{i}.jpg'))
            
    print(f"Mock dataset generated at {raw_path}")
    return raw_path

def split_dataset(raw_path, split_ratio=(0.7, 0.15, 0.15)):
    """Splits raw images into train, val, test directories."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    for split_dir in [TRAIN_DIR, VAL_DIR, TEST_DIR]:
        path = os.path.join(script_dir, split_dir)
        if os.path.exists(path):
            print(f"Removing existing {split_dir} directory...")
            shutil.rmtree(path)
        os.makedirs(path)
        for cls in CLASSES:
            os.makedirs(os.path.join(path, cls))

    print(f"\n--- Splitting Dataset (Train: {split_ratio[0]*100}%, Val: {split_ratio[1]*100}%, Test: {split_ratio[2]*100}%) ---")
    
    total_train, total_val, total_test = 0, 0, 0
    
    for cls in CLASSES:
        cls_path = os.path.join(raw_path, cls)
        images = os.listdir(cls_path)
        np.random.seed(42)
        np.random.shuffle(images)
        
        n_train = int(len(images) * split_ratio[0])
        n_val = int(len(images) * split_ratio[1])
        
        train_imgs = images[:n_train]
        val_imgs = images[n_train:n_train+n_val]
        test_imgs = images[n_train+n_val:]
        
        # Copy files
        for img in train_imgs:
            shutil.copy(os.path.join(cls_path, img), os.path.join(script_dir, TRAIN_DIR, cls, img))
        for img in val_imgs:
            shutil.copy(os.path.join(cls_path, img), os.path.join(script_dir, VAL_DIR, cls, img))
        for img in test_imgs:
            shutil.copy(os.path.join(cls_path, img), os.path.join(script_dir, TEST_DIR, cls, img))
            
        print(f"Class '{cls}': {len(images)} total -> {len(train_imgs)} train | {len(val_imgs)} val | {len(test_imgs)} test")
        total_train += len(train_imgs)
        total_val += len(val_imgs)
        total_test += len(test_imgs)
        
    print(f"\nTotal Split: Train: {total_train}, Val: {total_val}, Test: {total_test}")

def setup_generators():
    """Configures ImageDataGenerators with augmentation for training."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("\n--- Setting up Data Generators ---")
    # Training generator with Augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    # Validation and Test generators (ONLY rescaling, NO augmentation)
    val_test_datagen = ImageDataGenerator(rescale=1./255)
    
    train_generator = train_datagen.flow_from_directory(
        os.path.join(script_dir, TRAIN_DIR),
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )
    
    val_generator = val_test_datagen.flow_from_directory(
        os.path.join(script_dir, VAL_DIR),
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )
    
    test_generator = val_test_datagen.flow_from_directory(
        os.path.join(script_dir, TEST_DIR),
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    
    return train_generator, val_generator, test_generator

def visualize_augmentations(train_generator):
    """Saves a 3x3 grid of augmented images."""
    print("\n--- Generating Augmentation Visualization ---")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get a batch
    images, labels = next(train_generator)
    class_indices = {v: k for k, v in train_generator.class_indices.items()}
    
    plt.figure(figsize=(10, 10))
    for i in range(9):
        ax = plt.subplot(3, 3, i + 1)
        plt.imshow(images[i])
        cls_name = class_indices[np.argmax(labels[i])]
        plt.title(cls_name)
        plt.axis("off")
        
    plt.tight_layout()
    plot_path = os.path.join(script_dir, BASE_DIR, 'augmented_samples.png')
    plt.savefig(plot_path)
    plt.close()
    print(f"Augmented sample grid saved to {plot_path}")

def save_class_mapping(generator):
    """Saves the class indices to a JSON file for inference later."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(script_dir, MODELS_DIR), exist_ok=True)
    
    class_indices = generator.class_indices
    # Invert to map index -> name
    idx_to_class = {str(v): k for k, v in class_indices.items()}
    
    json_path = os.path.join(script_dir, MODELS_DIR, 'class_names.json')
    with open(json_path, 'w') as f:
        json.dump(idx_to_class, f, indent=4)
        
    print(f"\nClass names mapping saved to {json_path}")
    print(json.dumps(idx_to_class, indent=2))

def main():
    print("=========================================")
    print(" Plant Disease Dataset Preparation Start ")
    print("=========================================\n")
    
    # 1. Create or load raw data
    raw_path = create_mock_images()
    
    # 2. Split into train/val/test
    split_dataset(raw_path)
    
    # 3 & 4. Augmentation Pipeline and Generators
    train_gen, val_gen, test_gen = setup_generators()
    
    # 5. Visualize
    visualize_augmentations(train_gen)
    
    # 6. Save Mapping
    save_class_mapping(train_gen)
    
    print("\nData preparation complete! Ready for CNN training.")

if __name__ == "__main__":
    main()
