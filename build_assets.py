import os
import re

def minify_css(css):
    css = re.sub(r'/\*[\s\S]*?\*/', '', css)
    css = re.sub(r'\s+', ' ', css)
    css = css.replace(' {', '{').replace('{ ', '{')
    css = css.replace(' }', '}').replace('} ', '}')
    css = css.replace(' :', ':').replace(': ', ':')
    css = css.replace(' ;', ';').replace('; ', ';')
    css = css.replace(' ,', ',').replace(', ', ',')
    return css.strip()

def minify_js(js):
    # Safe JS bundling: just remove comments, don't strip newlines which breaks ASI
    js = re.sub(r'/\*[\s\S]*?\*/', '', js)
    return js.strip()

base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, 'static')
css_dir = os.path.join(static_dir, 'css')
js_dir = os.path.join(static_dir, 'js')

# CSS Bundle
css_files = ['style.css', 'weather.css']
bundled_css = ""
for f in css_files:
    path = os.path.join(css_dir, f)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            bundled_css += file.read() + "\n"

with open(os.path.join(css_dir, 'bundle.min.css'), 'w', encoding='utf-8') as file:
    file.write(minify_css(bundled_css))
print("Created bundle.min.css")

# JS Bundle
# Order matters
js_files = [
    'i18n.js', 'api.js', 'layout.js', 'auth.js', 'notifications.js',
    'dashboard.js', 'input-form.js', 'crop-result.js', 'disease-detect.js', 
    'fertilizer-recommend.js', 'yield-prediction.js', 'weather.js', 'market.js',
    'history.js', 'admin-dashboard.js', 'admin-datasets.js'
]
bundled_js = ""
for f in js_files:
    path = os.path.join(js_dir, f)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            bundled_js += f"\n{content}\n"

with open(os.path.join(js_dir, 'bundle.min.js'), 'w', encoding='utf-8') as file:
    file.write(minify_js(bundled_js))
print("Created bundle.min.js")
