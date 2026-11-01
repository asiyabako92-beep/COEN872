# Nigeria PHC Referral DSS — Prototype

## Current status
This is Stage 1 of the MSc project implementation. It provides a working Streamlit interface and a local SQLite database for fictional or authorised de-identified demonstration assessments.

**It does not contain a trained AI model and does not generate clinical referral recommendations.** Do not use it for real patient-care decisions.

## Pages included
- Dashboard
- Patient Assessment
- AI Recommendation (clearly marked as unavailable)
- Uncertainty & Expert Review (manual demonstration review record)
- Analytics (prototype data overview and CSV export)
- About the Project

## Requirements
- Windows 10/11
- Python 3.10 or later
- Internet connection for the initial package installation

## Installation on Windows
1. Extract the ZIP file.
2. Open the extracted `AI_Health_Referral_DSS` folder.
3. Click the address bar in File Explorer, type `cmd`, and press Enter.
4. Create a virtual environment:

   ```bat
   python -m venv venv
   ```

5. Activate it:

   ```bat
   venv\Scripts\activate
   ```

6. Install the packages:

   ```bat
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

7. Start the application:

   ```bat
   streamlit run app.py
   ```

The application should open in your browser. If it does not, copy the local URL shown in Command Prompt (usually `http://localhost:8501`) into your browser.

## Local data storage
Assessment and demonstration review records are stored in `referral_dss_demo.db` in the application folder. Keep this file private. Do not enter patient names, phone numbers, addresses or other direct identifiers.

To reset the demonstration database, stop the app and delete `referral_dss_demo.db`. This permanently deletes the locally stored demonstration records.

## Next development stages
1. Select and document an appropriate referral-labelled dataset.
2. Inspect data fields, labels, class balance, missingness and suitability for the Nigerian PHC context.
3. Build reproducible preprocessing and model-training pipelines.
4. Compare candidate models using appropriate validation.
5. Calibrate probabilities and implement conformal prediction / abstention.
6. Integrate model output and uncertainty-aware escalation.
7. Conduct testing, ethical review and documentation.

Do not interpret synthetic or rule-generated labels as actual clinician referral decisions.
