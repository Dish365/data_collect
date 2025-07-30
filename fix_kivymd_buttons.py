#!/usr/bin/env python3
"""
Script to fix KivyMD 1.x button classes to KivyMD 2.0 compatible button syntax
"""

import os
import re
from pathlib import Path

# Button class mappings from KivyMD 1.x to 2.0
BUTTON_MAPPINGS = {
    'MDRaisedButton': {
        'new_class': 'MDButton',
        'style': 'elevated',
        'needs_text_wrapper': True
    },
    'MDFlatButton': {
        'new_class': 'MDButton', 
        'style': 'text',
        'needs_text_wrapper': True
    },
    'MDRoundFlatButton': {
        'new_class': 'MDButton',
        'style': 'outlined', 
        'needs_text_wrapper': True
    },
    'MDFillRoundFlatButton': {
        'new_class': 'MDButton',
        'style': 'filled',
        'needs_text_wrapper': True
    },
    'MDRoundFlatIconButton': {
        'new_class': 'MDButton',
        'style': 'outlined',
        'needs_icon_wrapper': True,
        'needs_text_wrapper': True
    },
    'MDFillRoundFlatIconButton': {
        'new_class': 'MDButton', 
        'style': 'filled',
        'needs_icon_wrapper': True,
        'needs_text_wrapper': True
    }
}

def fix_button_imports(content):
    """Remove old button import statements"""
    # Remove import lines for old button classes
    import_patterns = [
        r'#:import\s+MDRaisedButton\s+.*\n',
        r'#:import\s+MDFlatButton\s+.*\n',
        r'#:import\s+MDRoundFlatButton\s+.*\n',
        r'#:import\s+MDFillRoundFlatButton\s+.*\n',
        r'#:import\s+MDRoundFlatIconButton\s+.*\n',
        r'#:import\s+MDFillRoundFlatIconButton\s+.*\n'
    ]
    
    for pattern in import_patterns:
        content = re.sub(pattern, '', content)
    
    return content

def fix_button_class_definitions(content):
    """Fix class definitions that inherit from old button classes"""
    for old_class, mapping in BUTTON_MAPPINGS.items():
        # Pattern to match class definitions like <MyButton@MDRaisedButton>:
        pattern = rf'(<[^@>]+@){old_class}(>:)'
        replacement = rf'\1{mapping["new_class"]}\2'
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_button_instances(content):
    """Fix direct button instances in KV files"""
    lines = content.split('\n')
    result_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line contains an old button class
        old_button_found = None
        for old_class in BUTTON_MAPPINGS.keys():
            if f'{old_class}:' in line:
                old_button_found = old_class
                break
        
        if old_button_found:
            mapping = BUTTON_MAPPINGS[old_button_found]
            indent = len(line) - len(line.lstrip())
            
            # Replace the button class and add style
            new_line = line.replace(f'{old_button_found}:', f'{mapping["new_class"]}:')
            result_lines.append(new_line)
            result_lines.append(' ' * (indent + 4) + f'style: "{mapping["style"]}"')
            
            # Look ahead to find text property and wrap it
            j = i + 1
            text_found = False
            icon_found = False
            
            while j < len(lines):
                next_line = lines[j]
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # If we've moved to a different indentation level, stop
                if next_line.strip() and next_indent <= indent:
                    break
                
                # Check for text property
                if 'text:' in next_line and not text_found:
                    if mapping.get('needs_text_wrapper'):
                        # Extract the text value
                        text_match = re.search(r'text:\s*(.+)', next_line)
                        if text_match:
                            text_value = text_match.group(1)
                            # Skip the original text line
                            j += 1
                            # Add MDButtonText wrapper
                            result_lines.append(' ' * (indent + 4) + 'MDButtonText:')
                            result_lines.append(' ' * (indent + 8) + f'text: {text_value}')
                            text_found = True
                            continue
                
                # Check for icon property  
                if 'icon:' in next_line and not icon_found:
                    if mapping.get('needs_icon_wrapper'):
                        # Extract the icon value
                        icon_match = re.search(r'icon:\s*(.+)', next_line)
                        if icon_match:
                            icon_value = icon_match.group(1)
                            # Skip the original icon line
                            j += 1
                            # Add MDButtonIcon wrapper
                            result_lines.append(' ' * (indent + 4) + 'MDButtonIcon:')
                            result_lines.append(' ' * (indent + 8) + f'icon: {icon_value}')
                            icon_found = True
                            continue
                
                # Copy other properties as-is
                result_lines.append(next_line)
                j += 1
            
            i = j
        else:
            result_lines.append(line)
            i += 1
    
    return '\n'.join(result_lines)

def fix_kv_file(file_path):
    """Fix a single KV file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes
        content = fix_button_imports(content)
        content = fix_button_class_definitions(content)
        content = fix_button_instances(content)
        
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
        print("\n✅ No changes needed - all files are already compatible!")

if __name__ == '__main__':
    main() 