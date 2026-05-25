# AI Smart Agriculture — Production Launch Checklist

> Complete this checklist before going live. Each item must be verified.

---

## 🔐 Security

- [ ] **SECRET_KEY** — Set to a cryptographically random string (min 32 chars)
- [ ] **JWT_SECRET_KEY** — Set to a different random string from SECRET_KEY
- [ ] **Database passwords** — Changed from defaults in `.env.production`
- [ ] **CORS origins** — Set `FRONTEND_URL` to your actual domain
- [ ] **HTTPS/SSL** — SSL certificate configured in Nginx (or via Cloudflare)
- [ ] **CSP headers** — Flask-Talisman active with proper `Content-Security-Policy`
- [ ] **Rate limiting** — Flask-Limiter enabled (100/min general, 10/min auth)
- [ ] **Input sanitization** — HTML escaping active on all string inputs
- [ ] **File upload validation** — MIME type, magic bytes, and file size checks active
- [ ] **SQL injection** — Confirmed: all queries use SQLAlchemy ORM (no raw SQL)

---

## 🗄️ Database

- [ ] **MySQL 8.0** — Running and accessible from the Flask container
- [ ] **Database created** — `agri_db` exists with correct user permissions
- [ ] **Tables created** — `db.create_all()` executed successfully
- [ ] **Indexes verified** — `user_id`, `prediction_type`, `created_at` columns indexed
- [ ] **Connection pooling** — `pool_size=10`, `max_overflow=20`, `pool_pre_ping=True`
- [ ] **Backup scheduled** — Automated daily mysqldump configured
- [ ] **Volume mounted** — `db_data:/var/lib/mysql` for data persistence

---

## 🤖 ML Models

- [ ] **All model files present** in `/models/`:
  - [ ] `crop_model.pkl`
  - [ ] `scaler_crop.pkl`
  - [ ] `label_encoder_crop.pkl`
  - [ ] `yield_model.pkl`
  - [ ] `scaler_yield.pkl`
  - [ ] `encoders_yield.pkl`
  - [ ] `fertilizer_model.pkl`
  - [ ] `scaler_fertilizer.pkl`
  - [ ] `encoders_fertilizer.pkl`
  - [ ] `disease_cnn_model.h5`
  - [ ] `class_names.json`
- [ ] **ModelRegistry** — All models load successfully at startup (check logs)
- [ ] **Test predictions** — Run E2E test: `python tests/e2e_test.py` (13/13 pass)

---

## 🧪 Testing

- [ ] **Unit tests** — `pytest tests/ -v` → 40/40 pass
- [ ] **E2E test** — `python tests/e2e_test.py` → 13/13 pass
- [ ] **Manual smoke test** — Register, login, run each prediction module, download PDF

---

## 🌐 Environment Variables

Verify all are set in `.env.production`:

- [ ] `FLASK_ENV=production`
- [ ] `SECRET_KEY` (unique, random)
- [ ] `JWT_SECRET_KEY` (unique, random)
- [ ] `DATABASE_URL` (mysql+pymysql://user:pass@db:3306/agri_db)
- [ ] `REDIS_URL` (redis://redis:6379/0)
- [ ] `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`
- [ ] `WEATHER_API_KEY` (OpenWeatherMap API key)

---

## 🐳 Docker & Infrastructure

- [ ] **Docker** — Installed and running
- [ ] **Docker Compose** — Version 3.8+ available
- [ ] **Images built** — `docker-compose build` completes without errors
- [ ] **Services healthy** — All containers show `Up (healthy)` in `docker-compose ps`
- [ ] **Nginx** — Reverse proxy serving on ports 80/443
- [ ] **Gunicorn** — Running with 4 workers, timeout=120s
- [ ] **Redis** — Connected and responding to PING
- [ ] **Log rotation** — Docker logging configured (10MB max, 5 files)

---

## 📊 Monitoring

- [ ] **Health endpoint** — `GET /api/health` returns `{"status": "ok"}`
- [ ] **Docker HEALTHCHECK** — Pinging `/api/health` every 30s
- [ ] **Application logs** — `/logs/app.log` with rotation (10MB, 5 backups)
- [ ] **ML audit logs** — All predictions logged with input hash
- [ ] **Error tracking** — 500 errors logged with full traceback

---

## 🎨 Frontend

- [ ] **Assets bundled** — `bundle.min.css` and `bundle.min.js` generated
- [ ] **HTML updated** — All pages reference bundled assets
- [ ] **Lazy loading** — `loading="lazy"` on all images
- [ ] **Responsive** — Tested on mobile, tablet, and desktop viewports
- [ ] **Error pages** — Custom 404 and 500 error responses (JSON format)

---

## 👤 Admin Account

- [ ] **Admin user created** — At least one user with `role: admin`
- [ ] **Admin panel accessible** — `/admin.html` loads with stats
- [ ] **Dataset management** — Can list and upload CSV files
- [ ] **Retraining** — Can trigger and monitor model retraining jobs

---

## 📝 Documentation

- [ ] **README.md** — Project overview, setup instructions, architecture
- [ ] **API docs** — All endpoints documented (`docs/api-docs.md`)
- [ ] **User manual** — Farmer guide (`docs/user-manual.md`)
- [ ] **Admin manual** — Admin guide (`docs/admin-manual.md`)

---

## 🚀 Final Go/No-Go

| Check | Status |
|---|---|
| All security items green | ☐ |
| Database backed up | ☐ |
| All tests passing | ☐ |
| Admin account working | ☐ |
| SSL configured | ☐ |
| Domain DNS pointing correctly | ☐ |
| Monitoring active | ☐ |

**Sign-off:** _______________________ **Date:** _______________
