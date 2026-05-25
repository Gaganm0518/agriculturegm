# AI Smart Agriculture — User Manual

> A step-by-step guide for farmers to use the AI Smart Agriculture platform.

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Dashboard Overview](#2-dashboard-overview)
3. [Crop Recommendation](#3-crop-recommendation)
4. [Disease Detection](#4-disease-detection)
5. [Yield Prediction](#5-yield-prediction)
6. [Fertilizer Advice](#6-fertilizer-advice)
7. [Weather Insights](#7-weather-insights)
8. [Prediction History](#8-prediction-history)
9. [Downloading PDF Reports](#9-downloading-pdf-reports)
10. [FAQ](#10-faq)

---

## 1. Getting Started

### Registration

1. Open the website and click **"Register"** on the login page.
2. Enter your **Full Name**, **Email**, and create a **Password** (min 8 characters with at least one number and one uppercase letter).
3. Click **"Create Account"**.
4. You will be automatically logged in and redirected to the Dashboard.

> *Screenshot placeholder: Registration form*

### Login

1. Enter your registered **Email** and **Password**.
2. Click **"Login"**.
3. Your session lasts 24 hours. After that, you'll need to log in again.

> *Screenshot placeholder: Login page*

---

## 2. Dashboard Overview

The Dashboard is your command center. It shows:

- **Quick Stats** — Total predictions made, recent activity
- **Module Cards** — Quick access to Crop, Disease, Yield, and Fertilizer tools
- **Weather Widget** — Live weather for your location
- **Recent Predictions** — Your latest 5 predictions

> *Screenshot placeholder: Dashboard overview*

---

## 3. Crop Recommendation

This module recommends the best crop to grow based on your soil and weather conditions.

### How to Use

1. Click **"Crop Recommendation"** from the sidebar or Dashboard.
2. Fill in:
   - **Nitrogen (N)** — Soil nitrogen content (mg/kg)
   - **Phosphorus (P)** — Soil phosphorus content (mg/kg)
   - **Potassium (K)** — Soil potassium content (mg/kg)
   - **Temperature** — Average temperature (°C)
   - **Humidity** — Relative humidity (%)
   - **pH** — Soil pH (0–14)
   - **Rainfall** — Annual rainfall (mm)
3. Click **"Get Recommendation"**.

### Interpreting Results

- **Recommended Crop** — The AI's top suggestion
- **Confidence Score** — How certain the model is (higher is better)
- **Season** — Best planting season
- **Water Needs** — High/Medium/Low irrigation requirements
- **Growing Tips** — Practical advice for cultivating the crop

> *Screenshot placeholder: Crop recommendation results*

---

## 4. Disease Detection

Upload a photo of a diseased leaf to identify the plant disease.

### How to Use

1. Click **"Disease Detection"** from the sidebar.
2. Click the upload area or drag-and-drop a leaf photo.
   - **Accepted formats:** JPEG, PNG
   - **Max size:** 5 MB
   - **Tip:** Take a clear, close-up photo in natural daylight
3. Click **"Detect Disease"**.

### Interpreting Results

- **Detected Disease** — Name of the identified disease
- **Confidence** — Model certainty percentage
- **Severity** — Low / Medium / High
- **Symptoms** — Description of visible symptoms
- **Remedy** — Recommended treatment steps
- **Affected Crops** — Other crops vulnerable to this disease

> *Screenshot placeholder: Disease detection results*

---

## 5. Yield Prediction

Estimate your expected crop yield based on farming parameters.

### How to Use

1. Click **"Yield Prediction"** from the sidebar.
2. Fill in:
   - **Crop** — Select from dropdown (Rice, Wheat, Maize, etc.)
   - **Season** — Kharif, Rabi, or Whole Year
   - **Region** — Your state/region
   - **Area (ha)** — Farm area in hectares
   - **Rainfall (mm)** — Expected annual rainfall
   - **Fertilizer (kg)** — Total fertilizer to be applied
   - **Pesticide (kg)** — Total pesticide to be applied
3. Click **"Predict Yield"**.

### Interpreting Results

- **Yield per Hectare** — Expected output in kg/ha
- **Total Yield** — Yield per ha × your total area
- **Unit** — Always in kilograms (kg)

> *Screenshot placeholder: Yield prediction results*

---

## 6. Fertilizer Advice

Get AI-powered fertilizer recommendations based on your soil composition.

### How to Use

1. Click **"Fertilizer Advice"** from the sidebar.
2. Fill in:
   - **Nitrogen, Phosphorus, Potassium** — Soil nutrient levels
   - **Soil Type** — Sandy, Loamy, Black, Red, Clayey
   - **Crop** — What you plan to grow
   - **Moisture** — Soil moisture (%)
   - **Temperature** — Current temperature (°C)
   - **Humidity** — Atmospheric humidity (%)
3. Click **"Get Recommendation"**.

### Interpreting Results

- **Recommended Fertilizer** — Brand/type name
- **Confidence** — Model certainty
- **Dosage** — Kg per acre to apply
- **Application Method** — How to apply (broadcast, drip, etc.)
- **Warning** — Important safety precautions

> *Screenshot placeholder: Fertilizer recommendation results*

---

## 7. Weather Insights

View real-time weather data for your farm location.

1. Click **"Weather Insights"** from the sidebar.
2. The system automatically detects your location (or enter a city name).
3. View current temperature, humidity, wind speed, and weather conditions.

---

## 8. Prediction History

All your past predictions are saved and accessible.

1. Click **"My History"** from the sidebar.
2. Use **filter tabs** to view by type (Crop, Disease, Yield, Fertilizer).
3. Click the **eye icon** to view full details of any prediction.
4. Click the **trash icon** to delete a record.
5. Use the **"Export CSV"** button to download all history as a spreadsheet.
6. Use **pagination** at the bottom to navigate through records.

> *Screenshot placeholder: History page with filter tabs*

---

## 9. Downloading PDF Reports

For any prediction, you can generate a professional PDF report.

1. Go to **My History**.
2. Click the **eye icon** on any prediction.
3. In the detail modal, click **"Download PDF Report"**.
4. The PDF includes: input parameters, prediction results, remedy/guidelines, and a disclaimer.

---

## 10. FAQ

### Q1: Is my data secure?
**A:** Yes. All data is encrypted in transit (HTTPS) and stored securely in our database. Only you can access your predictions.

### Q2: How accurate are the crop recommendations?
**A:** Our ML models are trained on extensive agricultural datasets and typically achieve 90–98% accuracy. However, always consult local agricultural experts for critical decisions.

### Q3: What image quality do I need for disease detection?
**A:** Take a clear, well-lit photo of the affected leaf. Close-up shots in natural daylight work best. Avoid blurry or dark images.

### Q4: Can I use this on my phone?
**A:** Yes! The website is fully responsive and works on smartphones, tablets, and desktops.

### Q5: Do I need internet to use it?
**A:** Yes, an internet connection is required to access the ML models and weather data.

### Q6: Why is my confidence score low?
**A:** Low confidence means the input data doesn't clearly match any pattern the model has seen. Try verifying your soil test values and re-entering them.

### Q7: Can I get results in my local language?
**A:** Yes! The platform supports English, Hindi (हिन्दी), and Kannada (ಕನ್ನಡ). Use the language switcher in the sidebar.

### Q8: How do I get a soil test done?
**A:** Contact your nearest Krishi Vigyan Kendra (KVK) or agricultural extension center. They can test your soil for N, P, K, pH levels.

### Q9: Is the platform free to use?
**A:** Yes, the platform is completely free for farmers.

### Q10: Who do I contact for support?
**A:** Email us at support@aismartagri.com or use the feedback form on the website.
