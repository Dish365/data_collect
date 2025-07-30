#!/usr/bin/env python3
"""
Script to fix button structure issues in form_builder.kv where properties 
are incorrectly placed inside MDButtonText blocks
"""

import re

def fix_form_builder_buttons():
    """Fix button structure in form_builder.kv"""
    file_path = 'gui/kv/form_builder.kv'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Look for MDButton: pattern
            if 'MDButton:' in line and 'style: "elevated"' in lines[i + 1] if i + 1 < len(lines) else False:
                button_indent = len(line) - len(line.lstrip())
                result_lines.append(line)  # MDButton:
                result_lines.append(lines[i + 1])  # style: "elevated"
                
                i += 2
                
                # Collect all properties and the MDButtonText
                button_properties = []
                button_text = None
                text_value = None
                
                while i < len(lines):
                    current_line = lines[i]
                    current_indent = len(current_line) - len(current_line.lstrip())
                    
                    # If we've moved to a different section, break
                    if current_line.strip() and current_indent <= button_indent:
                        break
                    
                    # Check if this is MDButtonText
                    if 'MDButtonText:' in current_line:
                        button_text = current_line
                        # Get the text value from next line
                        if i + 1 < len(lines) and 'text:' in lines[i + 1]:
                            text_value = lines[i + 1]
                            i += 2  # Skip both MDButtonText: and text: lines
                            continue
                    
                    # Check if this is a button property (not part of MDButtonText)
                    elif any(prop in current_line for prop in ['on_release:', 'size_hint_y:', 'height:', 'md_bg_color:', 'font_size:', 'elevation:']):
                        button_properties.append(current_line)
                    else:
                        # This is some other line, keep it as is
                        result_lines.append(current_line)
                    
                    i += 1
                
                # Now add properties in correct order: button properties first, then MDButtonText
                for prop in button_properties:
                    result_lines.append(prop)
                
                # Add empty line for readability
                result_lines.append(' ' * (button_indent + 4))
                
                # Add MDButtonText block
                if button_text and text_value:
                    result_lines.append(button_text)
                    result_lines.append(text_value)
                
                continue
            
            result_lines.append(line)
            i += 1
        
        # Write the fixed content
        fixed_content = '\n'.join(result_lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ Fixed button structure in {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

if __name__ == '__main__':
    fix_form_builder_buttons() 