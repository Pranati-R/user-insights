from joblib import load
import numpy as np

model = load("../app/models/local_iforest.pkl")

# extreme anomaly: 50 events in 1 second
features = np.array([[1, 50, 10, 10, 5, 0.01, 0.1]])

print(model.decision_function(features))
