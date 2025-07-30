#!/usr/bin/env python3
"""
Script to fix KivyMD 1.x theme attributes to KivyMD 2.0 compatible attributes
"""

import os
import re
from pathlib import Path

# Theme attribute mappings from KivyMD 1.x to 2.0
THEME_MAPPINGS = {
    # Main color properties that changed
    'primary': 'primaryColor',
    'accent': 'secondaryColor',
    'primary_color': 'primaryColor',
    'accent_color': 'secondaryColor',
    'primary_light': 'primaryContainerColor',
    'primary_dark': 'onPrimaryColor',
    'accent_light': 'secondaryContainerColor',
    'accent_dark': 'onSecondaryColor',
    
    # Background colors
    'bg_light': 'backgroundColor',
    'bg_normal': 'surfaceColor',
    'bg_dark': 'surfaceVariantColor',
    'bg_darkest': 'surfaceContainerColor',
    
    # Text colors
    'text_color': 'onSurfaceColor',
    'secondary_text_color': 'onSurfaceVariantColor',
    'opposite_text_color': 'onBackgroundColor',
    
    # Icon colors
    'icon_color': 'onSurfaceColor',
    'opposite_icon_color': 'onBackgroundColor',
    
    # Other colors - CRITICAL FIX
    'error': 'errorColor',  # This is the main issue from the error log
    'divider_color': 'outlineColor',
    'disabled_hint_text_color': 'disabledTextColor',
    'error_color': 'errorColor',
    'ripple_color': 'rippleColor',
    
    # Surface colors - UPDATED WITH CORRECT NAMES
    'surface': 'surfaceColor',
    'surface_variant': 'surfaceVariantColor',
    'surface_container': 'surfaceContainerColor',
    'surface_container_high': 'surfaceContainerHighColor',
    'surface_container_low': 'surfaceContainerLowColor',
    'surface_container_highest': 'surfaceContainerHighestColor',
    'surface_container_lowest': 'surfaceContainerLowestColor',
    'surface_bright': 'surfaceBrightColor',
    'surface_dim': 'surfaceDimColor',
    'surface_tint': 'surfaceTintColor',
    'outline': 'outlineColor',
    'outline_variant': 'outlineVariantColor',
    
    # CRITICAL FIXES - Missing properties from error logs
    'surfaceContainerHigh': 'surfaceContainerHighColor',
    'surfaceContainerLow': 'surfaceContainerLowColor',
    'surfaceContainerHighest': 'surfaceContainerHighestColor',
    'surfaceContainerLowest': 'surfaceContainerLowestColor',
    'surfaceVariant': 'surfaceVariantColor',
    'surfaceContainer': 'surfaceContainerColor',  # This was missing!
    'onPrimary': 'onPrimaryColor',  # New missing property!
    
    # On colors
    'on_primary': 'onPrimaryColor',
    'on_secondary': 'onSecondaryColor',
    'on_surface': 'onSurfaceColor',
    'on_background': 'onBackgroundColor',
    'on_error': 'onErrorColor',
    'on_surface_variant': 'onSurfaceVariantColor',
    
    # Container colors
    'primary_container': 'primaryContainerColor',
    'secondary_container': 'secondaryContainerColor',
    'error_container': 'errorContainerColor',
    'on_primary_container': 'onPrimaryContainerColor',
    'on_secondary_container': 'onSecondaryContainerColor',
    'on_error_container': 'onErrorContainerColor',
    
    # Additional mappings that might be needed
    'warning': 'errorColor',  # KivyMD 2.0 doesn't have warning, map to error
    'tertiary': 'tertiaryColor',
    'on_tertiary': 'onTertiaryColor',
    'tertiary_container': 'tertiaryContainerColor',
    'on_tertiary_container': 'onTertiaryContainerColor',
    
    # Fixed colors
    'primary_fixed': 'primaryFixedColor',
    'primary_fixed_dim': 'primaryFixedDimColor',
    'secondary_fixed': 'secondaryFixedColor',
    'secondary_fixed_dim': 'secondaryFixedDimColor',
    'tertiary_fixed': 'tertiaryFixedColor',
    'tertiary_fixed_dim': 'tertiaryFixedDimColor',
    'on_primary_fixed': 'onPrimaryFixedColor',
    'on_primary_fixed_variant': 'onPrimaryFixedVariantColor',
    'on_secondary_fixed': 'onSecondaryFixedColor',
    'on_secondary_fixed_variant': 'onSecondaryFixedVariantColor',
    'on_tertiary_fixed': 'onTertiaryFixedColor',
    'on_tertiary_fixed_variant': 'onTertiaryFixedVariantColor',
    
    # Shadow and other properties
    'shadow_color': 'shadowColor',
    'scrim_color': 'scrimColor',
    'inverse_primary': 'inversePrimaryColor',
    'inverse_surface': 'inverseSurfaceColor',
    'inverse_on_surface': 'inverseOnSurfaceColor',
}

def fix_kv_file(file_path):
    """Fix theme attributes in a single KV file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # Apply all theme mappings
        for old_attr, new_attr in THEME_MAPPINGS.items():
            # Replace app.theme_cls.old_attr with app.theme_cls.new_attr
            pattern = rf'app\.theme_cls\.{old_attr}\b'
            replacement = f'app.theme_cls.{new_attr}'
            
            # Count matches before replacement
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                changes_made.append(f"{old_attr} -> {new_attr} ({len(matches)} occurrences)")
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            for change in changes_made:
                print(f"  - {change}")
            return True
        else:
            print(f"No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix all KV files"""
    # Get the gui/kv directory
    kv_dir = Path("gui/kv")
    
    if not kv_dir.exists():
        print("Error: gui/kv directory not found!")
        return
    
    # Find all .kv files
    kv_files = list(kv_dir.glob("*.kv"))
    
    if not kv_files:
        print("No .kv files found in gui/kv directory!")
        return
    
    print(f"Found {len(kv_files)} KV files to process...")
    print("=" * 50)
    
    fixed_count = 0
    for kv_file in kv_files:
        if fix_kv_file(kv_file):
            fixed_count += 1
        print("-" * 30)
    
    print(f"\nProcessing complete! Fixed {fixed_count} out of {len(kv_files)} files.")
    print("\nNote: After running this script, you may need to:")
    print("1. Update your main.py to ensure proper theme initialization")
    print("2. Test the application to verify all colors display correctly")
    print("3. Adjust any custom color values if needed")

if __name__ == "__main__":
    main() 