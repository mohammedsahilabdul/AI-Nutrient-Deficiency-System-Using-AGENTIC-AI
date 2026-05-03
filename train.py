import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras import layers, models

IMG_SIZE = 224
BATCH_SIZE = 8   # smaller batch for small dataset

# Paths
train_dir = "DATASETS/train"
val_dir = "DATASETS/val"

# Check if validation folder exists
use_validation = os.path.exists(val_dir)

# Data generators
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=25,
    zoom_range=0.3,


    
    horizontal_flip=True
)

if use_validation:
    val_datagen = ImageDataGenerator(rescale=1./255)

# Load training data
train_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical'
)

# Load validation data ONLY if exists
if use_validation:
    val_data = val_datagen.flow_from_directory(
        val_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

# Model (EfficientNet)
base_model = EfficientNetB0(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3)
)

base_model.trainable = False  # freeze

x = base_model.output
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dense(128, activation='relu')(x)
x = layers.Dropout(0.5)(x)
output = layers.Dense(train_data.num_classes, activation='softmax')(x)

model = models.Model(inputs=base_model.input, outputs=output)

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("✅ Model ready. Starting training...")

# Train
if use_validation:
    history = model.fit(
        train_data,
        validation_data=val_data,
        epochs=10
    )
else:
    print("⚠️ No validation folder found. Training without validation...")
    history = model.fit(
        train_data,
        epochs=10
    )

# Create models folder if not exists
os.makedirs("models", exist_ok=True)

# Save model
model.save("models/nutrient_model.h5")
print("✅ Model saved at models/nutrient_model.h5")

# ================================
# TEST EVALUATION (if exists)
# ================================
test_dir = "DATASETS/test"

if os.path.exists(test_dir):
    print("🧪 Running test evaluation...")

    test_datagen = ImageDataGenerator(rescale=1./255)

    test_data = test_datagen.flow_from_directory(
        test_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

    loss, acc = model.evaluate(test_data)
    print(f"✅ Test Accuracy: {acc*100:.2f}%")
else:
    print("⚠️ No test folder found. Skipping test evaluation.")