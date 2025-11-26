"""
Train an improved anomaly detection model on historical session data.
This script trains multiple models and saves the best performing one.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import joblib
import numpy as np
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from pyod.models.iforest import IForest
from pyod.models.lof import LOF
from pyod.models.knn import KNN
from pyod.models.cblof import CBLOF

from app.core.config import get_settings
from app.schemas.analytics import SessionMetrics

settings = get_settings()


async def fetch_session_data():
    """Fetch all session data from MongoDB"""
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_db]
    sessions_collection = db[settings.sessions_collection]
    
    sessions = await sessions_collection.find({}).to_list(length=None)
    print(f"Fetched {len(sessions)} sessions from database")
    
    await client.close()
    return sessions


def extract_features(sessions):
    """Extract feature vectors from sessions"""
    features = []
    labels = []  # 1 for anomaly, 0 for normal
    
    for session in sessions:
        metrics = session.get('metrics', {})
        if not metrics:
            continue
        
        # Build feature vector (same as in ml_service.py)
        feature_vector = [
            metrics.get('duration_seconds', 0),
            metrics.get('event_count', 0),
            metrics.get('click_rate', 0),
            metrics.get('unique_pages', 0),
            metrics.get('action_diversity', 0),
            metrics.get('avg_inter_event_seconds', 0),
            metrics.get('dwell_estimate_seconds', 0),
            # Derived features
            metrics.get('event_count', 0) / max(metrics.get('duration_seconds', 1), 1),
            metrics.get('unique_pages', 0) / max(metrics.get('event_count', 1), 1),
            metrics.get('click_rate', 0) * metrics.get('event_count', 0),
        ]
        
        features.append(feature_vector)
        labels.append(1 if session.get('is_anomalous', False) else 0)
    
    return np.array(features), np.array(labels)


def train_models(X_train, X_test, contamination=0.05):
    """Train multiple anomaly detection models"""
    models = {
        'IsolationForest': IForest(
            contamination=contamination,
            n_estimators=200,
            max_samples=256,
            random_state=42,
            behaviour='new'
        ),
        'LOF': LOF(
            contamination=contamination,
            n_neighbors=20,
            novelty=False
        ),
        'KNN': KNN(
            contamination=contamination,
            n_neighbors=5,
            method='largest'
        ),
        'CBLOF': CBLOF(
            contamination=contamination,
            n_clusters=8,
            random_state=42
        ),
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train)
        
        # Evaluate on test set
        test_scores = model.decision_function(X_test)
        test_predictions = model.predict(X_test)
        
        results[name] = {
            'model': model,
            'test_scores': test_scores,
            'test_predictions': test_predictions,
            'anomaly_count': np.sum(test_predictions == 1)
        }
        
        print(f"{name} - Detected {results[name]['anomaly_count']} anomalies in test set")
    
    return results


def evaluate_models(results, y_test=None):
    """Evaluate and compare models"""
    print("\n" + "="*60)
    print("MODEL EVALUATION SUMMARY")
    print("="*60)
    
    for name, result in results.items():
        anomaly_rate = (result['anomaly_count'] / len(result['test_predictions'])) * 100
        print(f"\n{name}:")
        print(f"  Anomalies detected: {result['anomaly_count']}")
        print(f"  Anomaly rate: {anomaly_rate:.2f}%")
        print(f"  Score range: [{result['test_scores'].min():.3f}, {result['test_scores'].max():.3f}]")
        
        if y_test is not None:
            # Calculate accuracy if we have labels
            accuracy = np.mean(result['test_predictions'] == y_test)
            print(f"  Accuracy: {accuracy:.2%}")


def save_best_model(results, scaler, output_path):
    """Save the best performing model"""
    # For now, use IsolationForest as it's most reliable
    best_model_name = 'IsolationForest'
    best_model = results[best_model_name]['model']
    
    # Create models directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save model
    joblib.dump(best_model, output_path)
    print(f"\n✓ Saved {best_model_name} model to {output_path}")
    
    # Save scaler
    scaler_path = output_path.parent / "scaler.pkl"
    joblib.dump(scaler, scaler_path)
    print(f"✓ Saved scaler to {scaler_path}")
    
    # Save metadata
    metadata = {
        'model_type': best_model_name,
        'trained_at': datetime.now().isoformat(),
        'n_features': 10,
        'contamination': best_model.contamination,
        'feature_names': [
            'duration_seconds',
            'event_count',
            'click_rate',
            'unique_pages',
            'action_diversity',
            'avg_inter_event_seconds',
            'dwell_estimate_seconds',
            'events_per_second',
            'page_diversity',
            'total_clicks',
        ]
    }
    
    metadata_path = output_path.parent / "model_metadata.txt"
    with open(metadata_path, 'w') as f:
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")
    print(f"✓ Saved metadata to {metadata_path}")


async def main():
    """Main training pipeline"""
    print("="*60)
    print("ANOMALY DETECTION MODEL TRAINING")
    print("="*60)
    
    # 1. Fetch data
    print("\n[1/5] Fetching session data from database...")
    sessions = await fetch_session_data()
    
    if len(sessions) < 100:
        print(f"\n⚠ Warning: Only {len(sessions)} sessions found.")
        print("For best results, train on at least 1000 sessions.")
        print("Proceeding with available data...")
    
    # 2. Extract features
    print("\n[2/5] Extracting features...")
    X, y = extract_features(sessions)
    print(f"Extracted {len(X)} feature vectors")
    print(f"Feature shape: {X.shape}")
    print(f"Anomalies in dataset: {np.sum(y)} ({np.mean(y)*100:.2f}%)")
    
    # 3. Normalize features
    print("\n[3/5] Normalizing features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
    )
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # 4. Train models
    print("\n[4/5] Training models...")
    contamination = np.mean(y) if np.mean(y) > 0 else 0.05
    print(f"Using contamination rate: {contamination:.3f}")
    
    results = train_models(X_train, X_test, contamination=contamination)
    
    # 5. Evaluate and save
    print("\n[5/5] Evaluating models...")
    evaluate_models(results, y_test)
    
    # Save best model
    output_path = Path("app/models/local_iforest.pkl")
    save_best_model(results, scaler, output_path)
    
    print("\n" + "="*60)
    print("✓ TRAINING COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Restart your backend server to load the new model")
    print("2. Test the model on new uploads")
    print("3. Monitor anomaly detection performance")
    print("\nTo retrain with more data, simply run this script again.")


if __name__ == "__main__":
    asyncio.run(main())
