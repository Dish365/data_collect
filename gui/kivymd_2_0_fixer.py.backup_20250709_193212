#!/usr/bin/env python3
"""
KivyMD 2.0.0 Migration Fixer Script
===================================

This script automatically fixes import issues and component changes 
when migrating from KivyMD 1.x to KivyMD 2.0.0.

Usage:
    python kivymd_2_0_fixer.py [directory]

If no directory is provided, it will scan the current directory.
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict
import shutil
from datetime import datetime


class KivyMD2Fixer:
    """Fix KivyMD 2.0.0 compatibility issues in Python and KV files."""
    
    def __init__(self, dry_run: bool = False, backup: bool = True):
        self.dry_run = dry_run
        self.backup = backup
        self.changes_made = []
        
        # Python file import fixes
        self.py_import_fixes = [
            # Date/Time pickers
            (r'from kivymd\.uix\.pickers import MDDatePicker, MDTimePicker',
             'from kivymd.uix.pickers.datepicker import MDDatePicker\nfrom kivymd.uix.pickers.timepicker import MDTimePicker'),
            
            (r'from kivymd\.uix\.pickers import MDDatePicker',
             'from kivymd.uix.pickers.datepicker import MDDatePicker'),
            
            (r'from kivymd\.uix\.pickers import MDTimePicker',
             'from kivymd.uix.pickers.timepicker import MDTimePicker'),
            
            # Progress indicators
            (r'from kivymd\.uix\.progressbar import MDProgressBar',
             'from kivymd.uix.progressindicator import MDCircularProgressIndicator'),
            
            (r'from kivymd\.uix\.progressbar import MDCircularProgressIndicator',
             'from kivymd.uix.progressindicator import MDCircularProgressIndicator'),
            
            # Tabs - old system
            (r'from kivymd\.uix\.tab import MDTabsBase',
             'from kivymd.uix.tab import MDTabsItem, MDTabsItemText, MDTabsItemIcon'),
            
            # Button changes
            (r'from kivymd\.uix\.button import MDRaisedButton',
             'from kivymd.uix.button import MDButton'),
            
            (r'from kivymd\.uix\.button import MDFlatButton',
             'from kivymd.uix.button import MDButton'),
        ]
        
        # KV file import fixes
        self.kv_import_fixes = [
            # Progress indicators
            (r'#:import MDProgressBar kivymd\.uix\.progressbar\.MDProgressBar',
             '#:import MDCircularProgressIndicator kivymd.uix.progressindicator.MDCircularProgressIndicator'),
            
            (r'#:import MDSpinner kivymd\.uix\.spinner\.MDSpinner',
             '#:import MDCircularProgressIndicator kivymd.uix.progressindicator.MDCircularProgressIndicator'),
            
            # Date/Time pickers
            (r'#:import MDDatePicker kivymd\.uix\.pickers\.MDDatePicker',
             '#:import MDDatePicker kivymd.uix.pickers.datepicker.MDDatePicker'),
            
            (r'#:import MDTimePicker kivymd\.uix\.pickers\.MDTimePicker',
             '#:import MDTimePicker kivymd.uix.pickers.timepicker.MDTimePicker'),
            
            # Tabs
            (r'#:import MDTabsBase kivymd\.uix\.tab\.MDTabsBase',
             '#:import MDTabsItem kivymd.uix.tab.MDTabsItem\n#:import MDTabsItemText kivymd.uix.tab.MDTabsItemText\n#:import MDTabsItemIcon kivymd.uix.tab.MDTabsItemIcon'),
            
            # Buttons
            (r'#:import MDRaisedButton kivymd\.uix\.button\.MDRaisedButton',
             '#:import MDButton kivymd.uix.button.MDButton'),
            
            (r'#:import MDFlatButton kivymd\.uix\.button\.MDFlatButton',
             '#:import MDButton kivymd.uix.button.MDButton'),
        ]
        
        # Component name changes in Python files
        self.py_component_fixes = [
            # Progress bars
            (r'MDProgressBar\s*\(', 'MDCircularProgressIndicator('),
            (r'MDSpinner\s*\(', 'MDCircularProgressIndicator('),
            
            # Buttons
            (r'MDRaisedButton\s*\(', 'MDButton('),
            (r'MDFlatButton\s*\(', 'MDButton('),
            
            # Tab base classes - need special handling
            (r'class\s+(\w+)\s*\(\s*MDBoxLayout\s*,\s*MDTabsBase\s*\)',
             r'class \1(MDBoxLayout)'),
            
            (r'class\s+(\w+)\s*\(\s*MDTabsBase\s*,\s*MDBoxLayout\s*\)',
             r'class \1(MDBoxLayout)'),
        ]
        
        # Component name changes in KV files
        self.kv_component_fixes = [
            # Progress indicators
            (r'MDProgressBar:', 'MDCircularProgressIndicator:'),
            (r'MDSpinner:', 'MDCircularProgressIndicator:'),
            
            # Buttons
            (r'MDRaisedButton:', 'MDButton:'),
            (r'MDFlatButton:', 'MDButton:'),
        ]
        
        # Property changes
        self.property_fixes = [
            # Progress indicator properties
            (r'start:\s*([^\n]+)', r'active: \1'),
            
            # Button style additions (for MDButton)
            (r'(MDButton:(?:[^}]*(?:\n[ \t]*[^:\n]+:[^}]*)*)?)', 
             self._add_button_style),
        ]
        
        # Fallback imports for missing components
        self.fallback_imports = {
            'MDDatePicker': '''# Updated imports for KivyMD 2.0.0
try:
    from kivymd.uix.pickers.datepicker import MDDatePicker
except ImportError:
    try:
        from kivymd.uix.pickers.datepicker.datepicker import MDDatePicker
    except ImportError:
        try:
            from kivymd.uix.pickers.datepicker import MDDatePicker
        except ImportError:
            print("Warning: Could not import MDDatePicker. Date fields will be disabled.")
            MDDatePicker = None''',
            
            'MDTimePicker': '''# Updated imports for KivyMD 2.0.0
try:
    from kivymd.uix.pickers.timepicker import MDTimePicker
except ImportError:
    try:
        from kivymd.uix.pickers.timepicker.timepicker import MDTimePicker
    except ImportError:
        try:
            from kivymd.uix.pickers.timepicker import MDTimePicker
        except ImportError:
            print("Warning: Could not import MDTimePicker. Time fields will be disabled.")
            MDTimePicker = None''',
        }
    
    def _add_button_style(self, match):
        """Add style="elevated" to MDButton components."""
        button_block = match.group(1)
        if 'style:' not in button_block:
            # Add style as the first property
            lines = button_block.split('\n')
            if len(lines) > 1:
                lines.insert(1, f'{lines[1][:len(lines[1]) - len(lines[1].lstrip())]}style: "elevated"')
                return '\n'.join(lines)
        return button_block
    
    def create_backup(self, file_path: Path) -> None:
        """Create a backup of the original file."""
        if not self.backup:
            return
        
        backup_path = file_path.with_suffix(f'{file_path.suffix}.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        shutil.copy2(file_path, backup_path)
        print(f"📄 Created backup: {backup_path}")
    
    def fix_python_file(self, file_path: Path) -> bool:
        """Fix a Python file for KivyMD 2.0.0 compatibility."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_changed = False
            
            # Apply import fixes
            for old_pattern, new_pattern in self.py_import_fixes:
                if re.search(old_pattern, content):
                    content = re.sub(old_pattern, new_pattern, content)
                    file_changed = True
                    print(f"  ✓ Fixed import: {old_pattern.replace('\\', '')}")
            
            # Apply component fixes
            for old_pattern, new_pattern in self.py_component_fixes:
                if re.search(old_pattern, content):
                    content = re.sub(old_pattern, new_pattern, content)
                    file_changed = True
                    print(f"  ✓ Fixed component: {old_pattern.replace('\\', '')}")
            
            # Add fallback imports where needed
            for component, fallback in self.fallback_imports.items():
                if f'from kivymd.uix.pickers import {component}' in original_content:
                    content = content.replace(f'from kivymd.uix.pickers import {component}', fallback)
                    file_changed = True
                    print(f"  ✓ Added fallback import for {component}")
            
            # Special handling for tabs
            if 'MDTabsBase' in content:
                content = self._fix_tabs_system(content)
                file_changed = True
                print(f"  ✓ Updated tabs system")
            
            if file_changed and not self.dry_run:
                self.create_backup(file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return file_changed
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False
    
    def fix_kv_file(self, file_path: Path) -> bool:
        """Fix a KV file for KivyMD 2.0.0 compatibility."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_changed = False
            
            # Apply import fixes
            for old_pattern, new_pattern in self.kv_import_fixes:
                if re.search(old_pattern, content):
                    content = re.sub(old_pattern, new_pattern, content)
                    file_changed = True
                    print(f"  ✓ Fixed KV import: {old_pattern.replace('\\', '')}")
            
            # Apply component fixes
            for old_pattern, new_pattern in self.kv_component_fixes:
                if re.search(old_pattern, content):
                    content = re.sub(old_pattern, new_pattern, content)
                    file_changed = True
                    print(f"  ✓ Fixed KV component: {old_pattern}")
            
            # Apply property fixes
            for old_pattern, new_pattern in self.property_fixes:
                if re.search(old_pattern, content):
                    if callable(new_pattern):
                        content = re.sub(old_pattern, new_pattern, content)
                    else:
                        content = re.sub(old_pattern, new_pattern, content)
                    file_changed = True
                    print(f"  ✓ Fixed property: {old_pattern.replace('\\', '')}")
            
            # Special fixes for common issues
            if 'MDTabs:' in content and 'MDTabsBase' in original_content:
                content = self._fix_kv_tabs(content)
                file_changed = True
                print(f"  ✓ Updated KV tabs system")
            
            if file_changed and not self.dry_run:
                self.create_backup(file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return file_changed
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False
    
    def _fix_tabs_system(self, content: str) -> str:
        """Fix the tabs system in Python files."""
        # This is a complex transformation that might need manual review
        # For now, just remove MDTabsBase inheritance and add a comment
        
        # Remove MDTabsBase from class inheritance
        content = re.sub(
            r'class\s+(\w+)\s*\(\s*([^)]*),\s*MDTabsBase\s*\)',
            r'class \1(\2)  # TODO: Review tab implementation for KivyMD 2.0.0',
            content
        )
        
        content = re.sub(
            r'class\s+(\w+)\s*\(\s*MDTabsBase\s*,\s*([^)]*)\)',
            r'class \1(\2)  # TODO: Review tab implementation for KivyMD 2.0.0',
            content
        )
        
        content = re.sub(
            r'class\s+(\w+)\s*\(\s*MDTabsBase\s*\)',
            r'class \1(MDBoxLayout)  # TODO: Review tab implementation for KivyMD 2.0.0',
            content
        )
        
        return content
    
    def _fix_kv_tabs(self, content: str) -> str:
        """Fix tabs in KV files."""
        # Convert old MDTabs usage to new system
        # This is a basic transformation - might need manual review
        
        # Replace old tab structure with new one
        content = re.sub(
            r'MDTabs:\s*\n(\s+)id:\s*(\w+)',
            r'MDTabsPrimary:\n\1id: \2',
            content
        )
        
        return content
    
    def scan_directory(self, directory: Path) -> List[Path]:
        """Scan directory for Python and KV files."""
        files = []
        
        for ext in ['*.py', '*.kv']:
            files.extend(directory.rglob(ext))
        
        # Filter out backup files and __pycache__
        files = [f for f in files if '__pycache__' not in str(f) and '.backup_' not in str(f)]
        
        return files
    
    def fix_directory(self, directory: Path) -> Dict[str, int]:
        """Fix all files in a directory."""
        files = self.scan_directory(directory)
        
        results = {
            'total_files': len(files),
            'python_files': 0,
            'kv_files': 0,
            'files_changed': 0,
            'errors': 0
        }
        
        print(f"🔍 Found {len(files)} files to process in {directory}")
        
        for file_path in files:
            print(f"\n📁 Processing: {file_path}")
            
            try:
                if file_path.suffix == '.py':
                    results['python_files'] += 1
                    if self.fix_python_file(file_path):
                        results['files_changed'] += 1
                        self.changes_made.append(str(file_path))
                        
                elif file_path.suffix == '.kv':
                    results['kv_files'] += 1
                    if self.fix_kv_file(file_path):
                        results['files_changed'] += 1
                        self.changes_made.append(str(file_path))
                        
            except Exception as e:
                results['errors'] += 1
                print(f"❌ Error processing {file_path}: {e}")
        
        return results
    
    def generate_report(self, results: Dict[str, int]) -> str:
        """Generate a summary report."""
        report = f"""
🎯 KivyMD 2.0.0 Migration Report
{'='*40}

📊 Summary:
  • Total files scanned: {results['total_files']}
  • Python files: {results['python_files']}
  • KV files: {results['kv_files']}
  • Files changed: {results['files_changed']}
  • Errors: {results['errors']}

✅ Files modified:
"""
        
        for file_path in self.changes_made:
            report += f"  • {file_path}\n"
        
        if not self.changes_made:
            report += "  • No files needed changes\n"
        
        report += f"""
🔧 Common fixes applied:
  • MDProgressBar → MDCircularProgressIndicator
  • MDSpinner → MDCircularProgressIndicator
  • MDRaisedButton → MDButton (with style="elevated")
  • MDFlatButton → MDButton (with style="elevated")
  • Date/Time picker import paths updated
  • MDTabsBase system updated (may need manual review)
  • Progress indicator properties (start → active)

⚠️  Manual review needed:
  • Tab system implementations (marked with TODO comments)
  • Custom button styling
  • Complex progress indicator usage
  • Date/time picker error handling

💡 Next steps:
  1. Test your application thoroughly
  2. Review TODO comments in code
  3. Check for any remaining import errors
  4. Update custom themes if needed
"""
        
        return report


def main():
    """Main function to run the fixer script."""
    parser = argparse.ArgumentParser(
        description='Fix KivyMD 2.0.0 compatibility issues',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python kivymd_2_0_fixer.py                    # Fix current directory
  python kivymd_2_0_fixer.py ./src             # Fix specific directory
  python kivymd_2_0_fixer.py --dry-run         # Preview changes only
  python kivymd_2_0_fixer.py --no-backup       # Don't create backups
        """
    )
    
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to scan (default: current directory)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Don\'t create backup files'
    )
    
    args = parser.parse_args()
    
    directory = Path(args.directory).resolve()
    
    if not directory.exists():
        print(f"❌ Directory {directory} does not exist")
        sys.exit(1)
    
    print(f"🚀 KivyMD 2.0.0 Migration Fixer")
    print(f"📂 Target directory: {directory}")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    if args.no_backup:
        print("⚠️  Backup disabled - Original files will be overwritten")
    
    # Create fixer instance
    fixer = KivyMD2Fixer(
        dry_run=args.dry_run,
        backup=not args.no_backup
    )
    
    # Fix directory
    results = fixer.fix_directory(directory)
    
    # Generate and display report
    report = fixer.generate_report(results)
    print(report)
    
    # Write report to file
    if not args.dry_run:
        report_file = directory / 'kivymd_migration_report.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 Report saved to: {report_file}")
    
    return 0 if results['errors'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())