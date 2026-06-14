import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.utils import to_categorical

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
y_train_cat = to_categorical(y_train, num_classes=num_classes)
y_test_cat = to_categorical(y_test, num_classes=num_classes)

# ── Build Model ────────────────────────────────────
model = Sequential([
    Dense(256, activation='relu', input_shape=(X_train.shape[1],)),
    BatchNormalization(), Dropout(0.3),
    Dense(128, activation='relu'),
    BatchNormalization(), Dropout(0.3),
    Dense(64, activation='relu'),
    BatchNormalization(), Dropout(0.2),
    Dense(32, activation='relu'), Dropout(0.2),
    Dense(num_classes, activation='softmax')
])

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# ── Train ──────────────────────────────────────────
callbacks = [
    EarlyStopping(monitor='val_loss', patience=10,
                  restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                      patience=5, verbose=1)
]

print("Training started...")
model.fit(X_train, y_train_cat, epochs=100, batch_size=64,
          validation_split=0.2, callbacks=callbacks, verbose=1)

# ── Evaluate ───────────────────────────────────────
_, acc = model.evaluate(X_test, y_test_cat, verbose=0)
print(f"\nTest Accuracy: {acc*100:.2f}%")

y_pred = np.argmax(model.predict(X_test), axis=1)
print(classification_report(y_test, y_pred,
      target_names=target_le.classes_))

# ── Save ───────────────────────────────────────────
os.makedirs(MODEL_DIR, exist_ok=True)
model.save(os.path.join(MODEL_DIR, 'model.keras'))

with open(os.path.join(MODEL_DIR, 'scaler.pkl'), 'wb') as f:
    pickle.dump(scaler, f)

with open(os.path.join(MODEL_DIR, 'label_encoder.pkl'), 'wb') as f:
    pickle.dump({'features': encoders, 'target': target_le}, f)

print("\nAll artifacts saved! ✅")