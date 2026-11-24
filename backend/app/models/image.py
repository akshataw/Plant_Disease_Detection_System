from ..extensions import db
from .user import utcnow


class Image(db.Model):
    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    image_path = db.Column(db.String(255), unique=True, nullable=False)  # stored file name, not a full path
    original_filename = db.Column(db.String(255))
    content_type = db.Column(db.String(50), nullable=False)
    uploaded_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    user = db.relationship("User", back_populates="images")
    predictions = db.relationship("Prediction", back_populates="image", cascade="all, delete-orphan")
