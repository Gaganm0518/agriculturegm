-- AI Smart Agriculture Database Schema
-- Run this file to set up the initial tables and seed data

CREATE DATABASE IF NOT EXISTS agri_db;
USE agri_db;

-- 1. users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'farmer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_email (email)
);

-- 1b. token_blocklist
CREATE TABLE IF NOT EXISTS token_blocklist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jti VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_token_jti (jti)
);

-- 2. soil_weather_inputs
CREATE TABLE IF NOT EXISTS soil_weather_inputs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    soil_type VARCHAR(50),
    temperature FLOAT,
    humidity FLOAT,
    rainfall FLOAT,
    nitrogen FLOAT NOT NULL,
    phosphorus FLOAT NOT NULL,
    potassium FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_soil_user_id (user_id)
);

-- 3. crop_recommendations
CREATE TABLE IF NOT EXISTS crop_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    input_id INT NOT NULL,
    recommended_crop VARCHAR(100) NOT NULL,
    confidence_score FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (input_id) REFERENCES soil_weather_inputs(id) ON DELETE CASCADE,
    INDEX idx_crop_input_id (input_id)
);

-- 4. disease_detections
CREATE TABLE IF NOT EXISTS disease_detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    image_path VARCHAR(500) NOT NULL,
    disease_name VARCHAR(200) NOT NULL,
    remedy TEXT,
    confidence FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_disease_user_id (user_id)
);

-- 5. yield_predictions
CREATE TABLE IF NOT EXISTS yield_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    input_id INT NOT NULL,
    crop_name VARCHAR(100) NOT NULL,
    predicted_yield_kg FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (input_id) REFERENCES soil_weather_inputs(id) ON DELETE CASCADE,
    INDEX idx_yield_input_id (input_id)
);

-- 6. fertilizer_recommendations
CREATE TABLE IF NOT EXISTS fertilizer_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    input_id INT NOT NULL,
    fertilizer_name VARCHAR(150) NOT NULL,
    quantity_kg FLOAT,
    reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (input_id) REFERENCES soil_weather_inputs(id) ON DELETE CASCADE,
    INDEX idx_fert_input_id (input_id)
);

-- 7. admin_logs
CREATE TABLE IF NOT EXISTS admin_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL,
    action VARCHAR(255) NOT NULL,
    target_table VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_admin_logs_admin_id (admin_id)
);

-- Additional Seed Table for 10 common fertilizers
CREATE TABLE IF NOT EXISTS fertilizer_data_lookup (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    n_content FLOAT,
    p_content FLOAT,
    k_content FLOAT
);

-- Seed Data: 10 common fertilizers
INSERT IGNORE INTO fertilizer_data_lookup (name, description, n_content, p_content, k_content) VALUES
('Urea', 'High nitrogen fertilizer, good for leaf growth.', 46, 0, 0),
('DAP (Diammonium Phosphate)', 'High in phosphorus, good for root development.', 18, 46, 0),
('MOP (Muriate of Potash)', 'High potassium, improves disease resistance.', 0, 0, 60),
('NPK 19-19-19', 'Balanced fertilizer for overall plant growth.', 19, 19, 19),
('SSP (Single Super Phosphate)', 'Provides phosphorus, sulfur, and calcium.', 0, 16, 0),
('Ammonium Sulphate', 'Provides nitrogen and sulfur, good for alkaline soils.', 21, 0, 0),
('CAN (Calcium Ammonium Nitrate)', 'Neutral fertilizer, provides nitrogen and calcium.', 27, 0, 0),
('Potassium Nitrate', 'Provides potassium and nitrogen, good for fruits and vegetables.', 13, 0, 45),
('Compost', 'Organic matter, improves soil structure and slowly releases nutrients.', 1, 1, 1),
('Vermicompost', 'Nutrient-rich organic fertilizer produced by earthworms.', 1.5, 1.0, 1.0);
