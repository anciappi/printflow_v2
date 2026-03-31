import os
import re

def fix_html_tags_multiline(content):
    fixed_content = ""
    in_tag = False
    in_string = False
    string_char = ''
    tag_fixes = 0
    
    i = 0
    while i < len(content):
        char = content[i]
        
        # We need to skip <!-- --> and <script> / <style> blocks if possible, but basic tag parsing:
        
        if not in_tag:
            # Check if entering an HTML tag (like <div, <span, <a, </div, etc.)
            # Exclude <!-- ... -->
            if char == '<' and i + 1 < len(content) and (content[i+1].isalpha() or content[i+1] == '/'):
                in_tag = True
            
            fixed_content += char
        else:
            # We are inside a tag
            if not in_string:
                if char == '"' or char == "'":
                    in_string = True
                    string_char = char
                    fixed_content += char
                elif char == '>':
                    in_tag = False
                    fixed_content += char
                elif char == '\n':
                    # Replace newline with a space
                    fixed_content += ' '
                    tag_fixes += 1
                    
                    # Eat up leading spaces on the next line
                    j = i + 1
                    while j < len(content) and content[j] in [' ', '\t']:
                        j += 1
                    i = j - 1
                else:
                    fixed_content += char
            else:
                # Inside string
                if char == string_char:
                    # Check for escaping? Typically HTML attributes don't use \", but let's just close string
                    in_string = False
                fixed_content += char
                
        i += 1
    return fixed_content, tag_fixes

def main():
    directory = r'\\wsl.localhost\Ubuntu\home\anciappi\projects\antigravity\printflow_v2\templates'
    
    count_files_fixed = 0
    total_tags_fixed = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # We might skip <script> and <style> manually, but the parser just sees them as normal tags
                    # The content of <script> starts after <script> and ends at </script>.
                    # Our parser just formats the `<script ... \n ...>` tag itself, which is fine!
                    
                    fixed_content, tag_fixes = fix_html_tags_multiline(content)
                        
                    if tag_fixes > 0 and content != fixed_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(fixed_content)
                        count_files_fixed += 1
                        total_tags_fixed += tag_fixes
                        print(f"Fixed {tag_fixes} tags in {file}")
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    
    print(f"Done. Fixed {total_tags_fixed} tags across {count_files_fixed} files.")

if __name__ == '__main__':
    main()
