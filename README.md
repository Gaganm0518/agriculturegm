# 🌾 AI Smart Agriculture

> An AI-powered platform that helps Indian farmers make data-driven decisions about crops, diseases, yields, and fertilizers using machine learning.

---

## ✨ Features

| Module | Description |
|---|---|
| 🌱 **Crop Recommendation** | Recommends the best crop based on soil nutrients (N, P, K), temperature, humidity, pH, and rainfall |
| 🔬 **Disease Detection** | Upload a leaf photo to identify plant diseases using a CNN deep learning model |
| 📊 **Yield Prediction** | Estimates crop yield per hectare based on farming parameters |
| 🧪 **Fertilizer Advice** | Recommends the right fertilizer with dosage and application instructions |
| 🌤️ **Weather Insights** | Real-time weather data via OpenWeatherMap API |
| 📜 **History & Reports** | Full prediction history with filtering, export to CSV, and downloadable PDF reports |
| 🛡️ **Admin Panel** | User management, dataset uploads, model retraining triggers |
| 🌐 **Multi-Language** | English, Hindi, Kannada support |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10, Flask 3.0, Gunicorn |
| **ML Models** | scikit-learn, TensorFlow/Keras, Pandas, NumPy |
| **Database** | MySQL 8.0 (Production), SQLite (Development) |
| **Cache** | Redis 7.2 with Flask-Caching |
| **Auth** | JWT (Flask-JWT-Extended), Bcrypt |
| **Frontend** | Vanilla HTML/CSS/JS, Font Awesome |
| **PDF Reports** | ReportLab |
| **Infra** | Docker, Docker Compose, Nginx |
| **Security** | Flask-Talisman (CSP/HSTS), Flask-Limiter, Flask-CORS, input sanitization |
| **CI/CD** | GitHub Actions |

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────┐     ┌──────────────────────────┐
│   Browser    │────▶│  Nginx   │────▶│   Flask + Gunicorn       │
│  (Frontend)  │     │  :80/443 │     │   :5000 (4 workers)      │
└─────────────┘     └──────────┘     │                          │
                                      │  ┌──────────────────┐   │
                                      │  │  ModelRegistry    │   │
                                      │  │  (Thread-safe)    │   │
                                      │  └──────────────────┘   │
                                      │           │              │
                         ┌────────────┤           │              │
                         │            │  ┌────────▼─────────┐   │
                    ┌────▼────┐       │  │ ML Models (.pkl)  │   │
                    │  MySQL  │       │  │ CNN (.h5)         │   │
                    │  :3306  │       │  └──────────────────┘   │
                    └─────────┘       │                          │
                    ┌─────────┐       └──────────────────────────┘
                    │  Redis  │
                    │  :6379  │
                    └─────────┘
```

---

## 🚀 Setup Instructions

### Local Development

```bash
# 1. Clone the repo
git clone https://github.com/your-org/ai-smart-agriculture.git
cd ai-smart-agriculture

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.template .env
# Edit .env with your database URL, API keys, etc.

# 5. Run the development server
python run.py
# Open http://localhost:5000
```

### Docker Production Deployment

```bash
# 1. Configure environment
cp .env.production .env
# Edit .env with production secrets

# 2. Build and start all services
docker-compose up -d --build

# 3. Or use the deployment script
chmod +x deploy.sh
./deploy.sh

# The app will be available at http://localhost (port 80)
```

---

## 📁 Project Structure

```
ai-smart-agriculture/
├── backend/
│   ├── app.py              # Flask application factory
│   ├── config.py           # Configuration classes
│   ├── extensions.py       # Flask extension instances
│   ├── models/             # SQLAlchemy database models
│   ├── routes/             # API route blueprints
│   ├── services/           # ML services, email, weather, logging
│   └── utils/              # Helpers, validators
├── frontend/               # HTML pages
├── static/
│   ├── css/                # Stylesheets (bundle.min.css)
│   └── js/                 # JavaScript (bundle.min.js)
├── models/                 # Trained ML model files (.pkl, .h5)
├── datasets/               # Training data CSVs
├── tests/                  # Pytest test suite (40+ tests)
├── docs/                   # Documentation
├── nginx/                  # Nginx configuration
├── Dockerfile              # Container build
├── docker-compose.yml      # Multi-container orchestration
├── deploy.sh               # Deployment script
├── requirements.txt        # Python dependencies
└── run.py                  # Development entry point
```

---

## 📸 Screenshots

> *Screenshot placeholder: Login page*

> *Screenshot placeholder: Dashboard with stats*

> *Screenshot placeholder: Crop recommendation results*

> *Screenshot placeholder: Disease detection upload & results*

> *Screenshot placeholder: History page with filters*

---

## 🧪 Testing

```bash
# Run all unit tests
PYTHONPATH=. pytest tests/ -v

# Run end-to-end integration test
PYTHONPATH=. python tests/e2e_test.py
```

**Test Coverage:** 40 unit tests + 13-step E2E integration test covering the full farmer journey.

---

## 📚 Documentation

- [API Documentation](docs/api-docs.md)
- [User Manual](docs/user-manual.md)
- [Admin Manual](docs/admin-manual.md)
- [Launch Checklist](docs/checklist.md)

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 AI Smart Agriculture

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```
