import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ----------------------------
# Load Dataset
# ----------------------------
df = pd.read_csv("data/insider_logs.csv")

print("Dataset Loaded Successfully!\n")

# ----------------------------
# Encode Role Column
# ----------------------------
encoder = LabelEncoder()
df["role"] = encoder.fit_transform(df["role"])

# Save encoder for future predictions
joblib.dump(encoder, "models/label_encoder.pkl")

# ----------------------------
# Split Features and Target
# ----------------------------
X = df.drop("risk", axis=1)
y = df["risk"]

# ----------------------------
# Train-Test Split
# ----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# ----------------------------
# Train Model
# ----------------------------
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# ----------------------------
# Predictions
# ----------------------------
predictions = model.predict(X_test)

# ----------------------------
# Accuracy
# ----------------------------
accuracy = accuracy_score(y_test, predictions)

print("=" * 50)
print(f"Model Accuracy : {accuracy * 100:.2f}%")
print("=" * 50)

print("\nClassification Report\n")
print(classification_report(y_test, predictions))

print("\nConfusion Matrix\n")
print(confusion_matrix(y_test, predictions))

# ----------------------------
# Save Model
# ----------------------------
joblib.dump(model, "models/model.pkl")

print("\nModel saved successfully!")

print("\nLabel Encoder saved successfully!")