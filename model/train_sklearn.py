import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score
from sklearn.neural_network import MLPClassifier

# ── Paths ──────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '..', 'data', 'bugs.csv')
MODEL_DIR = os.path.join(BASE_DIR, '..', 'model')

# ── Load Data ──────────────────────────────────────
print("Loading data...")
df = pd.read_csv(DATA_PATH)
df['browser'] = df['browser'].fillna('N/A')
df = df.drop(columns=['bug_id', 'created_at', 'resolved_at'])

# ── Encode ─────────────────────────────────────────
cat_cols = ['bug_type', 'component', 'environment', 'platform',
            'operating_system', 'browser', 'reporter_role', 'module', 'status']

encoders = {}
for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

target_le = LabelEncoder()
df['severity'] = target_le.fit_transform(df['severity'])
print("Classes:", target_le.classes_)

# ── Scale ──────────────────────────────────────────
feature_cols = [c for c in df.columns if c != 'severity']
X = df[feature_cols].values
y = df['severity'].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ── Split ──────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

num_classes = len(target_le.classes_)

# ── Build Model ────────────────────────────────────
# TensorFlow Sequential (256→128→64→32) ke equivalent MLPClassifier architecture
# Dropout/BatchNorm sklearn mein nahi hote — inki jagah alpha (L2 regularization)
# aur early_stopping use kiya hai overfitting rokne ke liye.
model = MLPClassifier(
    hidden_layer_sizes=(256, 128, 64, 32),
    activation='relu',
    solver='adam',
    alpha=0.001,                 # L2 regularization (dropout jaisa effect)
    batch_size=64,
    learning_rate_init=0.001,
    max_iter=300,
    early_stopping=True,         # EarlyStopping ke equivalent
    validation_fraction=0.2,
    n_iter_no_change=10,         # patience=10 jaisa
    random_state=42,
    verbose=True
)

# ── Train ──────────────────────────────────────────
print("Training started...")
model.fit(X_train, y_train)

# ── Evaluate ───────────────────────────────────────
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\nTest Accuracy: {acc*100:.2f}%")

print(classification_report(y_test, y_pred,
      target_names=target_le.classes_))

# ── Save ───────────────────────────────────────────
os.makedirs(MODEL_DIR, exist_ok=True)

with open(os.path.join(MODEL_DIR, 'model_sklearn.pkl'), 'wb') as f:
    pickle.dump(model, f)

with open(os.path.join(MODEL_DIR, 'scaler.pkl'), 'wb') as f:
    pickle.dump(scaler, f)

with open(os.path.join(MODEL_DIR, 'label_encoder.pkl'), 'wb') as f:
    pickle.dump({'features': encoders, 'target': target_le}, f)

print("\nAll artifacts saved! ✅")
print("Files created: model_sklearn.pkl, scaler.pkl, label_encoder.pkl")