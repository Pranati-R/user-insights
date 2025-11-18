from datetime import datetime, timedelta, timezone

from app.services.metrics import compute_metrics


def test_compute_metrics_basic():
    now = datetime.now(timezone.utc)
    events = [
        {"timestamp": now, "event_type": "page_view", "page": "/"},
        {"timestamp": now + timedelta(seconds=10), "event_type": "click"},
        {
            "timestamp": now + timedelta(seconds=20),
            "event_type": "action",
            "metadata": {"action": "purchase"},
        },
    ]

    metrics = compute_metrics(events)

    assert metrics.event_count == 3
    assert metrics.duration_seconds == 20
    assert metrics.unique_pages == 1


