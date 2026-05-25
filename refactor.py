import os
import glob
import re

frontend_dir = r'C:\Users\Gagan M\.gemini\antigravity\scratch\ai-smart-agriculture\frontend'

for html_file in glob.glob(os.path.join(frontend_dir, '*.html')):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Only modify files that have dashboard-layout
    if 'dashboard-layout' in content:
        # Remove sidebar
        content = re.sub(r'<aside class="sidebar".*?</aside>', '', content, flags=re.DOTALL)
        
        # Remove topnav
        content = re.sub(r'<header class="topnav".*?</header>', '', content, flags=re.DOTALL)
        
        # Inject layout.js if not present
        if '/static/js/layout.js' not in content:
            content = content.replace('</body>', '    <script src="/static/js/layout.js"></script>\n</body>')
            
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
print('Layouts refactored.')
