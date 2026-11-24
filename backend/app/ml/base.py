"""Model-agnostic predictor contract (ADR 0011). Routes depend only on this interface."""
from abc import ABC, abstractmethod


class Predictor(ABC):
    @property
    @abstractmethod
    def version(self) -> str:
        """Identifier stored with each prediction (e.g. model file name)."""

    @property
    @abstractmethod
    def class_names(self) -> list[str]:
        """Ordered class labels matching the model's output units."""

    @abstractmethod
    def predict(self, image, top_k: int = 3) -> list[dict]:
        """Classify a PIL image. Returns [{"label": str, "confidence": float}, ...] sorted descending."""
