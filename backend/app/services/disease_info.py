"""Disease knowledge base (ADR 0010), keyed by model class label.

Labels are matched after normalisation (ADR 0012) so TFDS and Kaggle PlantVillage naming variants
(e.g. "Corn___Common_rust" vs "Corn_(maize)___Common_rust_") resolve to the same entry.
"""
import json
import os
import re
from functools import lru_cache

KB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "diseases.json")


def normalize_label(label: str) -> str:
    s = re.sub(r"\([^)]*\)", "", label.lower())
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


@lru_cache(maxsize=1)
def _knowledge_base() -> dict:
    with open(KB_PATH, encoding="utf-8") as f:
        entries = json.load(f)
    return {normalize_label(label): {"label": label, **info} for label, info in entries.items()}


def _fallback(label: str) -> dict:
    crop, _, disease = label.partition("___")
    disease = disease.replace("_", " ").strip() or "Unknown"
    return {
        "label": label,
        "crop": crop.replace("_", " ").strip(),
        "disease": disease,
        "is_healthy": disease.lower() == "healthy",
        "description": "No detailed information is available for this class yet.",
        "symptoms": [], "causes": [], "prevention": [], "treatment": [],
    }


def get_disease(label: str) -> dict:
    return _knowledge_base().get(normalize_label(label)) or _fallback(label)


def display_name(label: str) -> str:
    info = get_disease(label)
    return f"{info['crop']} — {info['disease']}"


def list_diseases() -> list[dict]:
    return [
        {k: info[k] for k in ("label", "crop", "disease", "is_healthy")}
        for info in sorted(_knowledge_base().values(), key=lambda i: (i["crop"], i["disease"]))
    ]


def find_disease(label: str) -> dict | None:
    return _knowledge_base().get(normalize_label(label))
