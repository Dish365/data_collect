"""
Responsive Layout Utilities for Tablet Optimization
"""

from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout

class ResponsiveHelper:
    """Helper class for responsive design decisions"""
    
    @staticmethod
    def is_landscape():
        """Check if device is in landscape orientation"""
        return Window.width > Window.height
    
    @staticmethod
    def is_tablet():
        """Check if device has tablet-like dimensions"""
        return min(Window.width, Window.height) >= 600
    
    @staticmethod
    def get_screen_size_category():
        """Get screen size category for responsive design"""
        width, height = Window.width, Window.height
        min_size = min(width, height)
        
        if min_size < 480:
            return "phone"
        elif min_size < 768:
            return "small_tablet"
        elif min_size < 1024:
            return "tablet"
        else:
            return "large_tablet"
    
    @staticmethod
    def get_responsive_cols():
        """Get number of columns based on screen size"""
        category = ResponsiveHelper.get_screen_size_category()
        is_landscape = ResponsiveHelper.is_landscape()
        
        if category == "phone":
            return 1
        elif category == "small_tablet":
            return 2 if is_landscape else 1
        elif category == "tablet":
            return 3 if is_landscape else 2
        else:  # large_tablet
            return 4 if is_landscape else 3
    
    @staticmethod
    def get_responsive_spacing():
        """Get responsive spacing based on screen size"""
        category = ResponsiveHelper.get_screen_size_category()
        
        spacing_map = {
            "phone": dp(8),
            "small_tablet": dp(12),
            "tablet": dp(16),
            "large_tablet": dp(20)
        }
        
        return spacing_map.get(category, dp(16))
    
    @staticmethod
    def get_responsive_padding():
        """Get responsive padding based on screen size"""
        category = ResponsiveHelper.get_screen_size_category()
        
        padding_map = {
            "phone": dp(12),
            "small_tablet": dp(16), 
            "tablet": dp(24),
            "large_tablet": dp(32)
        }
        
        return padding_map.get(category, dp(16))
    
    @staticmethod
    def get_responsive_font_size(base_size="16sp"):
        """Get responsive font size based on screen size"""
        category = ResponsiveHelper.get_screen_size_category()
        base = int(base_size.replace("sp", ""))
        
        multiplier_map = {
            "phone": 1.0,
            "small_tablet": 1.1,
            "tablet": 1.2,
            "large_tablet": 1.3
        }
        
        multiplier = multiplier_map.get(category, 1.0)
        return f"{int(base * multiplier)}sp"


class ResponsiveBoxLayout(MDBoxLayout):
    """Responsive BoxLayout that adapts to screen size"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_responsive_properties()
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, *args):
        """Handle window resize"""
        self.update_responsive_properties()
    
    def update_responsive_properties(self):
        """Update properties based on current screen size"""
        # Update spacing and padding responsively
        self.spacing = ResponsiveHelper.get_responsive_spacing()
        self.padding = ResponsiveHelper.get_responsive_padding()
        
        # Switch orientation based on screen size if needed
        if hasattr(self, 'adaptive_orientation') and self.adaptive_orientation:
            if ResponsiveHelper.is_landscape() and ResponsiveHelper.is_tablet():
                self.orientation = 'horizontal'
            else:
                self.orientation = 'vertical'


class ResponsiveGridLayout(MDGridLayout):
    """Responsive GridLayout that adapts columns to screen size"""
    
    def __init__(self, base_cols=2, **kwargs):
        self.base_cols = base_cols
        super().__init__(**kwargs)
        self.update_responsive_properties()
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, *args):
        """Handle window resize"""
        self.update_responsive_properties()
    
    def update_responsive_properties(self):
        """Update properties based on current screen size"""
        # Update columns responsively
        responsive_cols = ResponsiveHelper.get_responsive_cols()
        self.cols = min(responsive_cols, self.base_cols)
        
        # Update spacing and padding
        self.spacing = ResponsiveHelper.get_responsive_spacing()
        self.padding = ResponsiveHelper.get_responsive_padding()


class AdaptiveCardLayout(MDBoxLayout):
    """Adaptive layout that switches between single and multi-column based on screen size"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.adaptive_height = True
        self.spacing = ResponsiveHelper.get_responsive_spacing()
        self.padding = ResponsiveHelper.get_responsive_padding()
        
        # Create container for cards
        self.card_container = ResponsiveGridLayout(base_cols=2)
        self.add_widget(self.card_container)
        
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, *args):
        """Handle window resize"""
        self.spacing = ResponsiveHelper.get_responsive_spacing()
        self.padding = ResponsiveHelper.get_responsive_padding()
    
    def add_card(self, card):
        """Add a card to the adaptive layout"""
        self.card_container.add_widget(card)
    
    def clear_cards(self):
        """Clear all cards"""
        self.card_container.clear_widgets()


def get_tablet_optimized_button_height():
    """Get tablet-optimized button height"""
    category = ResponsiveHelper.get_screen_size_category()
    
    height_map = {
        "phone": dp(40),
        "small_tablet": dp(48),
        "tablet": dp(56),
        "large_tablet": dp(64)
    }
    
    return height_map.get(category, dp(48))


def get_tablet_optimized_card_height():
    """Get tablet-optimized card height"""
    category = ResponsiveHelper.get_screen_size_category()
    
    height_map = {
        "phone": dp(120),
        "small_tablet": dp(140),
        "tablet": dp(160),
        "large_tablet": dp(180)
    }
    
    return height_map.get(category, dp(140))


def apply_tablet_text_scaling(widget, base_font_style="Body1"):
    """Apply tablet-appropriate text scaling to a widget"""
    if hasattr(widget, 'font_size'):
        category = ResponsiveHelper.get_screen_size_category()
        
        if category in ["tablet", "large_tablet"]:
            # Increase font size for tablets
            current_size = widget.font_size
            if isinstance(current_size, str) and current_size.endswith("sp"):
                base_size = int(current_size.replace("sp", ""))
                widget.font_size = f"{int(base_size * 1.2)}sp"


# Tablet-Optimized Button Helpers
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton

class TabletOptimizedButton(MDRaisedButton):
    """Button that automatically adapts size for tablet use"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_tablet_properties()
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, *args):
        """Handle window resize"""
        self.update_tablet_properties()
    
    def update_tablet_properties(self):
        """Update button properties for tablet optimization"""
        category = ResponsiveHelper.get_screen_size_category()
        
        # Set tablet-appropriate height
        height_map = {
            "phone": dp(40),
            "small_tablet": dp(48),
            "tablet": dp(56),
            "large_tablet": dp(64)
        }
        
        self.size_hint_y = None
        self.height = height_map.get(category, dp(48))
        
        # Set tablet-appropriate font size
        font_size_map = {
            "phone": "14sp",
            "small_tablet": "16sp", 
            "tablet": "18sp",
            "large_tablet": "20sp"
        }
        
        if hasattr(self, 'font_size'):
            self.font_size = font_size_map.get(category, "16sp")


class TabletOptimizedIconButton(MDIconButton):
    """Icon button that automatically adapts size for tablet use"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_tablet_properties()
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, *args):
        """Handle window resize"""
        self.update_tablet_properties()
    
    def update_tablet_properties(self):
        """Update icon button properties for tablet optimization"""
        category = ResponsiveHelper.get_screen_size_category()
        
        # Set tablet-appropriate size
        size_map = {
            "phone": (dp(40), dp(40)),
            "small_tablet": (dp(48), dp(48)),
            "tablet": (dp(56), dp(56)),
            "large_tablet": (dp(64), dp(64))
        }
        
        self.size_hint = (None, None)
        self.size = size_map.get(category, (dp(48), dp(48)))
        
        # Set tablet-appropriate icon size
        icon_size_map = {
            "phone": "24sp",
            "small_tablet": "28sp",
            "tablet": "32sp", 
            "large_tablet": "36sp"
        }
        
        if hasattr(self, 'user_font_size'):
            self.user_font_size = icon_size_map.get(category, "28sp")


class ResponsiveButtonGrid(ResponsiveGridLayout):
    """Grid layout specifically optimized for buttons"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_height = True
        self.size_hint_y = None
        self.height = self.minimum_height
        
    def add_button(self, button_text, callback=None, **button_kwargs):
        """Add a tablet-optimized button to the grid"""
        button = TabletOptimizedButton(
            text=button_text,
            **button_kwargs
        )
        
        if callback:
            button.bind(on_press=callback)
            
        self.add_widget(button)
        return button
    
    def add_icon_button(self, icon, callback=None, **button_kwargs):
        """Add a tablet-optimized icon button to the grid"""
        button = TabletOptimizedIconButton(
            icon=icon,
            **button_kwargs
        )
        
        if callback:
            button.bind(on_press=callback)
            
        self.add_widget(button)
        return button


def create_tablet_action_bar(actions_list):
    """Create a responsive action bar with tablet-optimized buttons
    
    Args:
        actions_list: List of tuples (text, callback) or (icon, callback, is_icon)
    """
    action_bar = ResponsiveButtonGrid(base_cols=len(actions_list))
    action_bar.orientation = 'horizontal'
    action_bar.size_hint_y = None
    action_bar.height = get_tablet_optimized_button_height()
    
    for action in actions_list:
        if len(action) == 3 and action[2]:  # Icon button
            icon, callback, _ = action
            action_bar.add_icon_button(icon, callback)
        else:  # Text button
            text, callback = action[:2]
            action_bar.add_button(text, callback)
    
    return action_bar


def create_responsive_button_row(buttons_config, max_cols=4):
    """Create a responsive row of buttons that adapts to screen size
    
    Args:
        buttons_config: List of dicts with button configuration
        max_cols: Maximum columns for large screens
    """
    category = ResponsiveHelper.get_screen_size_category()
    is_landscape = ResponsiveHelper.is_landscape()
    
    # Determine optimal columns
    if category == "phone":
        cols = 1 if not is_landscape else 2
    elif category == "small_tablet": 
        cols = 2 if not is_landscape else 3
    elif category == "tablet":
        cols = 2 if not is_landscape else min(max_cols, 4)
    else:  # large_tablet
        cols = 3 if not is_landscape else min(max_cols, 4)
    
    # Create grid layout
    button_grid = ResponsiveGridLayout(base_cols=cols)
    button_grid.adaptive_height = True
    button_grid.size_hint_y = None
    button_grid.height = button_grid.minimum_height
    
    # Add buttons
    for config in buttons_config:
        if config.get('icon'):
            button = TabletOptimizedIconButton(**config)
        else:
            button = TabletOptimizedButton(**config)
        button_grid.add_widget(button)
    
    return button_grid


# Responsive Typography Helpers
from kivymd.uix.label import MDLabel

class ResponsiveLabel(MDLabel):
    """Label that automatically scales typography for tablet use"""
    
    def __init__(self, base_font_style="Body1", **kwargs):
        self.base_font_style = base_font_style
        super().__init__(**kwargs)
        self.update_typography()
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, *args):
        """Handle window resize"""
        self.update_typography()
    
    def update_typography(self):
        """Update typography based on screen size"""
        category = ResponsiveHelper.get_screen_size_category()
        
        # Font style mapping for different screen sizes
        style_scaling = {
            "phone": {
                "H1": "H2", "H2": "H3", "H3": "H4", "H4": "H5", "H5": "H6", "H6": "Subtitle1",
                "Subtitle1": "Subtitle2", "Subtitle2": "Body1", "Body1": "Body2", "Body2": "Caption"
            },
            "small_tablet": {
                "H1": "H1", "H2": "H2", "H3": "H3", "H4": "H4", "H5": "H5", "H6": "H6",
                "Subtitle1": "Subtitle1", "Subtitle2": "Subtitle2", "Body1": "Body1", "Body2": "Body2"
            },
            "tablet": {
                "H1": "H1", "H2": "H1", "H3": "H2", "H4": "H3", "H5": "H4", "H6": "H5",
                "Subtitle1": "H6", "Subtitle2": "Subtitle1", "Body1": "Subtitle2", "Body2": "Body1"
            },
            "large_tablet": {
                "H1": "H1", "H2": "H1", "H3": "H2", "H4": "H3", "H5": "H4", "H6": "H5",
                "Subtitle1": "H6", "Subtitle2": "Subtitle1", "Body1": "Subtitle2", "Body2": "Body1"
            }
        }
        
        scaling = style_scaling.get(category, style_scaling["small_tablet"])
        new_style = scaling.get(self.base_font_style, self.base_font_style)
        
        if hasattr(self, 'font_style'):
            self.font_style = new_style


def get_responsive_font_size(base_size_sp, style="Body1"):
    """Get responsive font size based on screen category
    
    Args:
        base_size_sp: Base size in sp (without 'sp' suffix)
        style: Font style for context (Body1, H1, etc.)
    """
    category = ResponsiveHelper.get_screen_size_category()
    
    # Base multipliers for different screen sizes
    multipliers = {
        "phone": 0.9,
        "small_tablet": 1.0,
        "tablet": 1.15,
        "large_tablet": 1.3
    }
    
    # Additional scaling for headers vs body text
    style_multipliers = {
        "H1": 1.2, "H2": 1.15, "H3": 1.1, "H4": 1.05, "H5": 1.0, "H6": 1.0,
        "Subtitle1": 1.0, "Subtitle2": 0.95, "Body1": 1.0, "Body2": 0.95, "Caption": 0.9
    }
    
    base_multiplier = multipliers.get(category, 1.0)
    style_multiplier = style_multipliers.get(style, 1.0)
    
    final_size = base_size_sp * base_multiplier * style_multiplier
    return f"{int(final_size)}sp"


def apply_responsive_typography(widget, base_style="Body1"):
    """Apply responsive typography to any widget with text
    
    Args:
        widget: Widget to apply typography to
        base_style: Base font style to scale from
    """
    if not hasattr(widget, 'font_style') and not hasattr(widget, 'font_size'):
        return
    
    category = ResponsiveHelper.get_screen_size_category()
    
    # Apply font style if widget supports it
    if hasattr(widget, 'font_style'):
        style_scaling = {
            "phone": base_style,
            "small_tablet": base_style,
            "tablet": _scale_font_style_up(base_style),
            "large_tablet": _scale_font_style_up(base_style, 2)
        }
        widget.font_style = style_scaling.get(category, base_style)
    
    # Apply direct font size if widget uses it
    elif hasattr(widget, 'font_size'):
        if isinstance(widget.font_size, str) and widget.font_size.endswith("sp"):
            base_size = int(widget.font_size.replace("sp", ""))
            widget.font_size = get_responsive_font_size(base_size, base_style)


def _scale_font_style_up(style, levels=1):
    """Helper to scale font style up by specified levels"""
    hierarchy = ["Caption", "Body2", "Body1", "Subtitle2", "Subtitle1", "H6", "H5", "H4", "H3", "H2", "H1"]
    
    try:
        current_index = hierarchy.index(style)
        new_index = min(current_index + levels, len(hierarchy) - 1)
        return hierarchy[new_index]
    except ValueError:
        return style


def create_responsive_text_section(title, content, title_style="H6", content_style="Body1"):
    """Create a responsive text section with title and content
    
    Args:
        title: Title text
        content: Content text
        title_style: Base style for title
        content_style: Base style for content
    """
    section = ResponsiveBoxLayout()
    section.orientation = 'vertical'
    section.adaptive_height = True
    section.size_hint_y = None
    section.height = section.minimum_height
    
    # Title label
    title_label = ResponsiveLabel(
        text=title,
        base_font_style=title_style,
        size_hint_y=None,
        height=dp(32)
    )
    apply_responsive_typography(title_label, title_style)
    
    # Content label
    content_label = ResponsiveLabel(
        text=content,
        base_font_style=content_style,
        text_size=(None, None),
        adaptive_height=True
    )
    apply_responsive_typography(content_label, content_style)
    
    section.add_widget(title_label)
    section.add_widget(content_label)
    
    return section


def get_tablet_line_height(base_line_height=1.2):
    """Get tablet-appropriate line height"""
    category = ResponsiveHelper.get_screen_size_category()
    
    line_height_map = {
        "phone": base_line_height,
        "small_tablet": base_line_height * 1.1,
        "tablet": base_line_height * 1.2,
        "large_tablet": base_line_height * 1.3
    }
    
    return line_height_map.get(category, base_line_height)


def optimize_text_for_tablets(text_widget):
    """Comprehensive tablet text optimization for any text widget"""
    if not text_widget:
        return
    
    category = ResponsiveHelper.get_screen_size_category()
    
    # Apply responsive font sizing
    apply_responsive_typography(text_widget)
    
    # Optimize text wrapping and sizing for tablets
    if category in ["tablet", "large_tablet"]:
        # Better text wrapping for larger screens
        if hasattr(text_widget, 'text_size'):
            if hasattr(text_widget, 'width'):
                text_widget.text_size = (text_widget.width, None)
        
        # Improve text contrast for larger viewing distances
        if hasattr(text_widget, 'theme_text_color'):
            # Keep existing theme but ensure good contrast
            pass
    
    # Increase padding for better readability on tablets
    if hasattr(text_widget, 'padding'):
        text_widget.padding = ResponsiveHelper.get_responsive_padding() 