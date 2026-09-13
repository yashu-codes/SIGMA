import csv
import random
from pathlib import Path

random.seed(42)

# Save training dataset inside the Sigma project folder
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "training_data.csv"

rows = []

for i in range(1, 1501):

    # Generate realistic-looking historical features
    violation_count = random.randint(0, 12)
    overdue_actions = random.randint(0, 10)
    inspection_score = random.randint(45, 100)
    maintenance_delay = random.randint(0, 30)
    equipment_failures = random.randint(0, 8)
    contractor_violations = random.randint(0, 8)
    contractor_compliance = random.randint(45, 100)
    environmental_issues = random.randint(0, 8)

    # Calculate a synthetic risk score
    risk_score = (
        violation_count * 3
        + overdue_actions * 4
        + (100 - inspection_score) * 0.35
        + maintenance_delay * 1.2
        + equipment_failures * 3
        + contractor_violations * 2.5
        + (100 - contractor_compliance) * 0.25
        + environmental_issues * 3
    )

    # Keep score between 0 and 100
    risk_score = max(0, min(100, risk_score))

    # Convert score into risk category
    if risk_score < 30:
        risk_level = "LOW"
    elif risk_score < 55:
        risk_level = "MEDIUM"
    elif risk_score < 75:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    rows.append([
        f"HIST_{i:04d}",
        f"M{random.randint(1, 10):03d}",
        violation_count,
        overdue_actions,
        inspection_score,
        maintenance_delay,
        equipment_failures,
        contractor_violations,
        contractor_compliance,
        environmental_issues,
        round(risk_score, 2),
        risk_level
    ])


headers = [
    "record_id",
    "mine_id",
    "violation_count",
    "overdue_actions",
    "inspection_score",
    "maintenance_delay_days",
    "equipment_failure_count",
    "contractor_violations",
    "contractor_compliance_score",
    "environmental_issues",
    "risk_score",
    "risk_level"
]


with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(rows)

print("Training dataset created successfully!")
print(f"Location: {OUTPUT_FILE}")
print(f"Total records: {len(rows)}")