import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load training data
data = pd.read_csv("../training_data.csv")

# Features used by AI
features = [
    "violation_count",
    "overdue_actions",
    "inspection_score",
    "maintenance_delay_days",
    "equipment_failure_count",
    "contractor_violations",
    "contractor_compliance_score",
    "environmental_issues"
]

X = data[features]
y = data["risk_level"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create AI model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Train
model.fit(X_train, y_train)

# Test
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Save trained model
joblib.dump(model, "risk_model.pkl")

print("AI Risk Model saved successfully!")

# Test AI with a new mine
new_mine = [[
    6,    # violations
    4,    # overdue actions
    70,   # inspection score
    12,   # maintenance delay
    3,    # equipment failures
    4,    # contractor violations
    65,   # contractor compliance
    5     # environmental issues
]]

prediction = model.predict(new_mine)

print("Predicted Risk Level:", prediction[0])

# Test AI with a new mine
new_mine = [[
    6, 4, 70, 12, 3, 4, 65, 5
]]

prediction = model.predict(new_mine)
probability = model.predict_proba(new_mine)

risk_level = prediction[0]
confidence = max(probability[0]) * 100

print("Predicted Risk Level:", risk_level)
print(f"AI Confidence: {confidence:.2f}%")

# Show important risk drivers
importance = model.feature_importances_

risk_drivers = sorted(
    zip(features, importance),
    key=lambda x: x[1],
    reverse=True
)

print("\nTop Risk Drivers:")

for feature, score in risk_drivers[:4]:
    print(f"- {feature}: {score:.2f}")

# AI Explanation and Recommendation

print("\nAI GOVERNANCE RECOMMENDATION")

recommendations = []

if new_mine[0][0] >= 5:
    recommendations.append("Investigate repeated compliance violations")

if new_mine[0][1] >= 3:
    recommendations.append("Close overdue corrective actions immediately")

if new_mine[0][2] < 75:
    recommendations.append("Schedule a priority safety inspection")

if new_mine[0][3] >= 10:
    recommendations.append("Perform overdue equipment maintenance")

if new_mine[0][4] >= 3:
    recommendations.append("Inspect high-failure equipment")

if new_mine[0][5] >= 3:
    recommendations.append("Review contractor compliance")

if new_mine[0][6] < 70:
    recommendations.append("Increase contractor monitoring")

if new_mine[0][7] >= 4:
    recommendations.append("Investigate environmental conditions")

for i, recommendation in enumerate(recommendations, 1):
    print(f"{i}. {recommendation}")
