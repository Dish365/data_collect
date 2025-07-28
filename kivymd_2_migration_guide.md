# KivyMD 2.0.1 Migration Guide

This guide helps you migrate from KivyMD 1.x to KivyMD 2.0.1, focusing on the major breaking changes.

## Font Style Migration

### Old vs New Font Styles

| Old (KivyMD 1.x) | New (KivyMD 2.0.1) | Usage |
|------------------|---------------------|--------|
| `"H1"` | `font_style: "Display"` + `role: "large"` | Large headlines |
| `"H2"` | `font_style: "Display"` + `role: "medium"` | Medium headlines |
| `"H3"` | `font_style: "Display"` + `role: "small"` | Small headlines |
| `"H4"` | `font_style: "Headline"` + `role: "large"` | Large titles |
| `"H5"` | `font_style: "Headline"` + `role: "medium"` | Medium titles |
| `"H6"` | `font_style: "Headline"` + `role: "small"` | Small titles |
| `"Subtitle1"` | `font_style: "Title"` + `role: "large"` | Large subtitles |
| `"Subtitle2"` | `font_style: "Title"` + `role: "medium"` | Medium subtitles |
| `"Body1"` | `font_style: "Body"` + `role: "large"` | Large body text |
| `"Body2"` | `font_style: "Body"` + `role: "medium"` | Medium body text |
| `"Caption"` | `font_style: "Label"` + `role: "small"` | Small labels/captions |
| `"Button"` | `font_style: "Label"` + `role: "large"` | Button text |
| `"Overline"` | `font_style: "Label"` + `role: "small"` | Overline text |

### Example Migration

**Old (KivyMD 1.x):**
```kv
MDLabel:
    text: "Title"
    font_style: "H6"
    theme_text_color: "Primary"
```

**New (KivyMD 2.0.1):**
```kv
MDLabel:
    text: "Title"
    font_style: "Headline"
    role: "small"
    theme_text_color: "Primary"
```

## Theme Property Migration

### Color Properties

| Old (KivyMD 1.x) | New (KivyMD 2.0.1) |
|------------------|---------------------|
| `app.theme_cls.primary_color` | `app.theme_cls.primaryColor` |
| `app.theme_cls.accent_color` | `app.theme_cls.secondaryColor` |
| `app.theme_cls.bg_light` | `app.theme_cls.backgroundColor` |
| `app.theme_cls.surface` | `app.theme_cls.surfaceColor` |
| `app.theme_cls.bg_dark` | `app.theme_cls.surfaceContainerColor` |

### Icon Properties

| Old (KivyMD 1.x) | New (KivyMD 2.0.1) |
|------------------|---------------------|
| `user_font_size: "24sp"` | `icon_size: "24dp"` |
| `font_size: dp(20)` | `icon_size: "20dp"` |

## Dialog Migration

### Old Dialog Syntax (KivyMD 1.x)
```python
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

dialog = MDDialog(
    title="Confirm",
    text="Are you sure?",
    buttons=[
        MDFlatButton(text="Cancel"),
        MDFlatButton(text="OK"),
    ],
)
```

### New Dialog Syntax (KivyMD 2.0.1)
```python
from kivymd.uix.dialog import (
    MDDialog, 
    MDDialogHeadlineText, 
    MDDialogSupportingText,
    MDDialogButtonContainer
)
from kivymd.uix.button import MDButton, MDButtonText

dialog = MDDialog(
    MDDialogHeadlineText(text="Confirm"),
    MDDialogSupportingText(text="Are you sure?"),
    MDDialogButtonContainer(
        MDButton(MDButtonText(text="Cancel"), style="text"),
        MDButton(MDButtonText(text="OK"), style="text"),
    ),
)
```

## Snackbar Migration

### Old Snackbar (KivyMD 1.x)
```python
from kivymd.uix.snackbar import Snackbar

Snackbar(text="Message").open()
```

### New Snackbar (KivyMD 2.0.1)
```python
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

snackbar = MDSnackbar(MDSnackbarText(text="Message"))
snackbar.open()
```

## Navigation Components

KivyMD 2.0.1 introduces new navigation components:
- `MDNavigationBar` (replaces `MDBottomNavigation`)
- `MDNavigationRail` 
- `MDNavigationDrawer` (updated)

## Quick Fix Script

Create a Python script to automatically update font styles:

```python
import os
import re

def update_font_styles(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Font style replacements
    replacements = {
        r'font_style:\s*"H1"': 'font_style: "Display"\n            role: "large"',
        r'font_style:\s*"H2"': 'font_style: "Display"\n            role: "medium"',
        r'font_style:\s*"H3"': 'font_style: "Display"\n            role: "small"',
        r'font_style:\s*"H4"': 'font_style: "Headline"\n            role: "large"',
        r'font_style:\s*"H5"': 'font_style: "Headline"\n            role: "medium"',
        r'font_style:\s*"H6"': 'font_style: "Headline"\n            role: "small"',
        r'font_style:\s*"Subtitle1"': 'font_style: "Title"\n            role: "large"',
        r'font_style:\s*"Subtitle2"': 'font_style: "Title"\n            role: "medium"',
        r'font_style:\s*"Body1"': 'font_style: "Body"\n            role: "large"',
        r'font_style:\s*"Body2"': 'font_style: "Body"\n            role: "medium"',
        r'font_style:\s*"Caption"': 'font_style: "Label"\n            role: "small"',
        r'font_style:\s*"Button"': 'font_style: "Label"\n            role: "large"',
        r'font_style:\s*"Overline"': 'font_style: "Label"\n            role: "small"',
        
        # Theme property replacements
        r'app\.theme_cls\.primary_color': 'app.theme_cls.primaryColor',
        r'app\.theme_cls\.accent_color': 'app.theme_cls.secondaryColor',
        r'app\.theme_cls\.bg_light': 'app.theme_cls.backgroundColor',
        r'app\.theme_cls\.surface': 'app.theme_cls.surfaceColor',
        
        # Icon property replacements
        r'user_font_size:\s*"(\d+)sp"': r'icon_size: "\1dp"',
    }
    
    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

# Run for all KV files
for root, dirs, files in os.walk('./kv'):
    for file in files:
        if file.endswith('.kv'):
            file_path = os.path.join(root, file)
            print(f"Updating {file_path}...")
            update_font_styles(file_path)
```

## Manual Steps Required

After running the script, you may need to manually:

1. **Check indentation**: The script might mess up indentation in some cases
2. **Verify role assignments**: Some font styles might need different roles based on context
3. **Update custom widgets**: Custom widget properties may need manual adjustment
4. **Test thoroughly**: Run your app and fix any remaining issues

## Breaking Changes Summary

1. **Font styles** completely changed - now use `font_style` + `role`
2. **Theme properties** renamed (camelCase instead of snake_case)
3. **Dialog API** completely restructured
4. **Navigation components** updated with new APIs
5. **Icon properties** changed from `user_font_size` to `icon_size`
6. **Snackbar API** restructured with new components

## Testing Your Migration

1. Run your app and check for any `KeyError` exceptions
2. Look for font/styling inconsistencies
3. Test all dialogs and popups
4. Verify navigation functionality
5. Check responsive behavior on different screen sizes

## Resources

- [KivyMD 2.0.1 Documentation](https://kivymd.readthedocs.io/en/latest/)
- [Material Design 3 Guidelines](https://m3.material.io/)
- [KivyMD GitHub Repository](https://github.com/kivymd/KivyMD)