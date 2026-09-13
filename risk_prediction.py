import joblib

model = joblib.load("risk_model.pkl")

features = [[
    6,    # violations
    4,    # overdue actions
    70,   # inspection score
    12,   # maintenance delay
    3,    # equipment failures
    4,    # contractor violations
    65,   # contractor compliance
    5     # environmental issues
]]

prediction = model.predict(features)[0]
probability = max(model.predict_proba(features)[0]) * 100

print("================================")
print("      MINEGUARD NEXUS AI")
print("================================")
print(f"Risk Level : {prediction}")
print(f"Confidence : {probability:.2f}%")
print("================================")