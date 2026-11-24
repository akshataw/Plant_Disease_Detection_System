import os
from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Detect connections killed by a db container restart instead of failing the next request
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
    # Small allowance on top of the file itself for multipart overhead
    MAX_CONTENT_LENGTH = (MAX_UPLOAD_MB + 1) * 1024 * 1024
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.getcwd(), "uploads"))

    MODEL_TYPE = os.getenv("MODEL_TYPE", "keras")
    MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/plant_disease_v1.keras")
    MODEL_VERSION = os.getenv("MODEL_VERSION")  # defaults to the model file name
    CLASS_NAMES_PATH = os.getenv("CLASS_NAMES_PATH", "/app/models/class_names.json")
    TOP_K = 3
    LOW_CONFIDENCE_THRESHOLD = float(os.getenv("LOW_CONFIDENCE_THRESHOLD", "0.5"))

    TESTING = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret-key-that-is-long-enough-for-hs256"
    MODEL_TYPE = "none"
    BCRYPT_LOG_ROUNDS = 4
