import random
import joblib
import numpy as np
from tqdm import tqdm
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest

# -----------------------------
# Constants
# -----------------------------
PAGES = ["/", "/pricing", "/login", "/settings", "/dashboard", "/product"]
ACTIONS = ["signup", "share", "buy", "click", "download"]


# -------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------
def ts(prev, min_gap=1, max_gap=25):
    return prev + timedelta(seconds=random.randint(min_gap, max_gap))

def ts_fast(prev):
    return prev + timedelta(milliseconds=random.randint(5, 120))


# -------------------------------------------------------
# NORMAL SESSION (Realistic)
# -------------------------------------------------------
def generate_normal_session(user_id):
    start = start0 = datetime.now() - timedelta(days=random.randint(0, 7))
    events = []

    for _ in range(random.randint(3, 7)):
        if random.random() < 0.65:
            events.append(("page_view", random.choice(PAGES), None, ts(start)))
        else:
            events.append(("action", None, random.choice(ACTIONS), ts(start)))
        start = events[-1][3]

    return events


# -------------------------------------------------------
# ANOMALIES (Real realistic patterns)
# -------------------------------------------------------
def generate_anomaly(user_id):
    start = datetime.now()
    events = []

    anomaly = random.choice([
        "rage_clicks", "click_burst", "scroll_spam",
        "fast_tab_switch", "idle_dead_session",
        "action_abuse", "loop_navigation",
        "broken_session", "chaos"
    ])

    if anomaly == "rage_clicks":
        for _ in range(random.randint(20, 40)):
            events.append(("click", None, None, ts_fast(start)))
            start = events[-1][3]

    elif anomaly == "click_burst":
        for _ in range(random.randint(30, 50)):
            events.append(("action", None, "click", ts_fast(start)))
            start = events[-1][3]

    elif anomaly == "scroll_spam":
        for _ in range(15):
            events.append(("scroll", "/", None, ts_fast(start)))
            start = events[-1][3]

    elif anomaly == "fast_tab_switch":
        for p in random.choices(PAGES, k=12):
            events.append(("page_view", p, None, ts_fast(start)))
            start = events[-1][3]

    elif anomaly == "idle_dead_session":
        events.append(("page_view", "/settings", None, start))
        start = start + timedelta(minutes=random.randint(45, 120))
        events.append(("click", None, None, start))

    elif anomaly == "action_abuse":
        for _ in range(random.randint(8, 20)):
            events.append(("action", None, random.choice(ACTIONS), ts_fast(start)))
            start = events[-1][3]

    elif anomaly == "loop_navigation":
        for _ in range(10):
            for p in ["/pricing", "/settings"]:
                events.append(("page_view", p, None, ts_fast(start)))
                start = events[-1][3]

    elif anomaly == "broken_session":
        events.append(("click", None, None, start))

    elif anomaly == "chaos":
        for _ in range(random.randint(15, 30)):
            events.append((
                random.choice(["page_view", "click", "action"]),
                random.choice(PAGES),
                random.choice(ACTIONS),
                ts_fast(start),
            ))
            start = events[-1][3]

    return events


# -------------------------------------------------------
# FEATURE EXTRACTION FOR EACH SESSION
# -------------------------------------------------------
def extract_features(events):
    if not events:
        return [0] * 10

    timestamps = [e[3] for e in events]
    duration = (timestamps[-1] - timestamps[0]).total_seconds()
    duration = max(duration, 1)

    types = [e[0] for e in events]
    pages = [e[1] for e in events if e[1]]
    actions = [e[2] for e in events if e[2]]

    event_count = len(events)
    click_count = types.count("click") + actions.count("click")

    unique_pages = len(set(pages))
    action_diversity = len(set(actions))

    inter_times = []
    for i in range(1, len(timestamps)):
        inter_times.append((timestamps[i] - timestamps[i - 1]).total_seconds())

    avg_inter_event = sum(inter_times) / len(inter_times) if inter_times else duration

    dwell_time = duration / max(unique_pages, 1)

    # Engineered features
    events_per_sec = event_count / duration
    page_diversity_ratio = unique_pages / max(event_count, 1)
    total_clicks = click_count

    return [
        duration,
        event_count,
        click_count / max(event_count, 1),  # click_rate
        unique_pages,
        action_diversity,
        avg_inter_event,
        dwell_time,
        events_per_sec,
        page_diversity_ratio,
        total_clicks,
    ]

def generate_stronger_anomaly(user_id):
    start = datetime.now()
    events = []

    anomaly = random.choice([
        "super_rage_clicks",
        "ultrafast_bot",
        "mass_navigation",
        "mass_actions",
        "long_idle_then_burst",
        "zero_dwell_bot",
        "chaotic_superbot",
    ])

    # 1. 80–150 clicks in <1 second (extreme rage clicking)
    if anomaly == "super_rage_clicks":
        for _ in range(random.randint(80, 150)):
            events.append(("click", None, None, ts_fast(start)))
            start = events[-1][3]

    # 2. Bot that switches pages every 5–15 ms (inhuman)
    elif anomaly == "ultrafast_bot":
        for _ in range(40):
            events.append(("page_view", random.choice(PAGES), None, ts_fast(start)))
            start = events[-1][3]

    # 3. User visits 20–40 unique pages (crawler bot)
    elif anomaly == "mass_navigation":
        for p in [f"/p/{i}" for i in range(random.randint(20, 40))]:
            events.append(("page_view", p, None, ts(start, 0, 1)))
            start = events[-1][3]

    # 4. Many different action types (API abuse)
    elif anomaly == "mass_actions":
        for _ in range(random.randint(30, 80)):
            events.append(("action", None, random.choice(ACTIONS), ts_fast(start)))
            start = events[-1][3]

    # 5. Idle for 2–4 hours then a burst of events
    elif anomaly == "long_idle_then_burst":
        events.append(("page_view", "/home", None, start))
        idle = start + timedelta(hours=random.randint(2, 4))
        for _ in range(random.randint(10, 20)):
            events.append(("click", None, None, ts_fast(idle)))
            idle = events[-1][3]

    # 6. Zero dwell time bot (all events in <300 ms)
    elif anomaly == "zero_dwell_bot":
        for _ in range(random.randint(20, 50)):
            events.append((random.choice(["page_view","click","action"]),
                           random.choice(PAGES),
                           random.choice(ACTIONS),
                           ts_fast(start)))
            start = events[-1][3]

    # 7. Extreme chaos bot (random flood)
    elif anomaly == "chaotic_superbot":
        for _ in range(random.randint(60, 120)):
            events.append((random.choice(["page_view","click","action","scroll"]),
                           random.choice(PAGES),
                           random.choice(ACTIONS),
                           ts_fast(start)))
            start = events[-1][3]

    return events

# -------------------------------------------------------
# GENERATE DATASET
# -------------------------------------------------------
def generate_dataset(n_normal=5000, n_anomalies=4000):
    X = []
    y = []

    for i in tqdm(range(n_normal)):
        sess = generate_normal_session(f"user-{i}")
        X.append(extract_features(sess))
        y.append(1)

    for i in tqdm(range(n_anomalies)):
        sess = generate_anomaly(f"anom-{i}")
        X.append(extract_features(sess))
        y.append(-1)

    for i in range(n_anomalies):
        sess = generate_stronger_anomaly(f"anom-{i}")
        X.append(extract_features(sess))
        y.append(-1)    

    return np.array(X), np.array(y)


# -------------------------------------------------------
# TRAIN MODEL
# -------------------------------------------------------
print("Generating dataset...")
X, y = generate_dataset()

print("Training IsolationForest with 10 features...")
model = IsolationForest(
    contamination=0.2,
    n_estimators=600,
    max_samples=256,
    bootstrap=True,
    random_state=42
)

model.fit(X)

print("Saving model...")
joblib.dump(model, "app/models/local_iforest.pkl")

print("DONE. Model saved as local_iforest.pkl")
