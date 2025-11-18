import random
from datetime import datetime, timedelta

PAGES = ["/", "/pricing", "/login", "/settings", "/dashboard", "/product"]
ACTIONS = ["signup", "share", "buy", "click", "download"]


# -----------------------------------------
# Helper functions
# -----------------------------------------
def ts(prev, min_gap=1, max_gap=25):
    return prev + timedelta(seconds=random.randint(min_gap, max_gap))


def ts_fast(prev):
    return prev + timedelta(milliseconds=random.randint(5, 120))


# ------------------------------
# Normal Session (Realistic)
# ------------------------------
def generate_normal_session(user_id):
    start = datetime.now() - timedelta(days=random.randint(0, 7))
    events = []

    event_count = random.randint(3, 7)

    for _ in range(event_count):
        if random.random() < 0.65:
            events.append({
                "user_id": user_id,
                "type": "page_view",
                "page": random.choice(PAGES),
                "action": None,
                "timestamp": ts(start).isoformat()
            })
        else:
            events.append({
                "user_id": user_id,
                "type": "action",
                "page": None,
                "action": random.choice(ACTIONS),
                "timestamp": ts(start).isoformat()
            })

        start = datetime.fromisoformat(events[-1]["timestamp"])

    return events


# ------------------------------
# REAL-WORLD ANOMALIES
# ------------------------------
def generate_anomaly(user_id):
    start = datetime.now()
    events = []

    anomaly = random.choice([
        "rage_clicks",
        "click_burst",
        "scroll_spam",
        "fast_tab_switch",
        "idle_dead_session",
        "action_abuse",
        "loop_navigation",
        "broken_session",
        "chaos",
    ])

    # 1. Rage Clicks – 20–40 clicks in <1 second
    if anomaly == "rage_clicks":
        for _ in range(random.randint(20, 40)):
            events.append({
                "user_id": user_id,
                "type": "click",
                "page": None,
                "action": None,
                "timestamp": ts_fast(start).isoformat()
            })
            start = datetime.fromisoformat(events[-1]["timestamp"])

    # 2. Click burst
    elif anomaly == "click_burst":
        for _ in range(random.randint(30, 50)):
            events.append({
                "user_id": user_id,
                "type": "action",
                "page": None,
                "action": "click",
                "timestamp": ts_fast(start).isoformat()
            })
            start = datetime.fromisoformat(events[-1]["timestamp"])

    # 3. Scroll spam – 15 scroll events in <1 second
    elif anomaly == "scroll_spam":
        for _ in range(random.randint(10, 20)):
            events.append({
                "user_id": user_id,
                "type": "scroll",
                "page": "/",
                "action": None,
                "timestamp": ts_fast(start).isoformat()
            })
            start = datetime.fromisoformat(events[-1]["timestamp"])

    # 4. Ultra fast tab switching
    elif anomaly == "fast_tab_switch":
        pages = random.choices(PAGES, k=12)
        for p in pages:
            events.append({
                "user_id": user_id,
                "type": "page_view",
                "page": p,
                "action": None,
                "timestamp": ts_fast(start).isoformat()
            })
            start = datetime.fromisoformat(events[-1]["timestamp"])

    # 5. Idle then sudden event (broken UX)
    elif anomaly == "idle_dead_session":
        events.append({
            "user_id": user_id,
            "type": "page_view",
            "page": "/settings",
            "action": None,
            "timestamp": start.isoformat()
        })
        idle = start + timedelta(minutes=random.randint(45, 120))
        events.append({
            "user_id": user_id,
            "type": "click",
            "page": None,
            "action": None,
            "timestamp": idle.isoformat()
        })

    # 6. Action-only API abuse
    elif anomaly == "action_abuse":
        for _ in range(random.randint(8, 20)):
            events.append({
                "user_id": user_id,
                "type": "action",
                "page": None,
                "action": random.choice(ACTIONS),
                "timestamp": ts_fast(start).isoformat()
            })
            start = datetime.fromisoformat(events[-1]["timestamp"])

    # 7. Loop navigation – impossible human pattern
    elif anomaly == "loop_navigation":
        for _ in range(10):
            for p in ["/pricing", "/settings"]:
                events.append({
                    "user_id": user_id,
                    "type": "page_view",
                    "page": p,
                    "action": None,
                    "timestamp": ts_fast(start).isoformat()
                })
                start = datetime.fromisoformat(events[-1]["timestamp"])

    # 8. Broken short session – too few events
    elif anomaly == "broken_session":
        events.append({
            "user_id": user_id,
            "type": "click",
            "page": None,
            "action": None,
            "timestamp": start.isoformat()
        })

    # 9. Chaos – completely random
    elif anomaly == "chaos":
        for _ in range(random.randint(15, 30)):
            events.append({
                "user_id": user_id,
                "type": random.choice(["page_view", "click", "action"]),
                "page": random.choice(PAGES),
                "action": random.choice(ACTIONS),
                "timestamp": ts_fast(start).isoformat()
            })
            start = datetime.fromisoformat(events[-1]["timestamp"])

    return events


# -----------------------------------------
# RANDOM ANOMALOUS SESSION
# -----------------------------------------
def generate_anomaly2(user_id):
    """Creates a *general* anomaly with randomness (no categories)."""

    # Random choice of anomaly behavior
    anomaly_type = random.choice([
        "fast_clicks",
        "too_many_events",
        "action_only",
        "weird_navigation",
        "idle_gap",
        "mixed_random",
    ])

    start = datetime.now()
    events = []

    if anomaly_type == "fast_clicks":
        # Many events too fast
        for _ in range(random.randint(10, 18)):
            events.append({
                "user_id": user_id,
                "type": random.choice(["page_view", "action"]),
                "page": random.choice(PAGES),
                "action": random.choice(ACTIONS),
                "timestamp": ts_fast(start).isoformat()
            })
            start = datetime.fromisoformat(events[-1]["timestamp"])

    elif anomaly_type == "too_many_events":
        for _ in range(random.randint(15, 25)):
            events.append({
                "user_id": user_id,
                "type": random.choice(["page_view", "action"]),
                "page": random.choice(PAGES),
                "action": random.choice(ACTIONS),
                "timestamp": ts(start, 0, 5).isoformat()
            })
            start = datetime.fromisoformat(events[-1]["timestamp"])

    elif anomaly_type == "action_only":
        for _ in range(random.randint(5, 10)):
            events.append({
                "user_id": user_id,
                "type": "action",
                "page": None,
                "action": random.choice(ACTIONS),
                "timestamp": ts(start).isoformat()
            })
            start = datetime.fromisoformat(events[-1]["timestamp"])

    elif anomaly_type == "weird_navigation":
        pages = random.sample(PAGES, len(PAGES))
        for p in pages:
            events.append({
                "user_id": user_id,
                "type": "page_view",
                "page": p,
                "action": None,
                "timestamp": ts(start, 1, 5).isoformat()
            })
            start = datetime.fromisoformat(events[-1]["timestamp"])

    elif anomaly_type == "idle_gap":
        events.append({
            "user_id": user_id,
            "type": "page_view",
            "page": "/settings",
            "action": None,
            "timestamp": start.isoformat()
        })

        # 1–3 hour idle gap
        start = start + timedelta(hours=random.randint(1, 3))

        events.append({
            "user_id": user_id,
            "type": "action",
            "page": None,
            "action": random.choice(ACTIONS),
            "timestamp": start.isoformat()
        })

    elif anomaly_type == "mixed_random":
        for _ in range(random.randint(8, 14)):
            events.append({
                "user_id": user_id,
                "type": random.choice(["page_view", "action"]),
                "page": random.choice(PAGES),
                "action": random.choice(ACTIONS),
                "timestamp": ts(start).isoformat()
            })
            start = datetime.fromisoformat(events[-1]["timestamp"])

    return events


# -----------------------------------------
# FINAL DATASET (simple)
# -----------------------------------------
def generate_dataset(n_normal=300, n_anomalies=80):
    data = []

    for i in range(n_normal):
        data.append(generate_normal_session(f"user-{i}"))

    for i in range(n_anomalies):
        data.append(generate_anomaly(f"anomaly-{i}"))
    j= i + 1   
    for i in range(n_anomalies):
        data.append(generate_anomaly2(f"anomaly-{i+j}"))

    return data
