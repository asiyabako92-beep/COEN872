import sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "referral_dss_demo.db"

st.set_page_config(
    page_title="Nigeria PHC Referral DSS",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- Styling --------------------------------------
st.markdown("""
<style>
    .stApp { background: #f5f8fb; }
    [data-testid="stSidebar"] { background: #073f35; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .brand { font-size: 1.45rem; font-weight: 800; line-height: 1.2; color: white; }
    .tagline { color: #d7eee7; font-style: italic; text-align: center; }
    .page-intro { color: #506174; margin-top: -0.4rem; }
    .notice { padding: 0.85rem 1rem; border-radius: 0.7rem; background: #fff4d6;
              border: 1px solid #edc65b; color: #664b00; margin-bottom: 1rem; }
    .section-head { background: #e3f2ec; padding: .65rem .85rem; border-radius: .55rem;
                    color: #07543f; font-weight: 750; margin: .7rem 0 .4rem 0; }
    div[data-testid="stMetric"] { background: white; border: 1px solid #e0e8ef;
        border-radius: .7rem; padding: .8rem; }
    .small-muted { color: #6b7785; font-size: .86rem; }
</style>
""", unsafe_allow_html=True)

# ----------------------------- Database -------------------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def initialise_db():
    with get_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            age INTEGER NOT NULL,
            sex TEXT NOT NULL,
            pregnancy TEXT,
            location TEXT,
            temperature_c REAL,
            heart_rate INTEGER,
            respiratory_rate INTEGER,
            systolic_bp INTEGER,
            diastolic_bp INTEGER,
            spo2 REAL,
            symptoms TEXT,
            complaint TEXT,
            symptom_duration TEXT,
            pain_severity INTEGER,
            medical_history TEXT,
            medications TEXT,
            allergies TEXT,
            provisional_diagnosis TEXT,
            clinical_notes TEXT,
            review_status TEXT DEFAULT 'Not reviewed',
            reviewer_decision TEXT,
            reviewer_comment TEXT,
            reviewed_at TEXT
        )
        """)
        conn.commit()

def fetch_assessments():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM assessments ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]

def save_assessment(data):
    with get_connection() as conn:
        cur = conn.execute("""
        INSERT INTO assessments (
            case_id, created_at, age, sex, pregnancy, location, temperature_c,
            heart_rate, respiratory_rate, systolic_bp, diastolic_bp, spo2,
            symptoms, complaint, symptom_duration, pain_severity, medical_history,
            medications, allergies, provisional_diagnosis, clinical_notes
        ) VALUES (
            :case_id, :created_at, :age, :sex, :pregnancy, :location, :temperature_c,
            :heart_rate, :respiratory_rate, :systolic_bp, :diastolic_bp, :spo2,
            :symptoms, :complaint, :symptom_duration, :pain_severity, :medical_history,
            :medications, :allergies, :provisional_diagnosis, :clinical_notes
        )
        """, data)
        conn.commit()
        return cur.lastrowid

def save_review(case_id, decision, comment):
    with get_connection() as conn:
        conn.execute("""
            UPDATE assessments
            SET review_status='Reviewed', reviewer_decision=?, reviewer_comment=?, reviewed_at=?
            WHERE case_id=?
        """, (decision, comment, datetime.now().isoformat(timespec="minutes"), case_id))
        conn.commit()

initialise_db()

# ----------------------------- Helpers --------------------------------------
def get_cases():
    return fetch_assessments()

def section(title):
    st.markdown(f'<div class="section-head">{title}</div>', unsafe_allow_html=True)

def case_frame(cases):
    if not cases:
        return pd.DataFrame()
    df = pd.DataFrame(cases)
    return df

def prototype_notice():
    st.markdown(
        '<div class="notice"><b>Prototype mode:</b> No trained or validated AI model is connected. '
        'The system does not generate clinical referral predictions. Do not use it to make '
        'real patient-care decisions.</div>',
        unsafe_allow_html=True
    )

# ----------------------------- Sidebar --------------------------------------
with st.sidebar:
    st.markdown('<div style="text-align:center;font-size:3rem;">🏥</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand" style="text-align:center;">Nigeria PHC<br>Referral DSS</div>', unsafe_allow_html=True)
    st.caption("COEN872 | AI Systems Development")
    st.divider()
    page = st.radio(
        "Navigation",
        ["Dashboard", "Patient Assessment", "AI Recommendation",
         "Uncertainty & Expert Review", "Analytics", "About the Project"],
        label_visibility="collapsed"
    )
    st.divider()
    st.markdown('<div class="tagline">Better Decisions.<br>Better Care.</div>', unsafe_allow_html=True)
    st.caption("Research prototype — not for clinical use")

cases = get_cases()
df = case_frame(cases)

# ----------------------------- Dashboard ------------------------------------
if page == "Dashboard":
    st.title("Uncertainty-Aware AI-Based Health Referral Decision Support System")
    st.markdown('<p class="page-intro">For Primary Healthcare Centres in Nigeria</p>', unsafe_allow_html=True)
    prototype_notice()

    total = len(cases)
    reviewed = sum(1 for x in cases if x["review_status"] == "Reviewed")
    pending = total - reviewed
    a, b, c, d = st.columns(4)
    a.metric("Assessment records", total)
    b.metric("Reviewed records", reviewed)
    c.metric("Awaiting review", pending)
    d.metric("AI model status", "Not connected")

    st.subheader("System workflow")
    steps = st.columns(4)
    for col, number, label in zip(
        steps, ["01", "02", "03", "04"],
        ["Patient assessment", "Model prediction", "Uncertainty estimation", "Expert escalation"]
    ):
        with col:
            st.markdown(f"### {number}")
            st.write(label)

    st.subheader("Recent assessment records")
    if cases:
        view = df[["case_id", "created_at", "age", "sex", "location", "review_status"]].head(8)
        st.dataframe(view, use_container_width=True, hide_index=True)
    else:
        st.info("No assessments have been recorded yet. Open Patient Assessment to add a fictional or authorised de-identified demonstration case.")

# ----------------------------- Patient Assessment ---------------------------
elif page == "Patient Assessment":
    st.title("Patient Assessment")
    st.write("Record the clinical information required for the research prototype.")
    st.caption("Use fictional or properly authorised, de-identified information only. Do not enter patient names, phone numbers, addresses or other direct identifiers.")
    prototype_notice()

    with st.form("assessment_form", clear_on_submit=True):
        section("Demographics")
        c1, c2, c3 = st.columns(3)
        age = c1.number_input("Age (years)", min_value=0, max_value=120, value=30)
        sex = c2.selectbox("Sex", ["Not specified", "Female", "Male"])
        location = c3.selectbox("State / location", [
            "Not specified", "Abuja FCT", "Kaduna", "Kano", "Lagos", "Niger",
            "Plateau", "Sokoto", "Other"
        ])
        pregnancy = st.selectbox("Pregnancy status", ["Not applicable / unknown", "Yes", "No"])

        section("Vital Signs")
        v1, v2, v3 = st.columns(3)
        temperature = v1.number_input("Temperature (°C)", 25.0, 45.0, 37.0, 0.1)
        heart_rate = v2.number_input("Heart rate (beats/min)", 0, 250, 80)
        respiratory_rate = v3.number_input("Respiratory rate (breaths/min)", 0, 100, 18)
        v4, v5, v6 = st.columns(3)
        systolic_bp = v4.number_input("Systolic BP (mmHg)", 0, 300, 120)
        diastolic_bp = v5.number_input("Diastolic BP (mmHg)", 0, 200, 80)
        spo2 = v6.number_input("Oxygen saturation (%)", 0.0, 100.0, 98.0, 0.5)

        section("Presenting Symptoms")
        symptoms = st.multiselect("Select symptoms", [
            "Fever", "Cough", "Shortness of breath", "Chest pain",
            "Abdominal pain", "Headache", "Vomiting", "Diarrhoea",
            "Fatigue", "Dizziness", "Bleeding", "Other"
        ])
        complaint = st.text_area("Chief complaint / presenting concern")
        symptom_duration = st.selectbox("Duration of symptoms", [
            "Not recorded", "Less than 24 hours", "1–3 days",
            "4–7 days", "More than 7 days"
        ])
        pain_severity = st.slider("Pain severity (if applicable)", 0, 10, 0)

        section("Medical History")
        m1, m2, m3 = st.columns(3)
        medical_history = m1.text_input("Relevant past medical history")
        medications = m2.text_input("Current medications")
        allergies = m3.text_input("Known allergies")

        provisional_diagnosis = st.text_input("Provisional diagnosis / clinical impression (if available)")
        clinical_notes = st.text_area("Additional clinical notes (avoid identifiers)")

        submitted = st.form_submit_button("Save Assessment", type="primary", use_container_width=True)

    if submitted:
        case_id = f"PHC-{datetime.now().strftime('%y%m%d')}-{datetime.now().strftime('%H%M%S%f')[-6:]}"
        record = {
            "case_id": case_id,
            "created_at": datetime.now().isoformat(timespec="minutes"),
            "age": int(age), "sex": sex, "pregnancy": pregnancy, "location": location,
            "temperature_c": float(temperature), "heart_rate": int(heart_rate),
            "respiratory_rate": int(respiratory_rate), "systolic_bp": int(systolic_bp),
            "diastolic_bp": int(diastolic_bp), "spo2": float(spo2),
            "symptoms": ", ".join(symptoms), "complaint": complaint,
            "symptom_duration": symptom_duration, "pain_severity": int(pain_severity),
            "medical_history": medical_history, "medications": medications,
            "allergies": allergies, "provisional_diagnosis": provisional_diagnosis,
            "clinical_notes": clinical_notes
        }
        save_assessment(record)
        st.success(f"Assessment saved successfully. Case ID: {case_id}")
        st.info("The record is stored locally. No AI prediction has been produced because the model is not connected.")

# ----------------------------- AI Recommendation ----------------------------
elif page == "AI Recommendation":
    st.title("AI Referral Recommendation")
    prototype_notice()
    st.subheader("Prediction status")
    c1, c2, c3 = st.columns(3)
    c1.metric("Referral prediction", "Unavailable")
    c2.metric("Calibrated confidence", "Unavailable")
    c3.metric("Conformal prediction set", "Unavailable")
    st.info(
        "This page will display the output of the selected trained model, calibrated "
        "class probabilities, uncertainty estimate and conformal prediction set after "
        "the data and model development stages are completed."
    )
    st.markdown("**Planned model candidates:** Logistic Regression, Random Forest and XGBoost.")
    st.markdown("**Planned uncertainty methods:** probability calibration and conformal prediction.")
    st.markdown("**Safety principle:** cases outside the pre-defined confidence or uncertainty criteria will be referred for qualified human review, subject to the final validated protocol.")

# ----------------------------- Expert Review --------------------------------
elif page == "Uncertainty & Expert Review":
    st.title("Uncertainty & Expert Review")
    st.write("Review workflow for cases that the future validated model flags for human assessment.")
    prototype_notice()
    reviewed = [x for x in cases if x["review_status"] == "Reviewed"]
    pending_cases = [x for x in cases if x["review_status"] != "Reviewed"]
    m1, m2, m3 = st.columns(3)
    m1.metric("Recorded assessments", len(cases))
    m2.metric("Pending manual review", len(pending_cases))
    m3.metric("Reviews recorded", len(reviewed))
    st.warning("Automatic uncertainty-based case flagging is not active until a trained model and uncertainty method are integrated.")

    if cases:
        st.subheader("Assessment records")
        table = pd.DataFrame([{
            "Case ID": x["case_id"], "Date": x["created_at"], "Age": x["age"],
            "Sex": x["sex"], "Location": x["location"], "Review status": x["review_status"]
        } for x in cases])
        st.dataframe(table, use_container_width=True, hide_index=True)

        st.subheader("Demonstration review record")
        selected_id = st.selectbox("Select a case record", [x["case_id"] for x in cases])
        selected = next(x for x in cases if x["case_id"] == selected_id)
        with st.expander("View recorded clinical information", expanded=True):
            l, r = st.columns(2)
            with l:
                st.write(f"**Age:** {selected['age']} | **Sex:** {selected['sex']}")
                st.write(f"**Location:** {selected['location']}")
                st.write(f"**Temperature:** {selected['temperature_c']} °C")
                st.write(f"**Heart rate:** {selected['heart_rate']} bpm")
                st.write(f"**Respiratory rate:** {selected['respiratory_rate']} /min")
            with r:
                st.write(f"**Blood pressure:** {selected['systolic_bp']}/{selected['diastolic_bp']} mmHg")
                st.write(f"**SpO₂:** {selected['spo2']}%")
                st.write(f"**Symptoms:** {selected['symptoms'] or 'Not recorded'}")
                st.write(f"**Chief complaint:** {selected['complaint'] or 'Not recorded'}")
                st.write(f"**Medical history:** {selected['medical_history'] or 'Not recorded'}")

        with st.form("expert_review_form"):
            decision = st.radio("Demonstration reviewer outcome", [
                "Reviewed — no additional comment",
                "Reviewed — further clinical assessment advised",
                "Reviewed — refer for qualified clinical assessment",
                "Unable to determine from information supplied"
            ])
            comment = st.text_area("Reviewer comments (optional)")
            review_submit = st.form_submit_button("Save Review Record", type="primary")
        if review_submit:
            save_review(selected_id, decision, comment)
            st.success("Review record saved locally.")
            st.rerun()
        if selected["review_status"] == "Reviewed":
            st.caption(f"Previous review: {selected['reviewer_decision']} | {selected['reviewed_at']}")
            if selected["reviewer_comment"]:
                st.write(f"**Comment:** {selected['reviewer_comment']}")
    else:
        st.info("No assessment records are available. Save a demonstration assessment first.")

# ----------------------------- Analytics ------------------------------------
elif page == "Analytics":
    st.title("Analytics & Model Evaluation")
    prototype_notice()
    st.subheader("Prototype data overview")
    a, b, c = st.columns(3)
    a.metric("Assessment records", len(cases))
    b.metric("Reviewed records", sum(1 for x in cases if x["review_status"] == "Reviewed"))
    c.metric("Model evaluation", "Not started")

    st.subheader("Planned evaluation framework")
    st.markdown("""
    | Evaluation area | Measures |
    |---|---|
    | Classification performance | Accuracy, precision, sensitivity/recall, specificity, F1-score |
    | Ranking performance | ROC-AUC and PR-AUC |
    | Probability calibration | Brier score and calibration curve |
    | Uncertainty / conformal prediction | Empirical coverage and average prediction-set size |
    | Human escalation | Selective risk and proportion of cases escalated |
    """)
    st.caption("No model-performance values are shown because no model has been trained or evaluated.")
    if cases:
        export_df = pd.DataFrame(cases)
        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download demonstration assessment records (CSV)", csv,
                           "referral_dss_demo_assessments.csv", "text/csv")

# ----------------------------- About ----------------------------------------
elif page == "About the Project":
    st.title("About the Project")
    st.markdown("""
    **Approved project title**

    An Uncertainty-Aware AI-Based Health Referral Decision Support System for
    Primary Healthcare Centres in Nigeria.

    **Aim**

    To develop an uncertainty-aware AI-based decision support system to assist
    frontline healthcare workers in safe and reliable patient referral decisions
    in Nigerian primary healthcare centres.

    **Planned objectives**
    1. Develop a machine-learning model to predict patient referral decisions from clinical information.
    2. Integrate uncertainty estimation to measure prediction confidence.
    3. Implement human-in-the-loop escalation of uncertain cases to medical experts.
    4. Develop a user-friendly web interface.
    5. Evaluate the system using appropriate machine-learning and uncertainty metrics.

    **Planned technical approach**

    Python and Streamlit for the application; Logistic Regression, Random Forest
    and XGBoost as candidate classifiers; probability calibration and conformal
    prediction for uncertainty estimation.
    """)
    st.error("Academic research prototype only. Not a medical device, not clinically validated, and not for use in patient-care decisions.")

st.sidebar.divider()
st.sidebar.caption("Local demonstration database: referral_dss_demo.db")
