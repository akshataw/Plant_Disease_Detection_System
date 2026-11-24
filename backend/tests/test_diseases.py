import json
import os

from app.services.disease_info import find_disease, normalize_label

KB = json.load(open(os.path.join(os.path.dirname(__file__), "..", "app", "data", "diseases.json")))
REQUIRED = {"crop", "disease", "is_healthy", "description", "symptoms", "causes", "prevention", "treatment"}

# Class names as emitted by TensorFlow Datasets `plant_village` (used by the training notebook)
TFDS_LABELS = [
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


def test_knowledge_base_complete():
    assert len(KB) == 38
    assert len({normalize_label(k) for k in KB}) == 38  # normalisation keeps entries distinct
    for label, info in KB.items():
        assert REQUIRED <= info.keys(), label
        if not info["is_healthy"]:
            assert info["symptoms"] and info["prevention"] and info["treatment"], label


def test_tfds_and_kaggle_labels_resolve():
    for label in TFDS_LABELS + list(KB):
        assert find_disease(label) is not None, label


def test_disease_endpoints(client):
    res = client.get("/api/v1/diseases")
    assert res.status_code == 200 and len(res.get_json()["items"]) == 38
    res = client.get("/api/v1/diseases/Corn___Common_rust")
    assert res.status_code == 200 and res.get_json()["disease"] == "Common rust"
    assert client.get("/api/v1/diseases/Nope___nothing").status_code == 404


def test_health(client):
    body = client.get("/api/v1/health").get_json()
    assert body["database"] is True and body["model_loaded"] is True
