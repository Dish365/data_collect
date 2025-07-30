#!/usr/bin/env python3
"""
Script to fix KivyMD 1.x font styles to KivyMD 2.0 compatible font styles
"""

import os
import re
from pathlib import Path

# Font style mappings from KivyMD 1.x to 2.0
FONT_STYLE_MAPPINGS = {
    # Old H1-H6 styles to new styles
    'H1': {'font_style': 'Display', 'role': 'large'},
    'H2': {'font_style': 'Display', 'role': 'medium'}, 
    'H3': {'font_style': 'Display', 'role': 'small'},
    'H4': {'font_style': 'Headline', 'role': 'large'},
    'H5': {'font_style': 'Headline', 'role': 'medium'},
    'H6': {'font_style': 'Headline', 'role': 'small'},
    
    # Old subtitle styles
    'Subtitle1': {'font_style': 'Title', 'role': 'large'},
    'Subtitle2': {'font_style': 'Title', 'role': 'medium'},
    
    # Old body styles  
    'Body1': {'font_style': 'Body', 'role': 'large'},
    'Body2': {'font_style': 'Body', 'role': 'medium'},
    
    # Other old styles
    'Button': {'font_style': 'Label', 'role': 'large'},
    'Caption': {'font_style': 'Label', 'role': 'small'},
    'Overline': {'font_style': 'Label', 'role': 'small'},
}

def fix_font_styles(content):
    """Fix font styles in KV content"""
    lines = content.split('\n')
    result_lines = []
    
    for i, line in enumerate(lines):
        # Check if line contains font_style
        if 'font_style:' in line:
            # Extract the font style value
            match = re.search(r'font_style:\s*["\']([^"\']+)["\']', line)
            if match:
                old_style = match.group(1)
                if old_style in FONT_STYLE_MAPPINGS:
                    mapping = FONT_STYLE_MAPPINGS[old_style]
                    
                    # Get the indentation
                    indent = len(line) - len(line.lstrip())
                    
                    # Replace the font_style line
                    new_line = line.replace(f'"{old_style}"', f'"{mapping["font_style"]}"')
                    new_line = new_line.replace(f"'{old_style}'", f'"{mapping["font_style"]}"')
                    result_lines.append(new_line)
                    
                    # Check if the next lines already have a role property
                    has_role = False
                    j = i + 1
                    while j < len(lines) and lines[j].strip():
                        next_line = lines[j]
                        next_indent = len(next_line) - len(next_line.lstrip())
                        
                        # If we've moved to a different indentation level, stop
                        if next_line.strip() and next_indent <= indent:
                            break
                            
                        if 'role:' in next_line:
                            has_role = True
                            break
                            
                        j += 1
                    
                    # Add role if it doesn't exist
                    if not has_role:
                        result_lines.append(' ' * indent + f'role: "{mapping["role"]}"')
                    
                    continue
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)

def fix_kv_file(file_path):
    """Fix a single KV file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply font style fixes
        content = fix_font_styles(content)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix all KV files"""
    gui_dir = Path('gui')
    if not gui_dir.exists():
        gui_dir = Path('.')
    
    kv_files = list(gui_dir.rglob('*.kv'))
    
    if not kv_files:
        print("No KV files found!")
        return
    
    print(f"Found {len(kv_files)} KV files to check...")
    
    fixed_files = []
    
    for kv_file in kv_files:
        if fix_kv_file(kv_file):
            fixed_files.append(str(kv_file))
    
    if fixed_files:
        print(f"\n✅ Fixed {len(fixed_files)} files:")
        for file in fixed_files:
            print(f"  - {file}")
    else:
        print("\n✅ No changes needed - all font styles are already compatible!")

if __name__ == '__main__':
    main() 