#!/usr/bin/env python3
"""
Test script to verify text input validation logic
"""

def test_has_text_input_data():
    """Test the has_text_input_data function logic"""
    
    # Mock widget classes for testing
    class MockTextField:
        def __init__(self, text=""):
            self.text = text
    
    class MockCheckbox:
        def __init__(self, active=False):
            self.active = active
    
    class MockSlider:
        def __init__(self, value=None):
            self.value = value
    
    class MockWidget:
        def __init__(self, response_field):
            self.response_field = response_field
    
    # Test cases
    test_cases = [
        # Text field tests
        ("Empty text field", MockWidget(MockTextField("")), False),
        ("Text field with spaces", MockWidget(MockTextField("   ")), False),
        ("Text field with content", MockWidget(MockTextField("Hello")), True),
        ("Text field with content and spaces", MockWidget(MockTextField("  Hello  ")), True),
        
        # Checkbox tests
        ("Empty checkbox list", MockWidget([]), False),
        ("Checkbox list with no selection", MockWidget([(MockCheckbox(False), "Option 1")]), False),
        ("Checkbox list with selection", MockWidget([(MockCheckbox(True), "Option 1")]), True),
        
        # Slider tests
        ("Slider with None value", MockWidget(MockSlider(None)), False),
        ("Slider with value", MockWidget(MockSlider(3)), True),
        ("Slider with zero value", MockWidget(MockSlider(0)), True),
    ]
    
    # Test the logic (simplified version of the actual function)
    def has_text_input_data(widget):
        if hasattr(widget, 'response_field'):
            if hasattr(widget.response_field, 'text'):
                # Direct text field (MDTextField)
                value = widget.response_field.text
                return bool(value is not None and str(value).strip())
            elif isinstance(widget.response_field, list):
                # Checkbox list for choice questions
                return any(cb.active for cb, opt in widget.response_field)
            elif hasattr(widget.response_field, 'value'):
                # Slider or other value-based widget
                value = widget.response_field.value
                return bool(value is not None and str(value).strip())
        return False
    
    # Run tests
    print("Testing text input validation logic...")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, widget, expected in test_cases:
        result = has_text_input_data(widget)
        if result == expected:
            print(f"✅ PASS: {test_name}")
            passed += 1
        else:
            print(f"❌ FAIL: {test_name}")
            print(f"   Expected: {expected}, Got: {result}")
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed!")

if __name__ == "__main__":
    test_has_text_input_data() 