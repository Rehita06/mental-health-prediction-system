# inference/utils.py
import os, joblib, json
from pathlib import Path

_MODEL = None
_META = None

def get_model_and_meta(models_dir=None):
    global _MODEL, _META
    if models_dir is None:
        models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
    models_dir = Path(models_dir)
    model_path = models_dir / 'best_model.joblib'
    meta_path = models_dir / 'metadata.json'
    if not model_path.exists() or not meta_path.exists():
        raise FileNotFoundError('Model or metadata not found. Train model first by running ml/train.py or calling /api/train/.')
    if _MODEL is None:
        _MODEL = joblib.load(model_path)
    if _META is None:
        with open(meta_path, 'r') as f:
            _META = json.load(f)
    return _MODEL, _META


RISK_DESCRIPTIONS = {
    "low": {
        "description": "Your mental health risk is low.",
        "recommendation": "Keep maintaining a healthy lifestyle and regular self-care."
    },
    "medium": {
        "description": "You might be experiencing some mental health concerns.",
        "recommendation": "Consider talking to a counselor or practicing stress management techniques."
    },
    "high": {
        "description": "Your mental health risk appears high.",
        "recommendation": "We strongly recommend consulting a mental health professional soon."
    }
}

def get_recommendation(prediction_label):
    """Return description and recommendation for a prediction label."""
    return RISK_DESCRIPTIONS.get(prediction_label.lower(), {
        "description": "Prediction unavailable",
        "recommendation": "No recommendations available."
    })
