import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt

# -------------------------------------------------
# Load ML Model
# -------------------------------------------------

model = joblib.load("models/model.pkl")
encoder = joblib.load("models/label_encoder.pkl")

# -------------------------------------------------
# Streamlit Page Config
# -------------------------------------------------

st.set_page_config(
    page_title="SmartRisk",
    page_icon="🛡️",
    layout="wide"
)

# -------------------------------------------------
# Session State
# -------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "total_predictions" not in st.session_state:
    st.session_state.total_predictions = 0

if "suspicious_predictions" not in st.session_state:
    st.session_state.suspicious_predictions = 0

# -------------------------------------------------
# Header
# -------------------------------------------------

st.title("🛡️ SmartRisk")

st.caption(
    "Real-Time User Behavior Analytics Platform for Insider Threat Detection Using Machine Learning"
)

st.markdown("---")

# -------------------------------------------------
# Sidebar
# -------------------------------------------------

menu = st.sidebar.radio(

    "Navigation",

    [

        "🏠 Manual Prediction",

        "📂 CSV Prediction",

        "📊 Model Insights",

        "ℹ About"

    ]

)

# ==================================================
# MANUAL PREDICTION
# ==================================================

if menu == "🏠 Manual Prediction":

    st.header("Employee Activity")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(

            "Predictions",

            st.session_state.total_predictions

        )

    with c2:

        st.metric(

            "Suspicious",

            st.session_state.suspicious_predictions

        )

    with c3:

        if len(st.session_state.history) == 0:

            avg = 0

        else:

            avg = sum(

                h["Risk"]

                for h in st.session_state.history

            ) / len(st.session_state.history)

        st.metric(

            "Average Risk",

            f"{avg:.1f}%"

        )

    with c4:

        st.metric(

            "ML Model",

            "Random Forest"

        )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        login_hour = st.slider(

            "Login Hour",

            0,

            23,

            9

        )

        failed_logins = st.number_input(

            "Failed Logins",

            0,

            20,

            0

        )

        usb = st.selectbox(

            "USB Usage",

            ["No", "Yes"]

        )

        files = st.number_input(

            "Files Accessed",

            1,

            500,

            50

        )

    with col2:

        emails = st.number_input(

            "Emails Sent",

            0,

            200,

            10

        )

        downloads = st.number_input(

            "Downloads",

            0,

            100,

            5

        )

        after = st.selectbox(

            "After Hours",

            ["No", "Yes"]

        )

        role = st.selectbox(

            "Role",

            [

                "Employee",

                "Manager",

                "Admin"

            ]

        )
    # ==========================================
    # Predict Button
    # ==========================================

    if st.button("🔍 Predict Risk", use_container_width=True):

        usb_value = 1 if usb == "Yes" else 0
        after_value = 1 if after == "Yes" else 0

        role_value = encoder.transform([role])[0]

        sample = pd.DataFrame([{

            "login_hour": login_hour,
            "failed_logins": failed_logins,
            "usb_usage": usb_value,
            "files_accessed": files,
            "emails_sent": emails,
            "downloads": downloads,
            "after_hours": after_value,
            "role": role_value

        }])

        prediction = model.predict(sample)[0]

        probability = model.predict_proba(sample)[0][1]

        risk_score = probability * 100

        # ----------------------------------------
        # Save History
        # ----------------------------------------

        st.session_state.total_predictions += 1

        if prediction == 1:
            st.session_state.suspicious_predictions += 1

        st.session_state.history.append({

            "Role": role,

            "Risk": round(risk_score, 2),

            "Prediction": "Suspicious" if prediction == 1 else "Normal"

        })

        st.markdown("---")

        c1, c2 = st.columns(2)

        with c1:

            if prediction == 1:

                st.error("⚠ Suspicious Activity Detected")

            else:

                st.success("✅ Normal User Activity")

            st.metric(

                "Risk Score",

                f"{risk_score:.2f}%"

            )

            st.progress(float(probability))

            if probability < 0.30:

                st.success("🟢 LOW RISK")

            elif probability < 0.70:

                st.warning("🟠 MEDIUM RISK")

            else:

                st.error("🔴 HIGH RISK")

        with c2:

            st.subheader("Activity Summary")

            st.write(f"**Login Hour:** {login_hour}")

            st.write(f"**Failed Logins:** {failed_logins}")

            st.write(f"**USB Usage:** {usb}")

            st.write(f"**Files Accessed:** {files}")

            st.write(f"**Emails Sent:** {emails}")

            st.write(f"**Downloads:** {downloads}")

            st.write(f"**After Hours:** {after}")

            st.write(f"**Role:** {role}")

        st.markdown("---")

        st.subheader("Prediction History")

        history_df = pd.DataFrame(

            st.session_state.history

        )

        st.dataframe(

            history_df,

            use_container_width=True

        )

        csv = history_df.to_csv(

            index=False

        ).encode("utf-8")

        st.download_button(

            "📥 Download Prediction History",

            csv,

            "prediction_history.csv",

            "text/csv",

            use_container_width=True

        )
    # ===================================================
# CSV PREDICTION
# ===================================================

elif menu == "📂 CSV Prediction":

    st.header("📂 Bulk CSV Prediction")

    st.info(
        "Upload a CSV file with the same columns used during training."
    )

    uploaded = st.file_uploader(
        "Choose CSV File",
        type=["csv"]
    )

    if uploaded is not None:

        df = pd.read_csv(uploaded)

        try:

            temp = df.copy()

            temp["role"] = encoder.transform(temp["role"])

            predictions = model.predict(temp)

            probabilities = model.predict_proba(temp)[:,1]

            df["Prediction"] = [
                "Suspicious" if p == 1 else "Normal"
                for p in predictions
            ]

            df["Risk Score (%)"] = [
                round(i*100,2)
                for i in probabilities
            ]

            st.success("Prediction Completed Successfully!")

            st.dataframe(
                df,
                use_container_width=True
            )

            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(

                "📥 Download Results",

                csv,

                "prediction_results.csv",

                "text/csv",

                use_container_width=True

            )

        except Exception as e:

            st.error("Invalid CSV Format")

            st.exception(e)

# ===================================================
# MODEL INSIGHTS
# ===================================================

elif menu == "📊 Model Insights":

    st.header("📊 Model Insights")

    st.subheader("Feature Importance")

    features = [

        "Login Hour",

        "Failed Logins",

        "USB Usage",

        "Files Accessed",

        "Emails Sent",

        "Downloads",

        "After Hours",

        "Role"

    ]

    importance = model.feature_importances_

    chart = pd.DataFrame({

        "Feature":features,

        "Importance":importance

    })

    chart = chart.sort_values(

        by="Importance",

        ascending=True

    )

    fig, ax = plt.subplots(figsize=(8,5))

    ax.barh(

        chart["Feature"],

        chart["Importance"]

    )

    ax.set_xlabel("Importance Score")

    ax.set_title("Random Forest Feature Importance")

    st.pyplot(fig)

    st.markdown("---")

    st.dataframe(

        chart.sort_values(

            by="Importance",

            ascending=False

        ),

        use_container_width=True

    )


## 🛡 SmartRisk

SmartRisk is a Machine Learning based User Behavior Analytics Platform
developed to identify potential insider threats by analyzing employee
activity logs.

---

### 🎯 Objective

Detect suspicious employee behavior using Machine Learning.

---

### 💻 Technologies Used

- Python

- Streamlit

- Pandas

- Scikit-Learn

- Matplotlib

- Joblib

---

### 🤖 Machine Learning Algorithm

Random Forest Classifier

---

### 📊 Features

✅ Manual Prediction

✅ Bulk CSV Prediction

✅ Risk Score

✅ Prediction History

✅ Download Report

✅ Feature Importance

---


# ===================================================
# FOOTER
# ===================================================

st.markdown("---")

st.caption("© 2026 SmartRisk | Insider Threat Detection using Machine Learning")           