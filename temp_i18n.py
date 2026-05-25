import os
import glob

frontend_dir = r'C:\Users\Gagan M\.gemini\antigravity\scratch\ai-smart-agriculture\frontend'

replacements = {
    '> Dashboard': ' data-i18n="nav.dashboard"> Dashboard',
    '> New Analysis': ' data-i18n="nav.new_analysis"> New Analysis',
    '> Crop Recommendation': ' data-i18n="dash.card.crop"> Crop Recommendation',
    '> Disease Detection': ' data-i18n="nav.disease_detection"> Disease Detection',
    '> Yield Prediction': ' data-i18n="nav.yield_prediction"> Yield Prediction',
    '> Fertilizer Recs': ' data-i18n="nav.fertilizer_recs"> Fertilizer Recs',
    '> Weather Info': ' data-i18n="nav.weather"> Weather Info',
    '> My History': ' data-i18n="nav.history"> My History',
    '> Settings': ' data-i18n="nav.settings"> Settings',
    '> Admin Panel': ' data-i18n="nav.admin_panel"> Admin Panel',
    '> Logout': ' data-i18n="nav.logout"> Logout',
    
    'Welcome back': '<span data-i18n="dash.welcome">Welcome back</span>',
    "Here is an overview of your farm's AI insights today.": '<span data-i18n="dash.overview">Here is an overview of your farm\'s AI insights today.</span>',
    'Discover the best crop for your soil and weather.': '<span data-i18n="dash.card.crop_desc">Discover the best crop for your soil and weather.</span>',
    'Scan a leaf image to instantly detect plant diseases.': '<span data-i18n="dash.card.disease_desc">Scan a leaf image to instantly detect plant diseases.</span>',
    'Forecast your crop harvest output based on inputs.': '<span data-i18n="dash.card.yield_desc">Forecast your crop harvest output based on inputs.</span>',
    'Get exact nutrient dosages to optimize soil health.': '<span data-i18n="dash.card.fertilizer_desc">Get exact nutrient dosages to optimize soil health.</span>',
    'View past predictions and analysis reports.': '<span data-i18n="dash.card.history_desc">View past predictions and analysis reports.</span>',
    'Try Now': '<span data-i18n="dash.btn.try">Try Now</span>',
    'View': '<span data-i18n="dash.btn.view">View</span>',
    
    'Soil & Environment Data Entry': '<span data-i18n="form.title">Soil & Environment Data Entry</span>',
    'Enter the precise readings from your farm to receive an accurate crop recommendation.': '<span data-i18n="form.subtitle">Enter the precise readings from your farm to receive an accurate crop recommendation.</span>',
    'Analyze with AI': '<span data-i18n="form.btn.analyze">Analyze with AI</span>',
    
    'Diagnose Plant Diseases with AI': '<span data-i18n="dis.title">Diagnose Plant Diseases with AI</span>',
    'Upload a clear photo of a plant leaf to instantly identify diseases and receive expert treatment plans.': '<span data-i18n="dis.subtitle">Upload a clear photo of a plant leaf to instantly identify diseases and receive expert treatment plans.</span>',
    'Drag and drop a leaf image here': '<span data-i18n="dis.drag">Drag and drop a leaf image here</span>',
    'or click to browse from your device': '<span data-i18n="dis.browse">or click to browse from your device</span>',
    'Supported formats: JPG, PNG (Max 5MB)': '<span data-i18n="dis.formats">Supported formats: JPG, PNG (Max 5MB)</span>',
    'Remove Image': '<span data-i18n="dis.btn.remove">Remove Image</span>',
    'Detect Disease': '<span data-i18n="dis.btn.detect">Detect Disease</span>',
    
    'Crop Yield Forecaster': '<span data-i18n="yld.title">Crop Yield Forecaster</span>',
    'Estimate your harvest output based on farm area, weather, and inputs.': '<span data-i18n="yld.subtitle">Estimate your harvest output based on farm area, weather, and inputs.</span>',
    'Predict Yield': '<span data-i18n="yld.btn.predict">Predict Yield</span>',
    
    'Smart Fertilizer Calculator': '<span data-i18n="fert.title">Smart Fertilizer Calculator</span>',
    'Determine the precise fertilizer type and dosage based on your soil deficiency.': '<span data-i18n="fert.subtitle">Determine the precise fertilizer type and dosage based on your soil deficiency.</span>',
    'Calculate Fertilizer': '<span data-i18n="fert.btn.calculate">Calculate Fertilizer</span>',
    
    'Prediction History': '<span data-i18n="hist.title">Prediction History</span>',
    'Your past AI analyses and reports.': '<span data-i18n="hist.subtitle">Your past AI analyses and reports.</span>',
    'Export CSV': '<span data-i18n="hist.btn.export">Export CSV</span>',
}

# Fix duplicate additions of data-i18n
for html_file in glob.glob(os.path.join(frontend_dir, '*.html')):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    for old, new in replacements.items():
        if new not in content:
            content = content.replace(old, new)
            
    # Add i18n.js
    if '/static/js/i18n.js' not in content:
        content = content.replace('</body>', '    <script src="/static/js/i18n.js"></script>\n</body>')
        
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
        
print('Updated HTML files.')
