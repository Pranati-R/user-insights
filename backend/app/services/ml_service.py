from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from huggingface_hub import snapshot_download
from loguru import logger
from skops.io import load as skops_load
import joblib
from sklearn.ensemble import IsolationForest

from app.core.config import get_settings
from app.schemas.analytics import SessionMetrics

settings = get_settings()

_model: IsolationForest | None = None


def load_model() -> IsolationForest:
    """
    Loads HuggingFace IsolationForest model.
    Automatically supports both .skops and .pkl formats.
    Falls back to a default dummy IsolationForest if loading fails.
    """
    global _model
    if _model is not None:
        return _model

    try:
        logger.info("Downloading anomaly model from {}", settings.hf_model_repo)
        repo_path = snapshot_download(
            repo_id=settings.hf_model_repo,
            token=settings.hf_token or None,
            allow_patterns=[settings.hf_model_filename],
        )
        model_path = Path(repo_path) / settings.hf_model_filename

        logger.info("Found model at {}", model_path)

        # Load based on file extension
        ext = model_path.suffix.lower()

        if ext == ".skops":
            logger.info("Loading model as .skops file")
            _model = skops_load(model_path, trusted=True)
        elif ext in [".pkl", ".pickle"]:
            logger.info("Loading model as .pkl file")
            _model = joblib.load(model_path)
        else:
            raise ValueError(f"Unsupported model format: {ext}")

        logger.info("Anomaly model loaded successfully")

    except Exception as exc:
        logger.error("Failed to load HF model: {}", exc)
        logger.warning("Falling back to default IsolationForest")

        # Create simple fallback model
        fallback = IsolationForest(random_state=42)
        dummy = np.zeros((10, 7))  # 7 features required
        fallback.fit(dummy)
        _model = fallback

    return _model


def build_feature_vector(metrics: SessionMetrics) -> np.ndarray:
    return np.array(
        [
            metrics.duration_seconds,
            metrics.event_count,
            metrics.click_rate,
            metrics.unique_pages,
            metrics.action_diversity,
            metrics.avg_inter_event_seconds,
            metrics.dwell_estimate_seconds,
        ]
    ).reshape(1, -1)


def score_session(metrics: SessionMetrics) -> dict[str, Any]:
    model = load_model()
    features = build_feature_vector(metrics)
    score = -float(model.score_samples(features)[0])
    is_anomalous = score >= settings.anomaly_score_threshold

    return {
        "score": score,
        "is_anomalous": is_anomalous,
        "features": features.tolist(),
    }
