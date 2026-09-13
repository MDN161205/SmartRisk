import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SmartRisk",
    page_icon="🛡️",
    layout="wide"
)


# =========================================================
# LOAD ML MODEL
# =========================================================

model = joblib.load("models/model.pkl")
encoder = joblib.load("models/label_encoder.pkl")


# =========================================================
# SESSION STATE
# =========================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "total_predictions" not in st.session_state:
    st.session_state.total_predictions = 0

if "suspicious_predictions" not in st.session_state:
    st.session_state.suspicious_predictions = 0


# =========================================================
# HEADER
# =========================================================

st.title("🛡️ SmartRisk")

st.caption(
    "Real-Time User Behavior Analytics Platform "
    "for Insider Threat Detection Using Machine Learning"
)

st.markdown("---")


# =========================================================
# SIDEBAR
# =========================================================

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Manual Prediction",
        "📂 CSV Prediction",
        "📊 Model Insights",
        "ℹ About"
    ]
)


# =========================================================
# MANUAL PREDICTION
# =========================================================

if menu == "🏠 Manual Prediction":

    st.header("Employee Activity")

    # -----------------------------------------------------
    # Dashboard Metrics
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Input Section
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        login_hour = st.slider(
            "Login Hour",
            min_value=0,
            max_value=23,
            value=9
        )

        failed_logins = st.number_input(
            "Failed Logins",
            min_value=0,
            max_value=20,
            value=0
        )

        usb = st.selectbox(
            "USB Usage",
            ["No", "Yes"]
        )

        files = st.number_input(
            "Files Accessed",
            min_value=1,
            max_value=500,
            value=50
        )


    with col2:

        emails = st.number_input(
            "Emails Sent",
            min_value=0,
            max_value=200,
            value=10
        )

        downloads = st.number_input(
            "Downloads",
            min_value=0,
            max_value=100,
            value=5
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


    # -----------------------------------------------------
    # Prediction Button
    # -----------------------------------------------------

    if st.button(
        "🔍 Predict Risk",
        use_container_width=True
    ):

        try:

        
  # Convert Yes/No values to numbers
            usb_value = 1 if usb == "Yes" else 0
            after_value = 1 if after == "Yes" else 0
 
            # Encode role
            role_value = encoder.transform([role])[0]

            # Create input DataFrame
            sample = pd.DataFrame([
                {
                    "login_hour": login_hour,
                    "failed_logins": failed_logins,
                    "usb_usage": usb_value,
                    "files_accessed": files,
                    "emails_sent": emails,
                    "downloads": downloads,
                    "after_hours": after_value,
                    "role": role_value
                }
            ])

            # Make prediction
            prediction = model.predict(sample)[0]

            # Get probability
            probability = model.predict_proba(sample)[0][1]

            risk_score = probability * 100

            # Update counters
            st.session_state.total_predictions += 1

            if prediction == 1:
                st.session_state.suspicious_predictions += 1

            # Save prediction history
            st.session_state.history.append(
                {
                    "Role": role,
                    "Risk": round(risk_score, 2),
                    "Prediction": (
                        "Suspicious"
                        if prediction == 1
                        else "Normal"
                    )
                }
            )

            st.markdown("---")

            # Result section
            result_col1, result_col2 = st.columns(2)

            with result_col1:

                if prediction == 1:
                    st.error(
                        "⚠️ Suspicious Activity Detected"
                    )
                else:
                    st.success(
                        "✅ Normal User Activity"
                    )

                st.metric(
                    "Risk Score",
                    f"{risk_score:.2f}%"
                )

                st.progress(
                    float(probability)
                )

                if probability < 0.30:
                    st.success("🟢 LOW RISK")

                elif probability < 0.70:
                    st.warning("🟠 MEDIUM RISK")

                else:
                    st.error("🔴 HIGH RISK")

            with result_col2:

                st.subheader("Activity Summary")

                st.write(
                    f"**Login Hour:** {login_hour}"
                )

                st.write(
                    f"**Failed Logins:** {failed_logins}"
                )

                st.write(
                    f"**USB Usage:** {usb}"
                )

                st.write(
                    f"**Files Accessed:** {files}"
                )

                st.write(
                    f"**Emails Sent:** {emails}"
                )

                st.write(
                    f"**Downloads:** {downloads}"
                )

                st.write(
                    f"**After Hours:** {after}"
                )

                st.write(
                    f"**Role:** {role}"
                )

            st.markdown("---")

            # Prediction History
            st.subheader("Prediction History")

            history_df = pd.DataFrame(
                st.session_state.history
            )

            st.dataframe(
                history_df,
                use_container_width=True
            )

            # Download history
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

        except Exception as e:

            st.error(
                "Prediction failed. Please check the "
                "input values and model files."
            )

            st.exception(e)


# =========================================================
# CSV PREDICTION
# =========================================================

elif menu == "📂 CSV Prediction":

    st.header("📂 Bulk CSV Prediction")

    st.info(
        "Upload a CSV file containing the same "
        "features used during model training."
    )

    uploaded = st.file_uploader(
        "Choose CSV File",
        type=["csv"]
    )

    if uploaded is not None:

        try:

            df = pd.read_csv(uploaded)

            st.subheader("Uploaded Data")

            st.dataframe(
                df,
                use_container_width=True
            )

            required_columns = [
                "login_hour",
                "failed_logins",
                "usb_usage",
                "files_accessed",
                "emails_sent",
                "downloads",
                "after_hours",
                "role"
            ]

            missing_columns = [
                column
                for column in required_columns
                if column not in df.columns
            ]

            if missing_columns:

                st.error(
                    "Missing required columns:"
                )

                st.write(missing_columns)

            else:

                temp = df.copy()

                temp["role"] = encoder.transform(
                    temp["role"]
                )

                predictions = model.predict(
                    temp[required_columns]
                )

                probabilities = model.predict_proba(
                    temp[required_columns]
                )[:, 1]

                df["Prediction"] = [
                    "Suspicious"
                    if p == 1
                    else "Normal"
                    for p in predictions
                ]

                df["Risk Score (%)"] = [
                    round(p * 100, 2)
                    for p in probabilities
                ]

                st.success(
                    "✅ Prediction Completed Successfully!"
                )

                st.subheader(
                    "Prediction Results"
                )

                st.dataframe(
                    df,
                    use_container_width=True
                )

                result_csv = df.to_csv(
                    index=False
                ).encode("utf-8")

                st.download_button(
                    "📥 Download Results",
                    result_csv,
                    "prediction_results.csv",
                    "text/csv",
                    use_container_width=True
                )

        except Exception as e:

            st.error(
                "Invalid CSV format or prediction error."
            )

            st.exception(e)


# =========================================================
# MODEL INSIGHTS
# =========================================================

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

    chart = pd.DataFrame(
        {
            "Feature": features,
            "Importance": importance
        }
    )

    chart = chart.sort_values(
        by="Importance",
        ascending=True
    )

    fig, ax = plt.subplots(
        figsize=(8, 5)
    )

    ax.barh(
        chart["Feature"],
        chart["Importance"]
    )

    ax.set_xlabel(
        "Importance Score"
    )

    ax.set_title(
        "Random Forest Feature Importance"
    )

    st.pyplot(fig)

    plt.close(fig)

    st.markdown("---")

    st.subheader(
        "Feature Importance Details"
    )

    st.dataframe(
        chart.sort_values(
            by="Importance",
            ascending=False
        ),
        use_container_width=True
    )


# =========================================================
# ABOUT
# =========================================================

elif menu == "ℹ About":

    st.header("🛡️ About SmartRisk")

    st.write(
        """
        SmartRisk is a Machine Learning based
        User Behavior Analytics Platform designed
        to identify potential insider threats by
        analyzing employee activity data.
        """
    )

    st.markdown("---")

    st.subheader("🎯 Objective")

    st.write(
        """
        The objective of SmartRisk is to analyze
        employee behavior and classify activity
        as normal or potentially suspicious using
        a Machine Learning model.
        """
    )

    st.subheader("💻 Technologies Used")

    st.write(
        """
        • Python

        • Streamlit

        • Pandas

        • Scikit-Learn

        • Matplotlib

        • Joblib
        """
    )

    st.subheader("🤖 Machine Learning Algorithm")

    st.write(
        "Random Forest Classifier"
    )

    st.subheader("📊 Main Features")

    st.write(
        """
        • Manual Risk Prediction

        • Bulk CSV Prediction

        • Risk Score Calculation

        • Prediction History

        • Downloadable Prediction Results

        • Feature Importance Visualization
        """
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "© 2026 SmartRisk | "
    "Insider Threat Detection using Machine Learning"
)