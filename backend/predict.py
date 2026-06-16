"""
predict.py — Bug Severity Prediction Logic (scikit-learn version)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pickle

# ── Paths ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, '..', 'model')

# ── Globals (ek baar load hoga, baar baar use hoga) ──
_model = None
_scaler = None
_encoders = None
_target_le = None

# Feature order EXACTLY wahi jo training mein thi (processed_bugs.csv ke order ke according)
FEATURE_ORDER = [
    'bug_type', 'component', 'environment', 'platform',
    'operating_system', 'browser', 'reporter_role', 'module', 'status',
    'affected_users', 'response_time_ms', 'error_code',
    'business_impact_score', 'reproduction_rate', 'memory_usage_mb',
    'cpu_usage_pct', 'lines_of_code', 'open_issues_count', 'fix_time_hours',
    'num_comments', 'num_attachments', 'sprint_number', 'test_coverage_pct',
    'reopen_count', 'num_linked_bugs', 'api_call_count', 'db_query_time_ms',
    'is_regression', 'is_security_related', 'has_workaround',
    'customer_reported', 'sla_breached'
]
CAT_COLS = ['bug_type', 'component', 'environment', 'platform',
            'operating_system', 'browser', 'reporter_role', 'module', 'status']
DEFAULTS = {
    'lines_of_code':     25000,
    'open_issues_count': 250,
    'num_comments':      25,
    'num_attachments':   5,
    'sprint_number':     25,
    'test_coverage_pct': 50.0,
    'num_linked_bugs':   5,
    'api_call_count':    500,
    'db_query_time_ms':  1500,
    'is_regression':     0,
    'has_workaround':    0,
    'error_code':        350
}
SEVERITY_COLORS = {
    'Critical': '#e74c3c',
    'High':     '#e67e22',
    'Medium':   '#f1c40f',
    'Low':      '#2ecc71',
}


def _load_artifacts():
    """Model + scaler + encoders ek baar load karo"""
    global _model, _scaler, _encoders, _target_le
    if _model is None:
        with open(os.path.join(MODEL_DIR, 'model_sklearn.pkl'), 'rb') as f:
            _model = pickle.load(f)
        with open(os.path.join(MODEL_DIR, 'scaler.pkl'), 'rb') as f:
            _scaler = pickle.load(f)
        with open(os.path.join(MODEL_DIR, 'label_encoder.pkl'), 'rb') as f:
            data = pickle.load(f)
            _encoders = data['features']
            _target_le = data['target']


def predict_severity(input_dict: dict) -> dict:
    _load_artifacts()
    for k, v in DEFAULTS.items():
        if k not in input_dict or input_dict[k] is None:
            input_dict[k] = v

    row = {}
    for feat in FEATURE_ORDER:
        val = input_dict.get(feat)
        if feat in CAT_COLS:
            le = _encoders[feat]
            if val not in le.classes_:
                val = le.classes_[0]
            row[feat] = le.transform([val])[0]
        else:
            row[feat] = float(val) if val is not None else 0.0

    X        = np.array([[row[f] for f in FEATURE_ORDER]])
    X_scaled = _scaler.transform(X)

    probs           = _model.predict_proba(X_scaled)[0]
    predicted_idx    = int(np.argmax(probs))
    predicted_label  = _target_le.inverse_transform([predicted_idx])[0]
    confidence       = float(probs[predicted_idx]) * 100

    all_probs = {
        cls: round(float(p) * 100, 2)
        for cls, p in zip(_target_le.classes_, probs)
    }

    return {
        'predicted_severity': predicted_label,
        'confidence':         round(confidence, 2),
        'all_probabilities':  all_probs,
        'color':              SEVERITY_COLORS.get(predicted_label, '#999999')
    }
