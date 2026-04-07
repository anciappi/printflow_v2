import os
import re

# Directorio de templates
templates_dir = r"\\wsl.localhost\Ubuntu\home\anciappi\projects\antigravity\printflow_v2\templates"
static_css_dir = r"\\wsl.localhost\Ubuntu\home\anciappi\projects\antigravity\printflow_v2\static\css"

# Patrones de reemplazo
replacements = [
    (r'\bfont-mono\b', ''),
    (r'\bfont-bold\b', 'font-normal'),
    (r'\bfont-semibold\b', 'font-normal'),
    (r'\bfont-extrabold\b', 'font-normal'),
    (r'\bfont-black\b', 'font-normal'),
    (r'\bfont-medium\b', 'font-light'),
]

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for pattern, repl in replacements:
        new_content = re.sub(pattern, repl, new_content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated: {filepath}")

def walk_and_process(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html') or file.endswith('.css'):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    walk_and_process(templates_dir)
    walk_and_process(static_css_dir)
