from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

import mysql.connector

import joblib

import os

from google import genai



app = FastAPI(title="MineGuard Nexus API")



# Gemini AI

gemini_client = genai.Client()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "https://sigma-mineguard-nexus-theta.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Load AI model

model = joblib.load("risk_model.pkl")



FEATURES = [

    "violation_count",

    "overdue_actions",

    "inspection_score",

    "maintenance_delay_days",

    "equipment_failure_count",

    "contractor_violations",

    "contractor_compliance_score",

    "environmental_issues"

]





def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        port=int(os.getenv("MYSQLPORT", "3306")),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE")
    )





@app.get("/")

def home():

    return {

        "message": "MineGuard Nexus API is running"

    }





@app.get("/mines")

def get_mines():



    connection = get_connection()

    cursor = connection.cursor(dictionary=True)



    cursor.execute("SELECT * FROM mines")

    mines = cursor.fetchall()



    cursor.close()

    connection.close()



    return mines





@app.get("/violations")

def get_violations():



    connection = get_connection()

    cursor = connection.cursor(dictionary=True)



    cursor.execute("SELECT * FROM violations")

    violations = cursor.fetchall()



    cursor.close()

    connection.close()



    return violations





@app.get("/inspections")

def get_inspections():



    connection = get_connection()

    cursor = connection.cursor(dictionary=True)



    cursor.execute("SELECT * FROM inspections")

    inspections = cursor.fetchall()



    cursor.close()

    connection.close()



    return inspections





# AI RISK PREDICTION

@app.get("/risk")

def predict_risk():



    connection = get_connection()

    cursor = connection.cursor(dictionary=True)



    # Get every mine

    cursor.execute("SELECT mine_id FROM mines")

    mines = cursor.fetchall()



    results = []



    for mine in mines:



        mine_id = mine["mine_id"]



        # -----------------------------

        # INSPECTIONS

        # -----------------------------

        cursor.execute("""

            SELECT

                COALESCE(SUM(violations_found), 0) AS violations,

                COALESCE(AVG(inspection_score), 100) AS inspection_score

            FROM inspections

            WHERE mine_id = %s

        """, (mine_id,))



        inspection = cursor.fetchone()



        # -----------------------------

        # VIOLATIONS

        # -----------------------------

        cursor.execute("""

            SELECT COUNT(*) AS violation_count

            FROM violations

            WHERE mine_id = %s

        """, (mine_id,))



        violations = cursor.fetchone()



        # -----------------------------

        # CORRECTIVE ACTIONS

        # -----------------------------

        cursor.execute("""

            SELECT COUNT(*) AS overdue_actions

            FROM corrective_actions

            WHERE mine_id = %s

            AND status IN ('Overdue', 'Open')

        """, (mine_id,))



        actions = cursor.fetchone()



        # -----------------------------

        # EQUIPMENT

        # -----------------------------

        cursor.execute("""

            SELECT

                COALESCE(SUM(maintenance_delay_days), 0) AS maintenance_delay,

                COALESCE(SUM(failure_count), 0) AS failures

            FROM equipment

            WHERE mine_id = %s

        """, (mine_id,))



        equipment = cursor.fetchone()



        # -----------------------------

        # CONTRACTORS

        # -----------------------------

        cursor.execute("""

            SELECT

                COALESCE(SUM(previous_violations), 0) AS contractor_violations,

                COALESCE(AVG(compliance_score), 100) AS contractor_compliance

            FROM contractors

            WHERE mine_id = %s

        """, (mine_id,))



        contractors = cursor.fetchone()



        # -----------------------------

        # ENVIRONMENT

        # -----------------------------

        cursor.execute("""

            SELECT

                COALESCE(SUM(

                    CASE

                        WHEN environmental_violation = 'Yes'

                        THEN 1

                        ELSE 0

                    END

                ), 0) AS environmental_issues

            FROM environment

            WHERE mine_id = %s

        """, (mine_id,))



        environment = cursor.fetchone()



        # -----------------------------

        # AI FEATURES

        # -----------------------------



        features = [[

            int(inspection["violations"]),

            int(actions["overdue_actions"]),

            float(inspection["inspection_score"]),

            int(equipment["maintenance_delay"]),

            int(equipment["failures"]),

            int(contractors["contractor_violations"]),

            float(contractors["contractor_compliance"]),

            int(environment["environmental_issues"])

        ]]



        # -----------------------------

        # AI PREDICTION

        # -----------------------------



        prediction = model.predict(features)[0]



        probabilities = model.predict_proba(features)[0]



        confidence = max(probabilities) * 100



        results.append({

            "mine_id": mine_id,

            "risk_level": prediction,

            "confidence": round(confidence, 2),

            "risk_factors": {

                "violations": int(inspection["violations"]),

                "overdue_actions": int(actions["overdue_actions"]),

                "inspection_score": round(

                    float(inspection["inspection_score"]), 2

                ),

                "maintenance_delay_days": int(

                    equipment["maintenance_delay"]

                ),

                "equipment_failures": int(

                    equipment["failures"]

                ),

                "contractor_violations": int(

                    contractors["contractor_violations"]

                ),

                "contractor_compliance": round(

                    float(contractors["contractor_compliance"]), 2

                ),

                "environmental_issues": int(

                    environment["environmental_issues"]

                )

            }

        })



    cursor.close()

    connection.close()



    return results



@app.get("/what-if")
def what_if(mine_id: str = "M001"):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT COALESCE(SUM(violations_found), 0) AS violations,
               COALESCE(AVG(inspection_score), 100) AS inspection_score
        FROM inspections WHERE mine_id = %s
    """, (mine_id,))
    inspection = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*) AS overdue_actions FROM corrective_actions
        WHERE mine_id = %s AND status IN ('Overdue', 'Open')
    """, (mine_id,))
    actions = cursor.fetchone()

    cursor.execute("""
        SELECT COALESCE(SUM(maintenance_delay_days), 0) AS maintenance_delay,
               COALESCE(SUM(failure_count), 0) AS failures
        FROM equipment WHERE mine_id = %s
    """, (mine_id,))
    equipment = cursor.fetchone()

    cursor.execute("""
        SELECT COALESCE(SUM(previous_violations), 0) AS contractor_violations,
               COALESCE(AVG(compliance_score), 100) AS contractor_compliance
        FROM contractors WHERE mine_id = %s
    """, (mine_id,))
    contractors = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*) AS environmental_issues FROM environment
        WHERE mine_id = %s AND environmental_violation = 'Yes'
    """, (mine_id,))
    environment = cursor.fetchone()

    cursor.close()
    connection.close()

    violations = int(inspection["violations"] or 0)
    overdue = int(actions["overdue_actions"] or 0)
    score = float(inspection["inspection_score"] or 100)
    maintenance = int(equipment["maintenance_delay"] or 0)
    failures = int(equipment["failures"] or 0)
    contractor_violations = int(contractors["contractor_violations"] or 0)
    contractor_compliance = float(contractors["contractor_compliance"] or 100)
    environmental = int(environment["environmental_issues"] or 0)

    def ml_result(values):
        prediction = model.predict([values])[0]
        probabilities = model.predict_proba([values])[0]
        return prediction, round(max(probabilities) * 100, 2)

    def scenario_score(values):
        v, o, s, m, f, cv, cc, env = values
        pressure = (
            min(v / 5, 1) * 20 +
            min(o / 5, 1) * 20 +
            max(0, min((100 - s) / 40, 1)) * 15 +
            min(m / 15, 1) * 15 +
            min(f / 5, 1) * 10 +
            min(cv / 5, 1) * 10 +
            max(0, min((80 - cc) / 30, 1)) * 5 +
            min(env / 3, 1) * 5
        )
        return round(max(0, min(100, pressure)), 1)

    def level(score_value):
        if score_value >= 70:
            return "CRITICAL"
        if score_value >= 50:
            return "HIGH"
        if score_value >= 30:
            return "MEDIUM"
        return "LOW"

    current_features = [violations, overdue, score, maintenance, failures,
                        contractor_violations, contractor_compliance, environmental]

    action_features = [max(0, violations - 1), max(0, overdue - 2),
                       min(100, score + 8), max(0, maintenance - 7),
                       max(0, failures - 1), max(0, contractor_violations - 1),
                       min(100, contractor_compliance + 7), max(0, environmental - 1)]

    delay_features = [violations + 1, overdue + 2, max(0, score - 8),
                      maintenance + 7, failures + 1, contractor_violations + 1,
                      max(0, contractor_compliance - 7), environmental + 1]

    current_ml, current_confidence = ml_result(current_features)
    action_ml, action_confidence = ml_result(action_features)
    delay_ml, delay_confidence = ml_result(delay_features)

    current_score = scenario_score(current_features)
    action_score = scenario_score(action_features)
    delay_score = scenario_score(delay_features)

    def result(ml_prediction, confidence, projected_score, baseline):
        return {
            "risk": level(projected_score),
            "ml_risk": ml_prediction,
            "confidence": confidence,
            "risk_score": projected_score,
            "change_from_current": round(projected_score - baseline, 1)
        }

    return {
        "mine_id": mine_id,
        "current": result(current_ml, current_confidence, current_score, current_score),
        "corrective_action": result(action_ml, action_confidence, action_score, current_score),
        "seven_day_delay": result(delay_ml, delay_confidence, delay_score, current_score),
        "recommendation": (
            "Complete high-priority corrective actions and delayed maintenance now. "
            "The simulation shows how intervention can reduce governance risk, "
            "while a seven-day delay can increase risk pressure."
        )
    }


@app.get("/risk-explanation")

def risk_explanation(mine_id: str = "M001"):



    connection = get_connection()

    cursor = connection.cursor(dictionary=True)



    # INSPECTIONS

    cursor.execute("""

        SELECT

            COALESCE(SUM(violations_found), 0) AS violations,

            COALESCE(AVG(inspection_score), 100) AS inspection_score

        FROM inspections

        WHERE mine_id = %s

    """, (mine_id,))

    inspection = cursor.fetchone()



    # CORRECTIVE ACTIONS

    cursor.execute("""

        SELECT COUNT(*) AS overdue_actions

        FROM corrective_actions

        WHERE mine_id = %s

        AND status IN ('Overdue', 'Open')

    """, (mine_id,))

    actions = cursor.fetchone()



    # EQUIPMENT

    cursor.execute("""

        SELECT

            COALESCE(SUM(maintenance_delay_days), 0) AS maintenance_delay,

            COALESCE(SUM(failure_count), 0) AS failures

        FROM equipment

        WHERE mine_id = %s

    """, (mine_id,))

    equipment = cursor.fetchone()



    # CONTRACTORS

    cursor.execute("""

        SELECT

            COALESCE(SUM(previous_violations), 0) AS contractor_violations,

            COALESCE(AVG(compliance_score), 100) AS contractor_compliance

        FROM contractors

        WHERE mine_id = %s

    """, (mine_id,))

    contractors = cursor.fetchone()



    # ENVIRONMENT

    cursor.execute("""

        SELECT COUNT(*) AS environmental_issues

        FROM environment

        WHERE mine_id = %s

        AND environmental_violation = 'Yes'

    """, (mine_id,))

    environment = cursor.fetchone()



    cursor.close()

    connection.close()



    violations = int(inspection["violations"])

    overdue = int(actions["overdue_actions"])

    score = float(inspection["inspection_score"])

    maintenance = int(equipment["maintenance_delay"])

    failures = int(equipment["failures"])

    contractor_violations = int(contractors["contractor_violations"])

    contractor_compliance = float(contractors["contractor_compliance"])

    environmental = int(environment["environmental_issues"])



    # AI prediction

    features = [[

        violations,

        overdue,

        score,

        maintenance,

        failures,

        contractor_violations,

        contractor_compliance,

        environmental

    ]]



    prediction = model.predict(features)[0]

    probabilities = model.predict_proba(features)[0]

    confidence = max(probabilities) * 100



    # Identify important risk drivers

    drivers = []



    if violations >= 3:

        drivers.append(

            f"High number of violations ({violations})"

        )



    if overdue >= 2:

        drivers.append(

            f"Overdue/open corrective actions ({overdue})"

        )



    if score < 70:

        drivers.append(

            f"Low inspection score ({round(score, 2)})"

        )



    if maintenance > 5:

        drivers.append(

            f"Maintenance delay ({maintenance} days)"

        )



    if failures >= 2:

        drivers.append(

            f"Repeated equipment failures ({failures})"

        )



    if contractor_violations >= 2:

        drivers.append(

            f"Contractor violation history ({contractor_violations})"

        )



    if contractor_compliance < 75:

        drivers.append(

            f"Low contractor compliance ({round(contractor_compliance, 2)}%)"

        )



    if environmental >= 1:

        drivers.append(

            f"Environmental issues detected ({environmental})"

        )



    if not drivers:

        drivers.append("No major risk driver detected")



    # Recommendation

    if overdue >= 2:

        recommendation = (

            "Prioritize and close overdue corrective actions."

        )

    elif maintenance > 5:

        recommendation = (

            "Schedule immediate equipment maintenance."

        )

    elif score < 70:

        recommendation = (

            "Conduct a focused safety and compliance inspection."

        )

    elif environmental >= 1:

        recommendation = (

            "Investigate and resolve environmental compliance issues."

        )

    else:

        recommendation = (

            "Continue regular monitoring and preventive inspections."

        )



    return {

        "mine_id": mine_id,

        "risk_level": prediction,

        "confidence": round(confidence, 2),

        "risk_drivers": drivers,

        "recommendation": recommendation

    }

@app.get("/compliance")

def get_compliance():

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)



    cursor.execute("SELECT * FROM violations")

    violations = cursor.fetchall()



    cursor.execute("SELECT * FROM corrective_actions")

    corrective_actions = cursor.fetchall()



    cursor.close()

    conn.close()



    total_violations = len(violations)



    open_violations = sum(

        1 for v in violations

        if str(v.get("status", "")).upper() not in ["RESOLVED", "CLOSED", "COMPLETED"]

    )



    overdue_actions = sum(

        1 for a in corrective_actions

        if str(a.get("status", "")).upper() == "OVERDUE"

    )



    completed_actions = sum(

        1 for a in corrective_actions

        if str(a.get("status", "")).upper() in ["COMPLETED", "CLOSED", "RESOLVED"]

    )



    return {

        "summary": {

            "total_violations": total_violations,

            "open_violations": open_violations,

            "overdue_actions": overdue_actions,

            "completed_actions": completed_actions

        },

        "violations": violations,

        "corrective_actions": corrective_actions

    }



@app.get("/operational")

def get_operational():



    conn = get_connection()

    cursor = conn.cursor(dictionary=True)



    cursor.execute("SELECT * FROM equipment")

    equipment = cursor.fetchall()



    cursor.execute("SELECT * FROM contractors")

    contractors = cursor.fetchall()



    cursor.close()

    conn.close()



    total_equipment = len(equipment)



    maintenance_delays = sum(

        1 for e in equipment

        if int(e.get("maintenance_delay_days") or 0) > 0

    )



    equipment_failures = sum(

        int(e.get("failure_count") or 0)

        for e in equipment

    )



    contractor_violations = sum(

        int(c.get("previous_violations") or 0)

        for c in contractors

    )



    overdue_contractor_actions = sum(

        int(c.get("overdue_actions") or 0)

        for c in contractors

    )



    return {

        "summary": {

            "total_equipment": total_equipment,

            "maintenance_delays": maintenance_delays,

            "equipment_failures": equipment_failures,

            "contractor_violations": contractor_violations,

            "overdue_contractor_actions": overdue_contractor_actions

        },

        "equipment": equipment,

        "contractors": contractors

    }



@app.get("/sustainability")

def get_sustainability():

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)



    cursor.execute("SELECT * FROM environment")

    environment = cursor.fetchall()



    cursor.close()

    conn.close()



    total_records = len(environment)



    environmental_violations = sum(

        1

        for e in environment

        if str(e.get("environmental_violation", "")).strip().lower()

        in ["yes", "true", "1"]

    )



    dust_values = [

        float(e["dust_level"])

        for e in environment

        if e.get("dust_level") is not None

    ]



    ph_values = [

        float(e["water_ph"])

        for e in environment

        if e.get("water_ph") is not None

    ]



    noise_values = [

        float(e["noise_level"])

        for e in environment

        if e.get("noise_level") is not None

    ]



    return {

        "summary": {

            "total_records": total_records,

            "environmental_violations": environmental_violations,

            "average_dust": round(

                sum(dust_values) / len(dust_values), 2

            ) if dust_values else 0,

            "average_water_ph": round(

                sum(ph_values) / len(ph_values), 2

            ) if ph_values else 0,

            "average_noise": round(

                sum(noise_values) / len(noise_values), 2

            ) if noise_values else 0

        },

        "environment": environment

    }



@app.get("/environmental-risk")

def environmental_risk():



    conn = get_connection()

    cursor = conn.cursor(dictionary=True)



    cursor.execute("SELECT * FROM environment")

    records = cursor.fetchall()



    cursor.close()

    conn.close()



    results = []



    for r in records:



        dust = float(r.get("dust_level") or 0)

        air = float(r.get("air_quality") or 0)

        ph = float(r.get("water_ph") or 7)

        noise = float(r.get("noise_level") or 0)



        risk_points = 0

        drivers = []



        if dust >= 80:

            risk_points += 2

            drivers.append("High dust level")

        elif dust >= 60:

            risk_points += 1

            drivers.append("Elevated dust level")



        if air < 60:

            risk_points += 2

            drivers.append("Poor air quality")

        elif air < 75:

            risk_points += 1

            drivers.append("Reduced air quality")



        if ph < 6.5 or ph > 8.5:

            risk_points += 2

            drivers.append("Abnormal water pH")



        if noise >= 85:

            risk_points += 2

            drivers.append("High noise level")

        elif noise >= 75:

            risk_points += 1

            drivers.append("Elevated noise level")



        if str(r.get("environmental_violation", "")).lower() == "yes":

            risk_points += 2

            drivers.append("Environmental violation detected")



        if risk_points >= 5:

            risk_level = "CRITICAL"

            recommendation = "Immediate environmental inspection and corrective action required."



        elif risk_points >= 3:

            risk_level = "HIGH"

            recommendation = "Schedule environmental inspection and mitigation measures."



        elif risk_points >= 1:

            risk_level = "MEDIUM"

            recommendation = "Monitor environmental conditions and review mitigation controls."



        else:

            risk_level = "LOW"

            recommendation = "Environmental conditions are currently stable."



        results.append({

            "mine_id": r.get("mine_id"),

            "risk_level": risk_level,

            "risk_score": risk_points,

            "risk_drivers": drivers,

            "recommendation": recommendation

        })



    return {

        "environmental_risk": results

    }



# ============================================================
# SIGMA AI GOVERNANCE ASSISTANT
# ============================================================

@app.get("/ai-assistant")
def ai_assistant(question: str, mine_id: str = "M001"):

    question = question.strip()

    if not question:
        return {
            "mine_id": mine_id,
            "answer": "Please enter a question and I'll help you."
        }

    # ========================================================
    # 1. GET DATA FROM MYSQL
    # ========================================================

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM mines WHERE mine_id = %s",
        (mine_id,)
    )
    mine = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM violations WHERE mine_id = %s",
        (mine_id,)
    )
    violations = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM corrective_actions WHERE mine_id = %s",
        (mine_id,)
    )
    corrective_actions = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM equipment WHERE mine_id = %s",
        (mine_id,)
    )
    equipment = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM contractors WHERE mine_id = %s",
        (mine_id,)
    )
    contractors = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM environment WHERE mine_id = %s",
        (mine_id,)
    )
    environment = cursor.fetchall()

    cursor.execute(
        """
        SELECT violations_found, inspection_score
        FROM inspections
        WHERE mine_id = %s
        """,
        (mine_id,)
    )
    inspections = cursor.fetchall()

    cursor.close()
    conn.close()

    # ========================================================
    # 2. CALCULATE MINE METRICS
    # ========================================================

    violation_count = len(violations)

    inspection_violations = sum(
        int(i.get("violations_found") or 0)
        for i in inspections
    )

    inspection_scores = [
        float(i["inspection_score"])
        for i in inspections
        if i.get("inspection_score") is not None
    ]

    inspection_score = (
        sum(inspection_scores) / len(inspection_scores)
        if inspection_scores
        else 100
    )

    overdue_actions = sum(
        1
        for a in corrective_actions
        if str(a.get("status", "")).strip().upper()
        in ["OPEN", "OVERDUE"]
    )

    maintenance_delay = sum(
        int(e.get("maintenance_delay_days") or 0)
        for e in equipment
    )

    equipment_failures = sum(
        int(e.get("failure_count") or 0)
        for e in equipment
    )

    contractor_violations = sum(
        int(c.get("previous_violations") or 0)
        for c in contractors
    )

    contractor_scores = [
        float(c["compliance_score"])
        for c in contractors
        if c.get("compliance_score") is not None
    ]

    contractor_compliance = (
        sum(contractor_scores) / len(contractor_scores)
        if contractor_scores
        else 100
    )

    environmental_issues = sum(
        1
        for e in environment
        if str(e.get("environmental_violation", "")).strip().lower()
        in ["yes", "true", "1"]
    )

    # ========================================================
    # 3. ML RISK PREDICTION
    # ========================================================

    features = [[
        inspection_violations,
        overdue_actions,
        inspection_score,
        maintenance_delay,
        equipment_failures,
        contractor_violations,
        contractor_compliance,
        environmental_issues
    ]]

    prediction = model.predict(features)[0]

    probabilities = model.predict_proba(features)[0]

    confidence = max(probabilities) * 100

    # ========================================================
    # 4. LOCAL SIGMA INTELLIGENCE
    # ========================================================

    q = question.lower()

    # --------------------------------------------------------
    # GREETINGS
    # --------------------------------------------------------

    greetings = [
    "hi",
    "hii",
    "hiii",
    "hiiii",
    "hello",
    "hey",
    "heyy",
    "hai",
    "good morning",
    "good afternoon",
    "good evening",
    "how are you"
]

    if q in greetings or any(
        q.startswith(g + " ")
        for g in greetings
    ):
        return {
            "mine_id": mine_id,
            "question": question,
            "answer": (
                "Hi! 👋 I'm SIGMA, your AI mining governance "
                "assistant. How can I help you today?"
            ),
            "source": "SIGMA"
        }

    # --------------------------------------------------------
    # THANK YOU
    # --------------------------------------------------------

    if "thank you" in q or q in ["thanks", "thank u", "thx"]:
        return {
            "mine_id": mine_id,
            "question": question,
            "answer": (
                "You're welcome! 😊 I'm here whenever you need "
                "help with mining governance, compliance or risk."
            ),
            "source": "SIGMA"
        }

    # ========================================================
    # 5. NATURAL LOCAL CONVERSATION
    # ========================================================

    if q in ["ok", "okay", "alright", "fine", "cool", "great"]:
        return {
            "mine_id": mine_id,
            "question": question,
            "answer": (
                "You're welcome! 👍 I'm here whenever you need me. "
                "You can ask about mine risk, compliance, equipment, "
                "contractors, inspections or environmental conditions."
            ),
            "source": "SIGMA"
        }

    if "what can you do" in q or "how can you help" in q:
        return {
            "mine_id": mine_id,
            "question": question,
            "answer": (
                "I can help you analyze the selected mine's governance data. "
                "I can explain risk, identify violations, review corrective "
                "actions, check equipment and contractor status, analyze "
                "environmental conditions, and suggest practical next steps."
            ),
            "source": "SIGMA"
        }

    if q in ["who are you", "what are you", "tell me about yourself"]:
        return {
            "mine_id": mine_id,
            "question": question,
            "answer": (
                "I'm SIGMA — the Smart Integrated Governance assistant "
                "for mining operations. I combine mine data, predictive "
                "risk analysis and governance insights to support better "
                "decisions."
            ),
            "source": "SIGMA"
        }

    # ========================================================
    # 6. MINE-SPECIFIC LOCAL ANSWERS
    # ========================================================

    # --------------------------------------------------------
    # RISK QUESTIONS
    # --------------------------------------------------------

    if (
        "why" in q and "risk" in q
    ) or "risk factors" in q or "risk drivers" in q:

        drivers = []

        if inspection_violations >= 3:
            drivers.append(
                f"{inspection_violations} inspection violations"
            )

        if overdue_actions >= 2:
            drivers.append(
                f"{overdue_actions} open/overdue corrective actions"
            )

        if inspection_score < 70:
            drivers.append(
                f"low inspection score ({inspection_score:.1f})"
            )

        if maintenance_delay > 5:
            drivers.append(
                f"{maintenance_delay} days of maintenance delay"
            )

        if equipment_failures >= 2:
            drivers.append(
                f"{equipment_failures} equipment failures"
            )

        if contractor_violations >= 2:
            drivers.append(
                f"{contractor_violations} contractor violations"
            )

        if contractor_compliance < 75:
            drivers.append(
                f"low contractor compliance ({contractor_compliance:.1f}%)"
            )

        if environmental_issues >= 1:
            drivers.append(
                f"{environmental_issues} environmental issue(s)"
            )

        if drivers:
            driver_text = "\n".join(
                f"• {d}" for d in drivers
            )
        else:
            driver_text = "• No major contributing factor detected."

        answer = (
            f"{mine_id} is currently classified as "
            f"{prediction} risk with {confidence:.1f}% model confidence.\n\n"
            f"Main risk drivers:\n"
            f"{driver_text}\n\n"
            f"Recommendation: prioritize the highest-severity "
            f"open corrective actions and address equipment or "
            f"compliance issues contributing to the risk."
        )

        return {
            "mine_id": mine_id,
            "question": question,
            "answer": answer,
            "source": "SIGMA ML + MySQL",
            "risk_level": prediction,
            "risk_confidence": round(confidence, 2)
        }
    # --------------------------------------------------------
    # MANAGEMENT / RECOMMENDATION QUESTIONS
    # --------------------------------------------------------

    if (
        "management" in q
        or "what should we do" in q
        or "what should management do" in q
        or "what should i do" in q
        or "recommendation" in q
        or "recommendations" in q
        or "next step" in q
        or "next steps" in q
    ):

        recommendations = []

        if overdue_actions > 0:
            recommendations.append(
                f"Close {overdue_actions} open/overdue corrective action(s)."
            )

        if maintenance_delay > 0:
            recommendations.append(
                f"Address {maintenance_delay} day(s) of equipment maintenance delay."
            )

        if equipment_failures > 0:
            recommendations.append(
                f"Inspect equipment associated with the {equipment_failures} recorded failure(s)."
            )

        if contractor_violations > 0:
            recommendations.append(
                f"Review contractor performance and {contractor_violations} recorded violation(s)."
            )

        if environmental_issues > 0:
            recommendations.append(
                f"Investigate {environmental_issues} environmental issue(s)."
            )

        if not recommendations:
            recommendations.append(
                "Continue routine inspections and preventive monitoring."
            )

        answer = (
            f"Management priorities for {mine_id} "
            f"(current risk: {prediction}):\n\n"
            + "\n".join(
                f"{i + 1}. {item}"
                for i, item in enumerate(recommendations)
            )
        )

        return {
            "mine_id": mine_id,
            "question": question,
            "answer": answer,
            "source": "SIGMA ML + MySQL",
            "risk_level": prediction,
            "risk_confidence": round(confidence, 2)
        }


    # --------------------------------------------------------
    # CURRENT RISK
    # --------------------------------------------------------

    if (
        "risk level" in q
        or "current risk" in q
        or "risk of" in q
        or q == "risk"
    ):

        return {
            "mine_id": mine_id,
            "question": question,
            "answer": (
                f"{mine_id} is currently classified as "
                f"{prediction} risk with a model confidence of "
                f"{confidence:.1f}%."
            ),
            "source": "SIGMA ML",
            "risk_level": prediction,
            "risk_confidence": round(confidence, 2)
        }

    # --------------------------------------------------------
    # VIOLATIONS
    # --------------------------------------------------------

    if "violation" in q:

        if violation_count == 0:
            answer = f"{mine_id} currently has no recorded violations."
        else:
            answer = (
                f"{mine_id} has {violation_count} recorded violation(s)."
            )

            if violations:
                categories = []

                for v in violations:
                    category = v.get("category")
                    severity = v.get("severity")

                    if category:
                        if severity:
                            categories.append(
                                f"{category} ({severity})"
                            )
                        else:
                            categories.append(str(category))

                if categories:
                    answer += (
                        "\n\nRecorded violation categories:\n"
                        + "\n".join(
                            f"• {c}" for c in categories
                        )
                    )

        return {
            "mine_id": mine_id,
            "question": question,
            "answer": answer,
            "source": "MySQL"
        }

    # --------------------------------------------------------
    # CORRECTIVE ACTIONS
    # --------------------------------------------------------

    if (
        "corrective action" in q
        or "corrective actions" in q
        or "actions" in q
        or "overdue" in q
    ):

        total_actions = len(corrective_actions)

        completed_actions = sum(
            1
            for a in corrective_actions
            if str(a.get("status", "")).upper()
            in ["COMPLETED", "CLOSED", "RESOLVED"]
        )

        answer = (
            f"{mine_id} has {total_actions} corrective action(s) "
            f"in the current system data.\n\n"
            f"• Open/overdue: {overdue_actions}\n"
            f"• Completed: {completed_actions}"
        )

        return {
            "mine_id": mine_id,
            "question": question,
            "answer": answer,
            "source": "MySQL"
        }

    # --------------------------------------------------------
    # EQUIPMENT
    # --------------------------------------------------------

    if (
        "equipment" in q
        or "maintenance" in q
        or "failure" in q
        or "machine" in q
    ):

        answer = (
            f"{mine_id} currently has {len(equipment)} equipment "
            f"record(s).\n\n"
            f"• Maintenance delay: {maintenance_delay} day(s)\n"
            f"• Equipment failures: {equipment_failures}"
        )

        if equipment:
            answer += "\n\nEquipment status:"

            for e in equipment:
                equipment_type = e.get(
                    "equipment_type",
                    "Equipment"
                )

                condition = e.get(
                    "condition",
                    "Unknown"
                )

                delay = e.get(
                    "maintenance_delay_days",
                    0
                )

                answer += (
                    f"\n• {equipment_type}: "
                    f"{condition}, maintenance delay "
                    f"{delay} day(s)"
                )

        return {
            "mine_id": mine_id,
            "question": question,
            "answer": answer,
            "source": "MySQL"
        }

    # --------------------------------------------------------
    # CONTRACTORS
    # --------------------------------------------------------

    if "contractor" in q:

        answer = (
            f"{mine_id} has {len(contractors)} contractor "
            f"record(s).\n\n"
            f"• Previous contractor violations: "
            f"{contractor_violations}\n"
            f"• Average contractor compliance: "
            f"{contractor_compliance:.1f}%"
        )

        return {
            "mine_id": mine_id,
            "question": question,
            "answer": answer,
            "source": "MySQL"
        }

    # --------------------------------------------------------
    # ENVIRONMENT
    # --------------------------------------------------------

    if (
        "environment" in q
        or "environmental" in q
        or "dust" in q
        or "air quality" in q
        or "water" in q
        or "noise" in q
    ):

        dust_values = [
            float(e["dust_level"])
            for e in environment
            if e.get("dust_level") is not None
        ]

        air_values = [
            float(e["air_quality"])
            for e in environment
            if e.get("air_quality") is not None
        ]

        ph_values = [
            float(e["water_ph"])
            for e in environment
            if e.get("water_ph") is not None
        ]

        noise_values = [
            float(e["noise_level"])
            for e in environment
            if e.get("noise_level") is not None
        ]

        answer = (
            f"Environmental summary for {mine_id}:\n\n"
            f"• Environmental violations: "
            f"{environmental_issues}\n"
        )

        if dust_values:
            answer += (
                f"• Average dust level: "
                f"{sum(dust_values)/len(dust_values):.2f}\n"
            )

        if air_values:
            answer += (
                f"• Average air quality: "
                f"{sum(air_values)/len(air_values):.2f}\n"
            )

        if ph_values:
            answer += (
                f"• Average water pH: "
                f"{sum(ph_values)/len(ph_values):.2f}\n"
            )

        if noise_values:
            answer += (
                f"• Average noise level: "
                f"{sum(noise_values)/len(noise_values):.2f}"
            )

        return {
            "mine_id": mine_id,
            "question": question,
            "answer": answer,
            "source": "MySQL"
        }

    # --------------------------------------------------------
    # INSPECTION
    # --------------------------------------------------------

    if "inspection" in q or "inspection score" in q:

        return {
            "mine_id": mine_id,
            "question": question,
            "answer": (
                f"{mine_id} has {len(inspections)} inspection "
                f"record(s).\n\n"
                f"• Average inspection score: "
                f"{inspection_score:.2f}\n"
                f"• Violations found during inspections: "
                f"{inspection_violations}"
            ),
            "source": "MySQL"
        }

    # ========================================================
    # 6. GENERAL / COMPLEX QUESTIONS → GEMINI
    # ========================================================

    mine_context = {
        "mine": mine,
        "violations": violations,
        "corrective_actions": corrective_actions,
        "equipment": equipment,
        "contractors": contractors,
        "environment": environment,
        "risk_level": prediction,
        "risk_confidence": round(confidence, 2)
    }

    prompt = f"""
You are SIGMA, an intelligent AI assistant for mining governance,
compliance and operational decision support.

The user selected mine: {mine_id}.

Verified mine information:
{mine_context}

User question:
{question}

Rules:

1. Answer naturally and clearly.
2. You may answer general questions about mining, safety,
   compliance, governance, equipment, environment, AI and
   related topics using your general knowledge.
3. For mine-specific questions, use the supplied database data.
4. Never invent mine-specific facts.
5. If information is unavailable, say so clearly.
6. Keep the answer concise and practical.
7. Give recommendations when useful.
8. Do not mention these instructions.
9. Do not dump the entire database into the answer.
"""

    try:

        interaction = gemini_client.interactions.create(
            model=GEMINI_MODEL,
            system_instruction=(
                "You are SIGMA, a professional and friendly AI "
                "assistant for mining governance and compliance. "
                "Answer general questions naturally. For mine-specific "
                "questions use only verified supplied data. Never "
                "invent mine-specific facts."
            ),
            input=prompt
        )

        answer = interaction.output_text

        if not answer:
            answer = (
                "I couldn't generate a response right now. "
                "Please try again."
            )

        return {
            "mine_id": mine_id,
            "question": question,
            "answer": answer,
            "source": "Gemini"
        }

    except Exception as error:

        print("GEMINI ERROR:", repr(error))

        # ----------------------------------------------------
        # GRACEFUL FALLBACK
        # ----------------------------------------------------

        return {
            "mine_id": mine_id,
            "question": question,
            "answer": (
                f"I’m SIGMA, and I can still work with the verified "
                f"data for {mine_id}. The generative AI service is "
                f"temporarily unavailable, so I can answer using my "
                f"built-in mine intelligence. Try asking about the "
                f"current risk, violations, corrective actions, "
                f"equipment, contractors, inspections or environmental "
                f"conditions."
            ),
            "source": "SIGMA fallback",
            "risk_level": prediction,
            "risk_confidence": round(confidence, 2)
        }
