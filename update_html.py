import os
import re

base_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(base_dir, 'frontend')

for file in os.listdir(frontend_dir):
    if file.endswith('.html'):
        path = os.path.join(frontend_dir, file)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add preconnect
        if '<head>' in content and 'api.openweathermap.org' not in content:
            content = content.replace('<head>', '<head>\n    <link rel="preconnect" href="https://api.openweathermap.org">\n    <link rel="preconnect" href="https://openweathermap.org">')

        # Replace CSS
        content = re.sub(r'<link rel="stylesheet" href="/static/css/style\.css">', '<link rel="stylesheet" href="/static/css/bundle.min.css">', content)
        content = re.sub(r'<link rel="stylesheet" href="/static/css/weather\.css">[\r\n]*', '', content)

        # Replace JS
        if '<script src="/static/js/' in content:
            content = re.sub(r'<script src="/static/js/.*?\"></script>[\r\n]*', '', content)
            content = content.replace('</body>', '    <script src="/static/js/bundle.min.js"></script>\n</body>')

        # Lazy load images
        content = re.sub(r'<img(?![^>]*loading=)([^>]*)>', r'<img loading="lazy"\1>', content)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
            
print('Updated HTML files')
