from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from huggingface_hub import snapshot_download
from loguru import logger
from skops.io import load as skops_load
import joblib

from pyod.models.iforest import IForest
from pyod.models.lof import LOF
from pyod.models.knn import KNN
from sklearn.preprocessing import StandardScaler

from app.core.config import get_settings
from app.schemas.analytics import SessionMetrics

settings = get_settings()

_model: IForest | None = None
_scaler: StandardScaler | None = None
_ensemble_models: dict[str, Any] | None = None

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
    logger.warning("Using emergency fallback PyOD IForest model with improved parameters")

    # Improved IsolationForest with better parameters
    fallback = IForest(
        contamination=0.05,  # Expect 5% anomalies
        n_estimators=200,    # More trees for better detection
        max_samples=256,     # Subsample size
        random_state=42,
        behaviour='new'      # Use new sklearn behavior
    )
    
    # Generate more realistic dummy data with variance (10 features)
    np.random.seed(42)
    dummy = np.random.randn(100, 10) * np.array([100, 10, 0.3, 5, 3, 30, 50, 0.1, 0.3, 5])  # 10 features with realistic scales
    fallback.fit(dummy)
    _model = fallback

    return _model


# --------------------------------
# Feature Builder
# --------------------------------
def build_feature_vector(metrics: SessionMetrics, normalize: bool = True) -> np.ndarray:
    """
    Build feature vector with optional normalization.
    Features are engineered to capture anomalous behavior patterns.
    """
    features = np.array(
        [
            metrics.duration_seconds,
            metrics.event_count,
            metrics.click_rate,
            metrics.unique_pages,
            metrics.action_diversity,
            metrics.avg_inter_event_seconds,
            metrics.dwell_estimate_seconds,
            # Derived features for better anomaly detection
            metrics.event_count / max(metrics.duration_seconds, 1),  # Events per second
            metrics.unique_pages / max(metrics.event_count, 1),      # Page diversity
            metrics.click_rate * metrics.event_count,                # Total clicks
        ]
    ).reshape(1, -1)
    
    if normalize:
        # Apply robust scaling to handle outliers
        global _scaler
        if _scaler is None:
            _scaler = StandardScaler()
            # Fit on typical ranges
            typical_data = np.array([
                [300, 20, 0.3, 5, 3, 15, 60, 0.067, 0.25, 6],
                [600, 40, 0.4, 8, 5, 15, 75, 0.067, 0.2, 16],
                [120, 10, 0.2, 3, 2, 12, 40, 0.083, 0.3, 2],
            ])
            _scaler.fit(typical_data)
        features = _scaler.transform(features)
    
    return features


def score_session(metrics: SessionMetrics) -> dict[str, Any]:
    """
    Score a session for anomaly detection with detailed explanations.
    Returns score, anomaly flag, and feature contributions.
    """
    model = load_model()
    features = build_feature_vector(metrics, normalize=True)

    # Get anomaly score
    score = float(model.decision_function(features)[0])
    
    # Normalize score to 0-1 range for better interpretation
    # Higher score = more anomalous
    normalized_score = 1 / (1 + np.exp(-score))  # Sigmoid transformation
    
    is_anomalous = normalized_score >= settings.anomaly_score_threshold

    # Feature importance for explainability
    feature_names = [
        "duration_seconds",
        "event_count",
        "click_rate",
        "unique_pages",
        "action_diversity",
        "avg_inter_event_seconds",
        "dwell_estimate_seconds",
        "events_per_second",
        "page_diversity",
        "total_clicks",
    ]
    
    # Calculate feature contributions (simplified)
    feature_contributions = {}
    raw_features = build_feature_vector(metrics, normalize=False)[0]
    for i, name in enumerate(feature_names):
        if i < len(raw_features):
            feature_contributions[name] = float(raw_features[i])

    return {
        "score": normalized_score,
        "raw_score": score,
        "is_anomalous": is_anomalous,
        "features": features.tolist(),
        "feature_contributions": feature_contributions,
        "anomaly_reasons": _get_anomaly_reasons(metrics, is_anomalous),
    }


def _get_anomaly_reasons(metrics: SessionMetrics, is_anomalous: bool) -> list[str]:
    """
    Generate human-readable reasons for why a session was flagged as anomalous.
    """
    if not is_anomalous:
        return []
    
    reasons = []
    
    # Check for suspicious patterns
    if metrics.duration_seconds < 10:
        reasons.append("Very short session duration (< 10 seconds)")
    elif metrics.duration_seconds > 3600:
        reasons.append("Unusually long session duration (> 1 hour)")
    
    if metrics.event_count < 3:
        reasons.append("Very few events (< 3)")
    elif metrics.event_count > 100:
        reasons.append("Unusually high number of events (> 100)")
    
    if metrics.click_rate > 0.8:
        reasons.append("Extremely high click rate (> 80%)")
    elif metrics.click_rate < 0.05 and metrics.event_count > 10:
        reasons.append("Unusually low click rate (< 5%)")
    
    if metrics.avg_inter_event_seconds < 0.5:
        reasons.append("Very rapid event succession (< 0.5s between events)")
    elif metrics.avg_inter_event_seconds > 120:
        reasons.append("Long gaps between events (> 2 minutes)")
    
    if metrics.unique_pages == 1 and metrics.event_count > 20:
        reasons.append("Many events on single page (possible bot)")
    
    events_per_second = metrics.event_count / max(metrics.duration_seconds, 1)
    if events_per_second > 2:
        reasons.append(f"High event frequency ({events_per_second:.1f} events/second)")
    
    if not reasons:
        reasons.append("Session pattern deviates from normal behavior")
    
    return reasons
