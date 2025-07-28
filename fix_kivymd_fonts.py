#!/usr/bin/env python3
"""
KivyMD 2.0.1 Font Style Migration Script

This script automatically updates KV files from KivyMD 1.x font styles 
to KivyMD 2.0.1 font styles and theme properties.

Usage:
    python fix_kivymd_fonts.py

The script will:
1. Find all .kv files in the current directory and subdirectories
2. Update font styles to the new KivyMD 2.0.1 format
3. Update theme property names
4. Update icon property names
5. Create backups of original files (with .backup extension)
"""

import os
import re
import shutil
from pathlib import Path

def create_backup(file_path):
    """Create a backup of the original file"""
    backup_path = f"{file_path}.backup"
    if not os.path.exists(backup_path):
        shutil.copy2(file_path, backup_path)
        print(f"  📋 Created backup: {backup_path}")

def update_font_styles(content):
    """Update font styles to KivyMD 2.0.1 format"""
    
    # Font style replacements with proper indentation
    font_replacements = {
        # Headers -> Display/Headline
        (r'(\s+)font_style:\s*"H1"', r'\1font_style: "Display"\n\1role: "large"'),
        (r'(\s+)font_style:\s*"H2"', r'\1font_style: "Display"\n\1role: "medium"'),
        (r'(\s+)font_style:\s*"H3"', r'\1font_style: "Display"\n\1role: "small"'),
        (r'(\s+)font_style:\s*"H4"', r'\1font_style: "Headline"\n\1role: "large"'),
        (r'(\s+)font_style:\s*"H5"', r'\1font_style: "Headline"\n\1role: "medium"'),
        (r'(\s+)font_style:\s*"H6"', r'\1font_style: "Headline"\n\1role: "small"'),
        
        # Subtitles -> Title
        (r'(\s+)font_style:\s*"Subtitle1"', r'\1font_style: "Title"\n\1role: "large"'),
        (r'(\s+)font_style:\s*"Subtitle2"', r'\1font_style: "Title"\n\1role: "medium"'),
        
        # Body text -> Body
        (r'(\s+)font_style:\s*"Body1"', r'\1font_style: "Body"\n\1role: "large"'),
        (r'(\s+)font_style:\s*"Body2"', r'\1font_style: "Body"\n\1role: "medium"'),
        
        # Small text -> Label
        (r'(\s+)font_style:\s*"Caption"', r'\1font_style: "Label"\n\1role: "small"'),
        (r'(\s+)font_style:\s*"Button"', r'\1font_style: "Label"\n\1role: "large"'),
        (r'(\s+)font_style:\s*"Overline"', r'\1font_style: "Label"\n\1role: "small"'),
    }
    
    for pattern, replacement in font_replacements:
        content = re.sub(pattern, replacement, content)
    
    return content

def update_theme_properties(content):
    """Update theme property names to KivyMD 2.0.1 format"""
    
    theme_replacements = {
        # Color properties
        r'app\.theme_cls\.primary_color': 'app.theme_cls.primaryColor',
        r'app\.theme_cls\.accent_color': 'app.theme_cls.secondaryColor',
        r'app\.theme_cls\.bg_light': 'app.theme_cls.backgroundColor',
        r'app\.theme_cls\.surface': 'app.theme_cls.surfaceColor',
        r'app\.theme_cls\.bg_dark': 'app.theme_cls.surfaceContainerColor',
        r'app\.theme_cls\.bg_normal': 'app.theme_cls.surfaceColor',
        
        # Icon properties
        r'user_font_size:\s*"(\d+)sp"': r'icon_size: "\1dp"',
        r'font_size:\s*dp\((\d+)\)': r'icon_size: "\1dp"',
    }
    
    for pattern, replacement in theme_replacements.items():
        content = re.sub(pattern, replacement, content)
    
    return content

def update_kv_file(file_path):
    """Update a single KV file"""
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Check if file needs updating
        if not any(old_style in original_content for old_style in 
                  ['font_style: "H', 'font_style: "Body', 'font_style: "Caption"', 
                   'font_style: "Subtitle', 'primary_color', 'user_font_size']):
            return False
        
        # Create backup
        create_backup(file_path)
        
        # Apply updates
        updated_content = original_content
        updated_content = update_font_styles(updated_content)
        updated_content = update_theme_properties(updated_content)
        
        # Write updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error updating {file_path}: {e}")
        return False

def find_kv_files(directory="."):
    """Find all KV files in the directory and subdirectories"""
    kv_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.kv'):
                kv_files.append(os.path.join(root, file))
    return kv_files

def main():
    """Main function"""
    print("🚀 KivyMD 2.0.1 Font Style Migration Script")
    print("=" * 50)
    
    # Find all KV files
    kv_files = find_kv_files()
    
    if not kv_files:
        print("❌ No .kv files found in current directory and subdirectories")
        return
    
    print(f"📁 Found {len(kv_files)} KV files:")
    for file in kv_files:
        print(f"   • {file}")
    
    print("\n🔄 Processing files...")
    
    updated_count = 0
    for file_path in kv_files:
        print(f"\n📝 Processing: {file_path}")
        if update_kv_file(file_path):
            updated_count += 1
            print(f"  ✅ Updated successfully")
        else:
            print(f"  ⏭️  No changes needed")
    
    print(f"\n🎉 Migration complete!")
    print(f"   • {updated_count} files updated")
    print(f"   • {len(kv_files) - updated_count} files unchanged")
    
    if updated_count > 0:
        print(f"\n💡 Next steps:")
        print(f"   1. Test your application: python main.py")
        print(f"   2. Check for any remaining issues")
        print(f"   3. If everything works, you can delete .backup files")
        print(f"   4. If issues occur, restore from .backup files")

if __name__ == "__main__":
    main() 