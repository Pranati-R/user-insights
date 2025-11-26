import numpy as np
import joblib
from datetime import datetime

from pyod.models.iforest import IForest

from generate_training_data import generate_dataset


# -------------------------------------------
# Feature Extractor
# -------------------------------------------
def extract_session_features(events):
    if not events:
        return None

    events = sorted(events, key=lambda e: e["timestamp"])
    timestamps = [
        datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00"))
        for e in events
    ]

    duration = (timestamps[-1] - timestamps[0]).total_seconds()
    event_count = len(events)

    pages = [e.get("page") for e in events if e["type"] == "page_view"]
    actions = [e.get("action") for e in events if e["type"] == "action"]

    click_rate = len(actions) / max(1, event_count)
    unique_pages = len(set(pages)) if pages else 0
    action_diversity = len(set(actions)) if actions else 0

    gaps = [
        (timestamps[i + 1] - timestamps[i]).total_seconds()
        for i in range(len(timestamps) - 1)
    ]
    avg_gap = np.mean(gaps) if gaps else 0

    dwell_estimate = duration / max(1, unique_pages) if unique_pages else duration

    return np.array([
        duration,
        event_count,
        click_rate,
        unique_pages,
        action_diversity,
        avg_gap,
        dwell_estimate
    ])


# -------------------------------------------
# Training Script
# -------------------------------------------
def main():
    print("\nGenerating synthetic dataset...")
    sessions = generate_dataset(n_normal=3000,  n_anomalies=1000)

    print("Extracting features...")
    X = []
    for session in sessions:
        fv = extract_session_features(session)
        if fv is not None:
            X.append(fv)

    X = np.array(X)
    print(f"Training samples: {X.shape[0]}")

    print("\nTraining PyOD IsolationForest...")
    model = IForest(contamination=0.12, random_state=42)
    model.fit(X)

    print("\nSaving model → models/local_iforest.pkl")
    Path("models").mkdir(exist_ok=True)
    joblib.dump(model, "models/local_iforest.pkl")

    print("Done!")


if __name__ == "__main__":
    from pathlib import Path
    main()
