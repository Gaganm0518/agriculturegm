from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
import random
from datetime import datetime, timedelta

market_bp = Blueprint('market', __name__)

# Crops to support
SUPPORTED_CROPS = ["Rice", "Wheat", "Maize", "Cotton", "Sugarcane"]

# Realistic Mock MSP Data (₹ per quintal, approx for 2024)
MSP_DATA = {
    "Rice": 2183,
    "Wheat": 2275,
    "Maize": 2090,
    "Cotton": 6620,
    "Sugarcane": 315 # per quintal
}

@market_bp.route('/prices', methods=['GET'])
@jwt_required()
def get_live_prices():
    """Fetch live mandi prices (Mocked)"""
    prices = []
    for crop in SUPPORTED_CROPS:
        msp = MSP_DATA[crop]
        # Generate a realistic mandi price varying slightly around the MSP
        variation = random.uniform(-0.1, 0.15) # -10% to +15%
        mandi_price = int(msp * (1 + variation))
        
        prices.append({
            "crop": crop,
            "mandi_price": mandi_price,
            "msp": msp,
            "difference": mandi_price - msp,
            "status": "Below MSP" if mandi_price < msp else "Above MSP"
        })
        
    return jsonify({
        "success": True,
        "data": prices
    }), 200

@market_bp.route('/msp', methods=['GET'])
@jwt_required()
def get_msp():
    """Fetch current MSP rates"""
    return jsonify({
        "success": True,
        "data": MSP_DATA
    }), 200

@market_bp.route('/predict/<crop_name>', methods=['GET'])
@jwt_required()
def predict_price(crop_name):
    """Predict best selling window for a crop"""
    # Normalize crop name
    crop_name = crop_name.capitalize()
    
    if crop_name not in SUPPORTED_CROPS:
        return jsonify({
            "success": False,
            "error": "Crop not supported for price prediction."
        }), 400
        
    base_price = MSP_DATA[crop_name]
    
    # Generate 6-month mock trend
    trend = []
    current_date = datetime.now()
    
    highest_price = 0
    best_month = ""
    
    for i in range(6):
        month_date = current_date + timedelta(days=30 * i)
        month_name = month_date.strftime("%B %Y")
        
        # Simulate price trend with some seasonality
        seasonal_factor = 1 + (random.uniform(-0.05, 0.15) if i > 2 else random.uniform(-0.1, 0.05))
        predicted_price = int(base_price * seasonal_factor)
        
        trend.append({
            "month": month_name,
            "price": predicted_price
        })
        
        if predicted_price > highest_price:
            highest_price = predicted_price
            best_month = month_name
            
    return jsonify({
        "success": True,
        "data": {
            "crop": crop_name,
            "trend": trend,
            "best_time_to_sell": best_month,
            "expected_high": highest_price,
            "advice": f"Hold your {crop_name} stock until {best_month} to maximize profits at an estimated ₹{highest_price}/qtl."
        }
    }), 200
