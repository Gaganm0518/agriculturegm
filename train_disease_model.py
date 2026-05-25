"""
Plant Disease CNN Training Script.
Uses Transfer Learning (MobileNetV2) to train a disease classification model.
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.metrics import classification_report, confusion_matrix

# Configuration
BASE_DIR = '../datasets/plant_disease'
TRAIN_DIR = os.path.join(BASE_DIR, 'train')
VAL_DIR = os.path.join(BASE_DIR, 'val')
TEST_DIR = os.path.join(BASE_DIR, 'test')
MODELS_DIR = '../models'
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
NUM_CLASSES = 5

def create_generators():
    """Sets up the training, validation, and test generators."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
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

def build_model(num_classes):
    """Builds the MobileNetV2 transfer learning model."""
    print("\n--- Building MobileNetV2 Model ---")
    base_model = MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3)
    )
    
    # Freeze the base model
    base_model.trainable = False
    
    # Add custom head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.3)(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("Model compiled (Base frozen).")
    return model, base_model

def plot_history(history_phase1, history_phase2, save_path):
    """Plots and saves the training history curves."""
    acc = history_phase1.history['accuracy'] + (history_phase2.history['accuracy'] if history_phase2 else [])
    val_acc = history_phase1.history['val_accuracy'] + (history_phase2.history['val_accuracy'] if history_phase2 else [])
    loss = history_phase1.history['loss'] + (history_phase2.history['loss'] if history_phase2 else [])
    val_loss = history_phase1.history['val_loss'] + (history_phase2.history['val_loss'] if history_phase2 else [])

    epochs_range = range(len(acc))

    plt.figure(figsize=(12, 5))
    
    # Accuracy Plot
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, acc, label='Training Accuracy')
    plt.plot(epochs_range, val_acc, label='Validation Accuracy')
    if history_phase2:
        plt.axvline(x=len(history_phase1.history['accuracy'])-1, color='r', linestyle='--', label='Fine-Tuning Starts')
    plt.legend(loc='lower right')
    plt.title('Training and Validation Accuracy')

    # Loss Plot
    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, loss, label='Training Loss')
    plt.plot(epochs_range, val_loss, label='Validation Loss')
    if history_phase2:
        plt.axvline(x=len(history_phase1.history['loss'])-1, color='r', linestyle='--', label='Fine-Tuning Starts')
    plt.legend(loc='upper right')
    plt.title('Training and Validation Loss')

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"\nTraining curves saved to {save_path}")

def save_class_mapping(generator):
    """Saves class mapping."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    idx_to_class = {str(v): k for k, v in generator.class_indices.items()}
    json_path = os.path.join(script_dir, MODELS_DIR, 'class_names.json')
    with open(json_path, 'w') as f:
        json.dump(idx_to_class, f, indent=4)
    print(f"Class names saved to {json_path}")
    return idx_to_class

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_save_path = os.path.join(script_dir, MODELS_DIR, 'disease_cnn_model.h5')
    plot_save_path = os.path.join(script_dir, BASE_DIR, 'training_curves.png')
    cm_save_path = os.path.join(script_dir, BASE_DIR, 'cm_cnn.png')

    # 1. Generators
    train_gen, val_gen, test_gen = create_generators()
    num_classes = len(train_gen.class_indices)
    class_names_dict = save_class_mapping(train_gen)
    class_names = [class_names_dict[str(i)] for i in range(num_classes)]

    # 2. Build Model
    model, base_model = build_model(num_classes)

    # Callbacks
    early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
    checkpoint = ModelCheckpoint(model_save_path, monitor='val_accuracy', save_best_only=True, verbose=1)

    # 3. Train Phase 1 (Frozen Base)
    print("\n--- Phase 1: Training Head (Base Frozen) ---")
    history_p1 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=10,  # Increase for better accuracy with real dataset
        callbacks=[early_stop, checkpoint]
    )

    # 4. Train Phase 2 (Fine-Tuning)
    print("\n--- Phase 2: Fine-Tuning Top 30 Layers ---")
    base_model.trainable = True
    
    # Freeze all layers except the top 30
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    # Recompile with lower learning rate
    model.compile(
        optimizer=Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    history_p2 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=5,  # Increase for better accuracy with real dataset
        callbacks=[early_stop, checkpoint]
    )

    # 5. Plot Curves
    plot_history(history_p1, history_p2, plot_save_path)

    # 6. Evaluation
    print("\n--- Evaluating on Test Set ---")
    # Load best weights saved by ModelCheckpoint
    if os.path.exists(model_save_path):
        model.load_weights(model_save_path)

    test_loss, test_acc = model.evaluate(test_gen)
    print(f"Test Accuracy: {test_acc * 100:.2f}%")

    test_gen.reset()
    y_pred_prob = model.predict(test_gen)
    y_pred = np.argmax(y_pred_prob, axis=1)
    y_true = test_gen.classes

    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=class_names))

    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix - Plant Disease CNN')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(cm_save_path)
    plt.close()
    print(f"Confusion Matrix saved to {cm_save_path}")
    print(f"Final Model saved to {model_save_path}")

if __name__ == "__main__":
    main()
