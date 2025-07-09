#!/usr/bin/env python3
"""
Script to fix question types in setup_cocoa_survey.py
"""

import re

def fix_question_types():
    """Fix all question types in the setup script"""
    
    with open('setup_cocoa_survey.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the replacements
    replacements = [
        ('"question_type": "single_choice"', '"question_type": "choice_single"'),
        ('"question_type": "multiple_choice"', '"question_type": "choice_multiple"'),
        ('"question_type": "scale_rating"', '"question_type": "scale_rating"'),  # This one is already correct
    ]
    
    # Apply replacements
    for old, new in replacements:
        content = content.replace(old, new)
    
    # Write back to file
    with open('setup_cocoa_survey.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed all question types!")

if __name__ == "__main__":
    fix_question_types() 