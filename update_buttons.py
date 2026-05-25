import os
import glob

frontend_dir = r'C:\Users\Gagan M\.gemini\antigravity\scratch\ai-smart-agriculture\frontend'

for html_file in glob.glob(os.path.join(frontend_dir, '*.html')):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'onclick="window.print()"' in content:
        content = content.replace('onclick="window.print()"', 'id="btn-download-report"')
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
print("Updated HTML buttons")
