# AI Smart Agriculture — Admin Manual

> Guide for platform administrators to manage users, datasets, and model retraining.

---

## Table of Contents

1. [Accessing the Admin Panel](#1-accessing-the-admin-panel)
2. [Dashboard Statistics](#2-dashboard-statistics)
3. [Managing Users](#3-managing-users)
4. [Managing Datasets](#4-managing-datasets)
5. [Model Retraining](#5-model-retraining)
6. [Monitoring & Logs](#6-monitoring--logs)

---

## 1. Accessing the Admin Panel

### Prerequisites
- Your account must have `role: admin`.
- To create the first admin account, register normally, then update the database:
  ```sql
  UPDATE users SET role = 'admin' WHERE email = 'admin@yourdomain.com';
  ```
  Or set `role` to `admin` in the registration API: `{"name": "Admin", "email": "...", "password": "...", "role": "admin"}`

### Access
- Navigate to `/admin.html` in your browser (requires login).
- All admin API endpoints are prefixed with `/api/admin/`.

---

## 2. Dashboard Statistics

**Endpoint:** `GET /api/admin/stats`

The admin dashboard shows:

| Metric | Description |
|---|---|
| Total Users | All registered farmers |
| Total Predictions | All predictions across all users |
| Predictions Today | Predictions made since midnight |
| Active Users (Weekly) | Distinct users who made predictions in the last 7 days |
| Distribution | Breakdown by type: Crop, Disease, Yield, Fertilizer |
| Trend Chart | Predictions per day for the last 7 days |

---

## 3. Managing Users

### View All Users
**Endpoint:** `GET /api/admin/users?page=1&per_page=20`

Shows a paginated list of all users with:
- Name, email, role, join date
- Number of predictions made

### Update User Role or Status
**Endpoint:** `PUT /api/admin/users/<user_id>`

```json
{
  "role": "admin",       // or "farmer"
  "is_active": true      // or false to disable account
}
```

**Use cases:**
- Promote a trusted farmer to admin
- Disable a spammer's account (set `is_active: false`)

### Delete a User
**Endpoint:** `DELETE /api/admin/users/<user_id>`

- Permanently deletes the user and all their predictions.
- **You cannot delete yourself** (safety check).
- This action is irreversible.

---

## 4. Managing Datasets

### View Available Datasets
**Endpoint:** `GET /api/admin/datasets`

Lists all `.csv` files in the `/datasets/` directory with:
- File name, size, last modified date, row count

### Upload a New Dataset
**Endpoint:** `POST /api/admin/datasets/upload`

- Upload a CSV file using `multipart/form-data` with field name `file`.
- Only `.csv` files are accepted.
- The file is saved to `/datasets/` and can be used for retraining.

**Important:**
- Ensure column headers match the expected training format.
- Back up the existing dataset before overwriting.

### Dataset Format Requirements

| Model | Required Columns |
|---|---|
| Crop | N, P, K, temperature, humidity, ph, rainfall, label |
| Disease | Image folder structure (class_name/image.jpg) |
| Yield | Crop, Crop_Year, Season, State, Area, Production, Annual_Rainfall, Fertilizer, Pesticide |
| Fertilizer | Temperature, Humidity, Moisture, Soil Type, Crop Type, Nitrogen, Phosphorous, Potassium, Fertilizer Name |

---

## 5. Model Retraining

### Trigger Retraining
**Endpoint:** `POST /api/admin/retrain/<model_type>`

**Valid model types:** `crop`, `disease`, `yield`, `fertilizer`

- Starts a background training thread.
- Returns a `job_id` to track progress.

### Check Training Status
**Endpoint:** `GET /api/admin/retrain/status/<job_id>`

**Response includes:**
- `status`: `pending`, `running`, `completed`, or `failed`
- `accuracy`: Final model accuracy (if completed)
- `error`: Error message (if failed)
- `log_tail`: Last 30 lines of the training log

### Retraining Workflow

1. Upload updated dataset via the Datasets panel.
2. Click "Retrain" for the relevant model type.
3. Monitor the job status until it shows `completed`.
4. The new model file is automatically saved to `/models/`.
5. **Restart the application** to load the new model (or the ModelRegistry will pick it up on next request cycle).

---

## 6. Monitoring & Logs

### Application Logs
- Location: `/logs/app.log`
- Rotation: Max 10 MB per file, 5 backups
- Every API request is logged with: method, endpoint, user_id, response time, status code
- All ML predictions include input hash for audit trail

### Docker Logs
```bash
# View web container logs
docker-compose logs -f web

# View nginx access logs
docker-compose logs -f nginx
```

### Health Check
- **Endpoint:** `GET /api/health`
- Returns database connection status and model availability.
- Docker HEALTHCHECK pings this every 30 seconds.

### Database Backups
```bash
# Manual MySQL backup
docker-compose exec db mysqldump -u agri_user -p agri_db > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -i db mysql -u agri_user -p agri_db < backup.sql
```
