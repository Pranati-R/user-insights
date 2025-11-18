from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from huggingface_hub import snapshot_download
from loguru import logger
from skops.io import load as skops_load
import joblib

from pyod.models.iforest import IForest

from app.core.config import get_settings
from app.schemas.analytics import SessionMetrics

settings = get_settings()

_model: IForest | None = None

LOCAL_MODEL_PATH = Path("app/models/local_iforest.pkl")   # <-- LOCAL MODEL


def load_local_model() -> IForest | None:
    """Try loading the locally saved PyOD model."""
    print(LOCAL_MODEL_PATH)
    print(LOCAL_MODEL_PATH.exists())
    if LOCAL_MODEL_PATH.exists():
        try:
            logger.info("Loading local fallback model from {}", LOCAL_MODEL_PATH)
            return joblib.load(LOCAL_MODEL_PATH)
        except Exception as e:
            logger.error("Failed to load local model: {}", e)
    return None


def load_model() -> IForest:
    """
    Loads model from HuggingFace.
    If HF fails, loads local model.
    If that fails, loads emergency fallback model.
    """
    global _model
    if _model is not None:
        return _model

    # # -------------------------------
    # # TRY 1: Load from HuggingFace
    # # -------------------------------
    # try:
    #     logger.info("Downloading anomaly model from {}", settings.hf_model_repo)
    #     repo_path = snapshot_download(
    #         repo_id=settings.hf_model_repo,
    #         token=settings.hf_token or None,
    #         allow_patterns=[settings.hf_model_filename],
    #     )
    #     model_path = Path(repo_path) / settings.hf_model_filename

    #     ext = model_path.suffix.lower()

    #     if ext == ".skops":
    #         _model = skops_load(model_path, trusted=True)
    #     else:
    #         _model = joblib.load(model_path)

    #     logger.info("HF model loaded successfully")

    #     return _model

    # except Exception as exc:
    #     logger.error("HF model load failed: {}", exc)

    # -------------------------------
    # TRY 2: Load local model
    # -------------------------------
    print("Loading local model")
    local_model = load_local_model()
    if local_model is not None:
        logger.info("Loaded local model successfully")
        _model = local_model
        return _model

    # -------------------------------
    # TRY 3: Emergency fallback
    # -------------------------------
    logger.warning("Using emergency fallback PyOD IForest model")

    fallback = IForest(contamination=0.02, random_state=42)
    dummy = np.zeros((20, 7))  # 7 features
    fallback.fit(dummy)
    _model = fallback

    return _model


# --------------------------------
# Feature Builder
# --------------------------------
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

    score = float(model.decision_function(features)[0])
    is_anomalous = score >= settings.anomaly_score_threshold

    return {
        "score": score,
        "is_anomalous": is_anomalous,
        "features": features.tolist(),
    }
