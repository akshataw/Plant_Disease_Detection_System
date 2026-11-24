from ..extensions import db
from .user import utcnow


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    disease_label = db.Column(db.String(150), nullable=False)  # canonical model class label
    disease_name = db.Column(db.String(150), nullable=False)  # human-readable name
    confidence = db.Column(db.Float, nullable=True)
    top_k = db.Column(db.JSON, nullable=True)  # [{"label": ..., "confidence": ...}, ...]
    model_version = db.Column(db.String(100), nullable=True)
    prediction_date = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    user = db.relationship("User", back_populates="predictions")
    image = db.relationship("Image", back_populates="predictions")
