# AI Smart Agriculture — API Documentation

> **Base URL:** `http://localhost:5000/api`  
> **Auth:** JWT Bearer Token (pass as `Authorization: Bearer <token>`)  
> **Rate Limits:** 100 req/min per user (10 req/min on auth endpoints)

---

## Standard Response Format

All endpoints return JSON in this structure:

**Success:**
```json
{
  "success": true,
  "message": "Description of result",
  "data": { ... }
}
```

**Error:**
```json
{
  "success": false,
  "error": "Description of error",
  "code": 400
}
```

---

## Error Codes

| Code | Meaning |
|---|---|
| 400 | Bad Request — invalid or missing input |
| 401 | Unauthorized — missing or invalid JWT |
| 403 | Forbidden — insufficient permissions (e.g., non-admin accessing admin route) |
| 404 | Not Found — resource doesn't exist |
| 409 | Conflict — duplicate resource (e.g., email already registered) |
| 429 | Too Many Requests — rate limit exceeded |
| 500 | Internal Server Error — unexpected server failure |

---

## 1. Authentication

### POST `/auth/register`
Register a new user.

| Field | Required | Details |
|---|---|---|
| Auth | No | — |
| Rate Limit | 10/min | — |

**Request Body:**
```json
{
  "name": "Ravi Kumar",
  "email": "ravi@farm.com",
  "password": "SecurePass123!"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Registration successful",
  "data": {
    "user": { "id": 1, "name": "Ravi Kumar", "email": "ravi@farm.com", "role": "farmer" },
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

---

### POST `/auth/login`

| Field | Required | Details |
|---|---|---|
| Auth | No | — |
| Rate Limit | 10/min | — |

**Request Body:**
```json
{ "email": "ravi@farm.com", "password": "SecurePass123!" }
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user": { "id": 1, "name": "Ravi Kumar", "email": "ravi@farm.com", "role": "farmer" },
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

---

### GET `/auth/me`

| Field | Required | Details |
|---|---|---|
| Auth | **Yes** | JWT Bearer |

**Response (200):**
```json
{ "success": true, "data": { "user": { "id": 1, "name": "Ravi Kumar", "email": "ravi@farm.com", "role": "farmer" } } }
```

---

### POST `/auth/logout`

| Field | Required | Details |
|---|---|---|
| Auth | **Yes** | JWT Bearer |

**Response (200):**
```json
{ "success": true, "message": "Successfully logged out" }
```

---

## 2. Crop Recommendation

### POST `/recommend/crop`

| Field | Required | Details |
|---|---|---|
| Auth | **Yes** | JWT Bearer |

**Request Body:**
```json
{
  "nitrogen": 90, "phosphorus": 42, "potassium": 43,
  "temperature": 25.5, "humidity": 80, "ph": 6.5, "rainfall": 200
}
```

| Param | Type | Validation |
|---|---|---|
| nitrogen | float | ≥ 0 |
| phosphorus | float | ≥ 0 |
| potassium | float | ≥ 0 |
| temperature | float | 0–60 |
| humidity | float | 0–100 |
| ph | float | 0–14 |
| rainfall | float | ≥ 0 |

**Response (200):**
```json
{
  "success": true,
  "message": "Crop recommendation successful",
  "data": {
    "crop": "Rice",
    "confidence": 95.3,
    "info": { "season": "Kharif", "water_needs": "High", "growing_tips": "..." },
    "prediction_id": 42
  }
}
```

---

## 3. Disease Detection

### POST `/detect/disease`

| Field | Required | Details |
|---|---|---|
| Auth | **Yes** | JWT Bearer |
| Content-Type | multipart/form-data | — |
| Max Upload | 5 MB | JPEG or PNG only |

**Request:** Multipart form with field `image` containing a leaf photo.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "disease": "Apple Scab",
    "confidence": 92.5,
    "remedy": "Apply fungicide spray...",
    "symptoms": "Dark spots on leaves",
    "severity": "Medium",
    "affected_crops": ["Apple"],
    "image_url": "/static/uploads/diseases/1/1716560000.jpg",
    "prediction_id": 43
  }
}
```

---

## 4. Yield Prediction

### POST `/predict/yield`

| Field | Required | Details |
|---|---|---|
| Auth | **Yes** | JWT Bearer |

**Request Body:**
```json
{
  "crop": "Rice", "season": "Kharif", "region": "Karnataka",
  "area_ha": 2.5, "rainfall": 180, "fertilizer_kg": 120, "pesticide_kg": 1.5
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "yield_per_ha": 3500.0,
    "total_yield_kg": 8750.0,
    "unit": "kg",
    "crop": "Rice"
  }
}
```

---

## 5. Fertilizer Recommendation

### POST `/recommend/fertilizer`

| Field | Required | Details |
|---|---|---|
| Auth | **Yes** | JWT Bearer |

**Request Body:**
```json
{
  "nitrogen": 50, "phosphorus": 50, "potassium": 50,
  "temperature": 25, "humidity": 60, "moisture": 40,
  "soil_type": "Sandy", "crop": "Wheat"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "fertilizer": "Urea",
    "confidence": 88.5,
    "quantity_kg_per_acre": "50",
    "application_method": "Broadcast",
    "description": "High nitrogen content...",
    "warning": "Avoid over-application",
    "input_npk": { "nitrogen": 50, "phosphorus": 50, "potassium": 50 }
  }
}
```

---

## 6. History

### GET `/history/?type=all&page=1&per_page=20`

| Param | Default | Details |
|---|---|---|
| type | all | Filter: `crop`, `disease`, `yield`, `fertilizer`, `all` |
| page | 1 | Page number |
| per_page | 20 | Items per page (max 100) |

**Response (200):**
```json
{
  "data": {
    "history": [
      {
        "id": 42,
        "prediction_type": "crop_recommendation",
        "summary": "Recommended: Rice",
        "icon": "fa-leaf",
        "badge_color": "#16a34a",
        "created_at": "2026-05-25T00:00:00"
      }
    ],
    "pagination": { "page": 1, "per_page": 20, "total": 42, "total_pages": 3 }
  }
}
```

### DELETE `/history/<id>`
Delete a specific prediction record. Auth required.

### GET `/history/export`
Download all history as CSV. Auth required.

---

## 7. PDF Report

### GET `/report/<prediction_type>/<prediction_id>`
Download a generated PDF report. Auth required.

**Prediction types:** `crop_recommendation`, `disease_detection`, `yield_prediction`, `fertilizer_recommendation`

**Response:** Binary PDF file (`application/pdf`).

---

## 8. Weather

### GET `/weather?lat=12.97&lon=77.59` or `/weather?city=Bangalore`

| Field | Required | Details |
|---|---|---|
| Auth | No | Public endpoint |

**Response (200):**
```json
{
  "data": {
    "success": true,
    "city": "Bangalore",
    "temperature": 28.5,
    "humidity": 65,
    "description": "Partly cloudy",
    "wind_speed": 3.2,
    "icon": "02d"
  }
}
```

---

## 9. Health Check

### GET `/health`

**Response (200):**
```json
{ "status": "ok", "db": "connected", "models_loaded": true }
```

---

## 10. Admin Endpoints

All admin endpoints require `role: admin` on the JWT user.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/admin/stats` | Dashboard statistics |
| GET | `/admin/users?page=1` | Paginated user list |
| PUT | `/admin/users/<id>` | Update user role/status |
| DELETE | `/admin/users/<id>` | Delete user |
| GET | `/admin/datasets` | List CSV datasets |
| POST | `/admin/datasets/upload` | Upload CSV dataset |
| POST | `/admin/retrain/<model_type>` | Trigger model retraining |
| GET | `/admin/retrain/status/<job_id>` | Check retraining status |
