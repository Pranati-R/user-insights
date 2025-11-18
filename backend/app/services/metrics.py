from __future__ import annotations

from collections import Counter

from app.schemas.analytics import SessionMetrics
from app.schemas.events import EventType


def compute_metrics(events: list[dict]) -> SessionMetrics:
    if not events:
        raise ValueError("Cannot compute metrics for empty event list")

    timestamps = sorted(event["timestamp"] for event in events)
    duration = (timestamps[-1] - timestamps[0]).total_seconds() or 1.0

    click_count = sum(1 for event in events if event.get("event_type") == EventType.CLICK.value)
    event_count = len(events)
    click_rate = click_count / event_count

    pages = {event.get("page") for event in events if event.get("page")}
    actions = Counter(
        (
            event.get("metadata", {}).get("action")
            or event.get("action")
        )
        for event in events
        if event.get("metadata", {}).get("action") or event.get("action")
    )

    inter_event = []
    for first, second in zip(timestamps, timestamps[1:]):
        inter_event.append((second - first).total_seconds())

    avg_inter_event = sum(inter_event) / len(inter_event) if inter_event else duration
    dwell_estimate = duration / max(len(pages), 1)

    return SessionMetrics(
        duration_seconds=duration,
        event_count=event_count,
        click_rate=click_rate,
        unique_pages=len(pages),
        action_diversity=len(actions),
        avg_inter_event_seconds=avg_inter_event,
        dwell_estimate_seconds=dwell_estimate,
    )


