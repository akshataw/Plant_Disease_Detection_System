"""Create a tiny, untrained 38-class model with the same I/O contract as the real one.

Lets the full stack run end-to-end before the Colab-trained model is available (ADR 0003).
Predictions from this model are random — never use it for real diagnosis.

Usage (inside backend container):  python /ml/scripts/make_dummy_model.py --out /app/models
"""
import argparse
import json
import os

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
import keras  # noqa: E402

# Same order as TFDS `plant_village` label names
CLASS_NAMES = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
    "Blueberry___healthy", "Cherry___healthy", "Cherry___Powdery_mildew",
    "Corn___Cercospora_leaf_spot Gray_leaf_spot", "Corn___Common_rust", "Corn___healthy",
    "Corn___Northern_Leaf_Blight", "Grape___Black_rot", "Grape___Esca_(Black_Measles)", "Grape___healthy",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot", "Peach___healthy", "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy",
    "Potato___Early_blight", "Potato___healthy", "Potato___Late_blight", "Raspberry___healthy",
    "Soybean___healthy", "Squash___Powdery_mildew", "Strawberry___healthy", "Strawberry___Leaf_scorch",
    "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___healthy", "Tomato___Late_blight",
    "Tomato___Leaf_Mold", "Tomato___Septoria_leaf_spot", "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot", "Tomato___Tomato_mosaic_virus", "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="/app/models")
    parser.add_argument("--name", default="plant_disease_dummy.keras")
    args = parser.parse_args()

    model = keras.Sequential([
        keras.Input(shape=(224, 224, 3)),
        keras.layers.Rescaling(1 / 127.5, offset=-1),  # same embedded preprocessing as the real model
        keras.layers.Conv2D(8, 3, strides=4, activation="relu"),
        keras.layers.GlobalAveragePooling2D(),
        keras.layers.Dense(len(CLASS_NAMES), activation="softmax"),
    ])
    os.makedirs(args.out, exist_ok=True)
    model.save(os.path.join(args.out, args.name))
    names_path = os.path.join(args.out, "class_names.json")
    if not os.path.exists(names_path):  # never clobber the real model's class list
        with open(names_path, "w") as f:
            json.dump(CLASS_NAMES, f, indent=2)
    print(f"Wrote {os.path.join(args.out, args.name)} and {names_path}")


if __name__ == "__main__":
    main()
