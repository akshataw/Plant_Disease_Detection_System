from flask import current_app

from ..extensions import db
from ..models import Image, Prediction
from . import storage
from .disease_info import display_name, get_disease


class ModelUnavailableError(RuntimeError):
    pass


def run_prediction(user_id: int, pil_image, original_filename: str) -> Prediction:
    predictor = current_app.extensions.get("predictor")
    if predictor is None:
        raise ModelUnavailableError("The disease detection model is not loaded")

    top_k = predictor.predict(pil_image, top_k=current_app.config["TOP_K"])
    best = top_k[0]

    filename = storage.save_image(pil_image)
    try:
        image = Image(user_id=user_id, image_path=filename,
                      original_filename=(original_filename or "")[:255], content_type="image/jpeg")
        prediction = Prediction(
            image=image, user_id=user_id,
            disease_label=best["label"], disease_name=display_name(best["label"]),
            confidence=best["confidence"], top_k=top_k, model_version=predictor.version,
        )
        db.session.add_all([image, prediction])
        db.session.commit()
    except Exception:
        db.session.rollback()
        storage.delete_image(filename)
        raise
    return prediction


def serialize_prediction(p: Prediction, detailed: bool = True) -> dict:
    data = {
        "id": p.id,
        "disease_label": p.disease_label,
        "disease_name": p.disease_name,
        "confidence": p.confidence,
        "low_confidence": (p.confidence or 0) < current_app.config["LOW_CONFIDENCE_THRESHOLD"],
        "is_healthy": get_disease(p.disease_label)["is_healthy"],
        "model_version": p.model_version,
        "prediction_date": p.prediction_date.isoformat(),
        "image_id": p.image_id,
        "image_url": f"/api/v1/images/{p.image_id}",
    }
    if detailed:
        data["top_k"] = [{**t, "name": display_name(t["label"])} for t in (p.top_k or [])]
        data["details"] = get_disease(p.disease_label)
    return data


def delete_prediction(p: Prediction) -> None:
    image = p.image
    orphaned_file = None
    db.session.delete(p)
    db.session.flush()
    if db.session.query(Prediction.id).filter_by(image_id=image.id).first() is None:
        orphaned_file = image.image_path
        db.session.delete(image)
    db.session.commit()
    # Remove the file only once the rows are gone: a stray file is harmless, a row pointing at a
    # missing file is a permanently broken history entry.
    if orphaned_file:
        storage.delete_image(orphaned_file)
