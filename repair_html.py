import os
import glob
import re

frontend_dir = r'C:\Users\Gagan M\.gemini\antigravity\scratch\ai-smart-agriculture\frontend'

def fix_html(content):
    # Fix the broken </i> tags
    # Example: </i data-i18n="nav.dashboard"> Dashboard -> </i><span data-i18n="nav.dashboard"> Dashboard</span>
    
    # Use regex to find broken closing tags
    pattern = r'</(i|button|h\d|span|div) data-i18n="([^"]+)">([^<]+)'
    
    def replacer(match):
        tag = match.group(1)
        key = match.group(2)
        text = match.group(3)
        # We wrap the text in a span if it wasn't already wrapped, or just add data-i18n to the existing tag if it was an opening tag.
        # But wait, it was a closing tag: `</i...`
        # So we should restore the closing tag `</i>` and wrap the text in a span.
        return f'</{tag}><span data-i18n="{key}">{text.rstrip()}</span>\n'

    content = re.sub(pattern, replacer, content)
    
    # Also fix some other broken things if any
    
    return content

for html_file in glob.glob(os.path.join(frontend_dir, '*.html')):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    fixed_content = fix_html(content)
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

print("HTML repaired")
