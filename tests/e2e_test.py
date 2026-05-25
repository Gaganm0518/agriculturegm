"""
End-to-End Integration Test Script
Tests the complete farmer journey through the AI Smart Agriculture API.
"""
import json, io, sys, os
from unittest.mock import patch
from PIL import Image

os.environ['FLASK_ENV'] = 'testing'

from backend.app import create_app
from backend.extensions import db

app = create_app('testing')
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['RATELIMIT_ENABLED'] = False

results = []
def log(step, status, detail=''):
    results.append(f'[{status}] {step}: {detail}')
    print(f'[{status}] {step}: {detail}')

def make_jpeg():
    img = Image.new('RGB', (100, 100), color=(0, 128, 0))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf

with app.app_context():
    db.create_all()
    with app.test_client() as c:

        # === STEP 1: Register ===
        res = c.post('/api/auth/register', json={
            'name': 'Test Farmer', 'email': 'farmer@test.com', 'password': 'FarmPass123!'
        })
        if res.status_code == 201:
            token = res.json['data']['access_token']
            log('1. Register', 'PASS', '201')
        else:
            log('1. Register', 'FAIL', f'{res.status_code}: {res.text}')
            sys.exit(1)

        headers = {'Authorization': f'Bearer {token}'}

        # === STEP 2: Login ===
        res = c.post('/api/auth/login', json={'email': 'farmer@test.com', 'password': 'FarmPass123!'})
        log('2. Login', 'PASS' if res.status_code == 200 else 'FAIL', res.status_code)

        # === STEP 3: Get Profile ===
        res = c.get('/api/auth/me', headers=headers)
        log('3. Get Profile', 'PASS' if res.status_code == 200 else 'FAIL', res.status_code)

        # === STEP 4: Crop Recommendation ===
        with patch('backend.routes.recommend.CropService.recommend') as mock:
            mock.return_value = ('Rice', 95.3, {'season': 'Kharif', 'water_needs': 'High'})
            res = c.post('/api/recommend/crop', json={
                'nitrogen': 90, 'phosphorus': 42, 'potassium': 43,
                'temperature': 25, 'humidity': 80, 'ph': 6.5, 'rainfall': 200
            }, headers=headers)
            crop_prediction_id = res.json.get('data', {}).get('prediction_id')
            log('4. Crop Recommendation', 'PASS' if res.status_code == 200 else 'FAIL',
                f"{res.status_code} crop={res.json.get('data', {}).get('crop')}")

        # === STEP 5: Disease Detection ===
        with patch('backend.routes.detect.DiseaseService.predict') as mock:
            mock.return_value = {
                'disease_name': 'Apple Scab', 'confidence': 92.5, 'remedy': 'Fungicide',
                'symptoms': 'Dark spots', 'severity': 'Medium', 'affected_crops': ['Apple']
            }
            res = c.post('/api/detect/disease',
                data={'image': (make_jpeg(), 'leaf.jpg')},
                content_type='multipart/form-data', headers=headers)
            log('5. Disease Detection', 'PASS' if res.status_code == 200 else 'FAIL',
                f"{res.status_code} disease={res.json.get('data', {}).get('disease')}")

        # === STEP 6: Yield Prediction ===
        with patch('backend.routes.predict.YieldService.predict_yield') as mock:
            mock.return_value = 3500.0
            res = c.post('/api/predict/yield', json={
                'crop': 'Rice', 'season': 'Kharif', 'region': 'Karnataka',
                'area_ha': 2.5, 'rainfall': 180, 'fertilizer_kg': 120, 'pesticide_kg': 1.5
            }, headers=headers)
            log('6. Yield Prediction', 'PASS' if res.status_code == 200 else 'FAIL',
                f"{res.status_code} yield={res.json.get('data', {}).get('total_yield_kg')}")

        # === STEP 7: Fertilizer Recommendation ===
        with patch('backend.routes.recommend.FertilizerService.recommend') as mock:
            mock.return_value = ('Urea', 88.5, {'quantity_kg_per_acre': '50'})
            res = c.post('/api/recommend/fertilizer', json={
                'nitrogen': 50, 'phosphorus': 50, 'potassium': 50,
                'temperature': 25, 'humidity': 60, 'moisture': 40,
                'soil_type': 'Sandy', 'crop': 'Wheat'
            }, headers=headers)
            log('7. Fertilizer Recommendation', 'PASS' if res.status_code == 200 else 'FAIL',
                f"{res.status_code} fert={res.json.get('data', {}).get('fertilizer')}")

        # === STEP 8: View History ===
        res = c.get('/api/history/?type=all&page=1&per_page=10', headers=headers)
        data = res.json or {}
        history_count = len(data.get('data', {}).get('history', []))
        log('8. View History', 'PASS' if res.status_code == 200 and history_count >= 4 else 'FAIL',
            f"{res.status_code} items={history_count}")

        # === STEP 9: Export CSV ===
        res = c.get('/api/history/export', headers=headers)
        log('9. Export CSV', 'PASS' if res.status_code == 200 else 'FAIL', f"{res.status_code}")

        # === STEP 10: Download PDF Report ===
        if crop_prediction_id:
            res = c.get(f'/api/report/crop_recommendation/{crop_prediction_id}', headers=headers)
            if res.status_code != 200:
                log('10. Download PDF', 'FAIL', f"{res.status_code} body={res.text[:200]}")
            else:
                log('10. Download PDF', 'PASS', f"{res.status_code} content_type={res.content_type}")
        else:
            log('10. Download PDF', 'SKIP', 'No prediction_id available')

        # === STEP 11: Health Check ===
        res = c.get('/api/health')
        log('11. Health Check', 'PASS' if res.status_code == 200 else 'FAIL', f"{res.status_code}")

        # === STEP 12: Logout ===
        res = c.post('/api/auth/logout', headers=headers)
        log('12. Logout', 'PASS' if res.status_code == 200 else 'FAIL', f"{res.status_code}")

        # === STEP 13: Access after logout (should fail) ===
        res = c.get('/api/auth/me', headers=headers)
        log('13. Access After Logout', 'PASS' if res.status_code == 401 else 'FAIL', f"{res.status_code}")

print('\n' + '='*60)
passed = sum(1 for r in results if '[PASS]' in r)
failed = sum(1 for r in results if '[FAIL]' in r)
print(f'RESULTS: {passed} passed, {failed} failed out of {len(results)} steps')
print('='*60)
