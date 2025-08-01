"""
Responsive Layout Helper for KivyMD Applications
Provides utilities for creating responsive layouts across different screen sizes
Follows Material Design 3 responsive breakpoints
"""

from kivy.core.window import Window
from kivy.metrics import dp
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.label import MDLabel


class ResponsiveHelper(EventDispatcher):
    """
    Helper class for managing responsive layouts across different screen sizes
    Follows Material Design responsive breakpoints
    """
    
    # Screen size categories
    PHONE = "phone"
    SMALL_TABLET = "small_tablet"
    TABLET = "tablet"
    LARGE_TABLET = "large_tablet"
    DESKTOP = "desktop"
    
    # Breakpoints (in dp)
    BREAKPOINTS = {
        PHONE: 0,           # 0-599dp
        SMALL_TABLET: 600,  # 600-839dp
        TABLET: 840,        # 840-1199dp
        LARGE_TABLET: 1200, # 1200-1599dp
        DESKTOP: 1600       # 1600dp+
    }
    
    # Current screen properties
    current_category = StringProperty(PHONE)
    is_landscape = BooleanProperty(False)
    screen_width = NumericProperty(0)
    screen_height = NumericProperty(0)
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResponsiveHelper, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        super().__init__()
        self._initialized = True
        
        # Bind to window size changes
        Window.bind(size=self._on_window_resize)
        
        # Initialize current values
        self._update_screen_info()
    
    def _on_window_resize(self, window, size):
        """Handle window resize events"""
        self._update_screen_info()
    
    def _update_screen_info(self):
        """Update current screen information"""
        self.screen_width = Window.width
        self.screen_height = Window.height
        self.is_landscape = Window.width > Window.height
        self.current_category = self._get_category_for_width(Window.width)
    
    def _get_category_for_width(self, width):
        """Get screen category for given width"""
        width_dp = width  # Assuming width is already in dp
        
        if width_dp < self.BREAKPOINTS[self.SMALL_TABLET]:
            return self.PHONE
        elif width_dp < self.BREAKPOINTS[self.TABLET]:
            return self.SMALL_TABLET
        elif width_dp < self.BREAKPOINTS[self.LARGE_TABLET]:
            return self.TABLET
        elif width_dp < self.BREAKPOINTS[self.DESKTOP]:
            return self.LARGE_TABLET
        else:
            return self.DESKTOP
    
    @classmethod
    def get_screen_size_category(cls):
        """Get current screen size category"""
        instance = cls()
        return instance.current_category
    
    @classmethod
    def is_landscape(cls):
        """Check if screen is in landscape orientation"""
        instance = cls()
        return instance.is_landscape
    
    @classmethod
    def get_responsive_value(cls, phone=None, small_tablet=None, tablet=None, 
                           large_tablet=None, desktop=None, default=None):
        """
        Get responsive value based on current screen size
        
        Args:
            phone: Value for phone screens
            small_tablet: Value for small tablet screens
            tablet: Value for tablet screens
            large_tablet: Value for large tablet screens
            desktop: Value for desktop screens
            default: Default value if specific size not provided
        
        Returns:
            Appropriate value for current screen size
        """
        instance = cls()
        category = instance.current_category
        
        # Create value mapping
        values = {
            cls.PHONE: phone,
            cls.SMALL_TABLET: small_tablet,
            cls.TABLET: tablet,
            cls.LARGE_TABLET: large_tablet,
            cls.DESKTOP: desktop
        }
        
        # Get value for current category or fall back to default
        value = values.get(category)
        if value is not None:
            return value
        
        # Fallback logic - use the closest smaller screen size value
        fallback_order = [cls.DESKTOP, cls.LARGE_TABLET, cls.TABLET, cls.SMALL_TABLET, cls.PHONE]
        current_index = fallback_order.index(category)
        
        for fallback_category in fallback_order[current_index:]:
            fallback_value = values.get(fallback_category)
            if fallback_value is not None:
                return fallback_value
        
        return default
    
    @classmethod
    def get_padding(cls):
        """Get responsive padding values"""
        return cls.get_responsive_value(
            phone=dp(12),
            small_tablet=dp(16),
            tablet=dp(20),
            large_tablet=dp(24),
            desktop=dp(28),
            default=dp(16)
        )
    
    @classmethod
    def get_spacing(cls):
        """Get responsive spacing values"""
        return cls.get_responsive_value(
            phone=dp(8),
            small_tablet=dp(12),
            tablet=dp(16),
            large_tablet=dp(20),
            desktop=dp(24),
            default=dp(12)
        )
    
    @classmethod
    def get_card_elevation(cls):
        """Get responsive card elevation"""
        return cls.get_responsive_value(
            phone=1,
            small_tablet=2,
            tablet=2,
            large_tablet=3,
            desktop=3,
            default=2
        )
    
    @classmethod
    def get_font_sizes(cls):
        """Get responsive font sizes"""
        category = cls.get_screen_size_category()
        
        if category == cls.PHONE:
            return {
                "headline": "18sp",
                "title": "16sp",
                "subtitle": "14sp",
                "body": "13sp",
                "small": "11sp",
                "hint": "10sp"
            }
        elif category == cls.SMALL_TABLET:
            return {
                "headline": "20sp",
                "title": "18sp",
                "subtitle": "16sp",
                "body": "14sp",
                "small": "12sp",
                "hint": "11sp"
            }
        elif category in [cls.TABLET, cls.LARGE_TABLET]:
            return {
                "headline": "24sp",
                "title": "20sp",
                "subtitle": "18sp",
                "body": "16sp",
                "small": "14sp",
                "hint": "12sp"
            }
        else:  # Desktop
            return {
                "headline": "28sp",
                "title": "24sp",
                "subtitle": "20sp",
                "body": "18sp",
                "small": "16sp",
                "hint": "14sp"
            }
    
    @classmethod
    def get_touch_target_size(cls):
        """Get responsive touch target sizes"""
        return cls.get_responsive_value(
            phone=dp(40),
            small_tablet=dp(44),
            tablet=dp(48),
            large_tablet=dp(52),
            desktop=dp(56),
            default=dp(44)
        )
    
    @classmethod
    def get_icon_size(cls):
        """Get responsive icon sizes"""
        return cls.get_responsive_value(
            phone=dp(20),
            small_tablet=dp(22),
            tablet=dp(24),
            large_tablet=dp(26),
            desktop=dp(28),
            default=dp(24)
        )
    
    @classmethod
    def should_use_sidebar(cls):
        """Determine if sidebar layout should be used"""
        category = cls.get_screen_size_category()
        is_landscape = cls.is_landscape()
        
        if category == cls.LARGE_TABLET:
            return True
        elif category == cls.TABLET:
            return is_landscape
        elif category == cls.SMALL_TABLET:
            return is_landscape
        else:
            return False
    
    @classmethod
    def get_layout_columns(cls):
        """Get number of columns for grid layouts"""
        return cls.get_responsive_value(
            phone=1,
            small_tablet=2,
            tablet=3,
            large_tablet=4,
            desktop=5,
            default=1
        )
    
    @classmethod
    def get_card_width_ratio(cls):
        """Get card width ratio for responsive cards"""
        category = cls.get_screen_size_category()
        is_landscape = cls.is_landscape()
        
        if category == cls.PHONE:
            return 1.0  # Full width
        elif category == cls.SMALL_TABLET:
            return 0.8 if not is_landscape else 0.6
        elif category == cls.TABLET:
            return 0.7 if not is_landscape else 0.5
        elif category == cls.LARGE_TABLET:
            return 0.6
        else:  # Desktop
            return 0.5
    
    @classmethod
    def get_sidebar_width_ratio(cls):
        """Get sidebar width ratio"""
        return cls.get_responsive_value(
            phone=0.0,
            small_tablet=0.25,
            tablet=0.3,
            large_tablet=0.3,
            desktop=0.25,
            default=0.3
        )
    
    @classmethod
    def get_content_width_ratio(cls):
        """Get main content width ratio when sidebar is present"""
        if cls.should_use_sidebar():
            return 1.0 - cls.get_sidebar_width_ratio()
        return 1.0
    
    @classmethod
    def get_responsive_height(cls, base_height):
        """Get responsive height based on base height"""
        multiplier = cls.get_responsive_value(
            phone=0.8,
            small_tablet=0.9,
            tablet=1.0,
            large_tablet=1.1,
            desktop=1.2,
            default=1.0
        )
        return base_height * multiplier
    
    @classmethod
    def get_dialog_size(cls, base_width=500, base_height=550):
        """Get responsive dialog size for optimal positioning"""
        from kivy.core.window import Window
        
        category = cls.get_screen_size_category()
        
        if category == cls.PHONE:
            width = min(dp(base_width * 0.95), Window.width * 0.95)
            height = min(dp(base_height), Window.height * 0.85)
        elif category == cls.SMALL_TABLET:
            width = min(dp(base_width * 1.1), Window.width * 0.8)
            height = min(dp(base_height * 1.1), Window.height * 0.75)
        else:  # TABLET, LARGE_TABLET, DESKTOP
            width = min(dp(base_width * 1.4), Window.width * 0.7)
            height = min(dp(base_height * 1.2), Window.height * 0.7)
        
        return width, height


# Responsive Layout Classes
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
        self.spacing = ResponsiveHelper.get_spacing()
        self.padding = ResponsiveHelper.get_padding()
        
        # Switch orientation based on screen size if needed
        if hasattr(self, 'adaptive_orientation') and self.adaptive_orientation:
            if ResponsiveHelper.is_landscape() and ResponsiveHelper.get_screen_size_category() in [ResponsiveHelper.TABLET, ResponsiveHelper.LARGE_TABLET]:
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
        responsive_cols = ResponsiveHelper.get_layout_columns()
        self.cols = min(responsive_cols, self.base_cols)
        
        # Update spacing and padding
        self.spacing = ResponsiveHelper.get_spacing()
        self.padding = ResponsiveHelper.get_padding()


class AdaptiveCardLayout(MDBoxLayout):
    """Adaptive layout that switches between single and multi-column based on screen size"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.adaptive_height = True
        self.spacing = ResponsiveHelper.get_spacing()
        self.padding = ResponsiveHelper.get_padding()
        
        # Create container for cards
        self.card_container = ResponsiveGridLayout(base_cols=2)
        self.add_widget(self.card_container)
        
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, *args):
        """Handle window resize"""
        self.spacing = ResponsiveHelper.get_spacing()
        self.padding = ResponsiveHelper.get_padding()
    
    def add_card(self, card):
        """Add a card to the adaptive layout"""
        self.card_container.add_widget(card)
    
    def clear_cards(self):
        """Clear all cards"""
        self.card_container.clear_widgets()


# Responsive Button Classes
class ResponsiveButton(MDButton):
    """Button that automatically adapts size for responsive use"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_responsive_properties()
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, *args):
        """Handle window resize"""
        self.update_responsive_properties()
    
    def update_responsive_properties(self):
        """Update button properties for responsive optimization"""
        # Set responsive height
        self.size_hint_y = None
        self.height = ResponsiveHelper.get_touch_target_size()
        
        # Set responsive font size
        font_sizes = ResponsiveHelper.get_font_sizes()
        if hasattr(self, 'font_size'):
            self.font_size = font_sizes.get("body", "14sp")


class ResponsiveIconButton(MDButton):
    """Icon button that automatically adapts size for responsive use"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_responsive_properties()
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, *args):
        """Handle window resize"""
        self.update_responsive_properties()
    
    def update_responsive_properties(self):
        """Update icon button properties for responsive optimization"""
        # Set responsive size
        icon_size = ResponsiveHelper.get_icon_size()
        self.size_hint = (None, None)
        self.size = (icon_size * 2, icon_size * 2)
        
        # Set responsive icon size
        if hasattr(self, 'user_font_size'):
            self.user_font_size = f"{icon_size}sp"


class ResponsiveButtonGrid(ResponsiveGridLayout):
    """Grid layout specifically optimized for buttons"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_height = True
        self.size_hint_y = None
        self.height = self.minimum_height
        
    def add_button(self, button_text, callback=None, **button_kwargs):
        """Add a responsive button to the grid"""
        button = ResponsiveButton(
            text=button_text,
            **button_kwargs
        )
        
        if callback:
            button.bind(on_press=callback)
            
        self.add_widget(button)
        return button
    
    def add_icon_button(self, icon, callback=None, **button_kwargs):
        """Add a responsive icon button to the grid"""
        button = ResponsiveIconButton(
            icon=icon,
            **button_kwargs
        )
        
        if callback:
            button.bind(on_press=callback)
            
        self.add_widget(button)
        return button


# Responsive Typography
class ResponsiveLabel(MDLabel):
    """Label that automatically scales typography for responsive use with KivyMD 2.0"""
    
    def __init__(self, base_font_style="Body", base_role="large", **kwargs):
        self.base_font_style = base_font_style
        self.base_role = base_role
        super().__init__(**kwargs)
        self.update_typography()
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, *args):
        """Handle window resize"""
        self.update_typography()
    
    def update_typography(self):
        """Update typography based on screen size using KivyMD 2.0 font styles"""
        category = ResponsiveHelper.get_screen_size_category()
        
        # Font style and role mapping for different screen sizes (KivyMD 2.0)
        style_scaling = {
            ResponsiveHelper.PHONE: {
                ("Display", "large"): ("Display", "medium"),
                ("Display", "medium"): ("Display", "small"),
                ("Display", "small"): ("Headline", "large"),
                ("Headline", "large"): ("Headline", "medium"),
                ("Headline", "medium"): ("Headline", "small"),
                ("Headline", "small"): ("Title", "large"),
                ("Title", "large"): ("Title", "medium"),
                ("Title", "medium"): ("Title", "small"),
                ("Title", "small"): ("Body", "large"),
                ("Body", "large"): ("Body", "medium"),
                ("Body", "medium"): ("Body", "small"),
                ("Body", "small"): ("Label", "small"),
                ("Label", "large"): ("Label", "medium"),
                ("Label", "medium"): ("Label", "small"),
                ("Label", "small"): ("Label", "small")
            },
            ResponsiveHelper.SMALL_TABLET: {
                # Keep original sizes for small tablets
                ("Display", "large"): ("Display", "large"),
                ("Display", "medium"): ("Display", "medium"),
                ("Display", "small"): ("Display", "small"),
                ("Headline", "large"): ("Headline", "large"),
                ("Headline", "medium"): ("Headline", "medium"),
                ("Headline", "small"): ("Headline", "small"),
                ("Title", "large"): ("Title", "large"),
                ("Title", "medium"): ("Title", "medium"),
                ("Title", "small"): ("Title", "small"),
                ("Body", "large"): ("Body", "large"),
                ("Body", "medium"): ("Body", "medium"),
                ("Body", "small"): ("Body", "small"),
                ("Label", "large"): ("Label", "large"),
                ("Label", "medium"): ("Label", "medium"),
                ("Label", "small"): ("Label", "small")
            },
            ResponsiveHelper.TABLET: {
                # Scale up for tablets
                ("Display", "small"): ("Display", "medium"),
                ("Display", "medium"): ("Display", "large"),
                ("Headline", "small"): ("Headline", "medium"),
                ("Headline", "medium"): ("Headline", "large"),
                ("Title", "small"): ("Title", "medium"),
                ("Title", "medium"): ("Title", "large"),
                ("Body", "small"): ("Body", "medium"),
                ("Body", "medium"): ("Body", "large"),
                ("Label", "small"): ("Label", "medium"),
                ("Label", "medium"): ("Label", "large")
            }
        }
        
        # Use tablet scaling for larger screens too
        if category in [ResponsiveHelper.LARGE_TABLET, ResponsiveHelper.DESKTOP]:
            category = ResponsiveHelper.TABLET
        
        scaling = style_scaling.get(category, style_scaling[ResponsiveHelper.SMALL_TABLET])
        style_role_key = (self.base_font_style, self.base_role)
        new_style, new_role = scaling.get(style_role_key, (self.base_font_style, self.base_role))
        
        if hasattr(self, 'font_style'):
            self.font_style = new_style
        if hasattr(self, 'role'):
            self.role = new_role


# Convenience functions for common responsive patterns
def responsive_padding():
    """Get current responsive padding"""
    return ResponsiveHelper.get_padding()

def responsive_spacing():
    """Get current responsive spacing"""
    return ResponsiveHelper.get_spacing()

def responsive_font_size(size_type="body"):
    """Get responsive font size for given type"""
    sizes = ResponsiveHelper.get_font_sizes()
    return sizes.get(size_type, sizes["body"])

def is_mobile():
    """Check if current device is mobile-sized"""
    return ResponsiveHelper.get_screen_size_category() == ResponsiveHelper.PHONE

def is_tablet():
    """Check if current device is tablet-sized"""
    category = ResponsiveHelper.get_screen_size_category()
    return category in [ResponsiveHelper.SMALL_TABLET, ResponsiveHelper.TABLET, ResponsiveHelper.LARGE_TABLET]

def is_desktop():
    """Check if current device is desktop-sized"""
    return ResponsiveHelper.get_screen_size_category() == ResponsiveHelper.DESKTOP

def use_compact_layout():
    """Determine if compact layout should be used"""
    category = ResponsiveHelper.get_screen_size_category()
    return category in [ResponsiveHelper.PHONE, ResponsiveHelper.SMALL_TABLET]


# Responsive Button Creation Helpers
def create_responsive_button(text, style="filled", callback=None, **kwargs):
    """Create a responsive button with KivyMD 2.0.1 style"""
    button = ResponsiveButton(
        style=style,
        **kwargs
    )
    
    # Add button text
    button.add_widget(MDButtonText(text=text))
    
    if callback:
        button.bind(on_press=callback)
    
    return button


def create_responsive_icon_button(icon, text=None, style="filled", callback=None, **kwargs):
    """Create a responsive icon button with KivyMD 2.0.1 style"""
    button = ResponsiveIconButton(
        style=style,
        **kwargs
    )
    
    # Add icon
    button.add_widget(MDButtonIcon(icon=icon))
    
    # Add text if provided
    if text:
        button.add_widget(MDButtonText(text=text))
    
    if callback:
        button.bind(on_press=callback)
    
    return button


def create_responsive_button_row(buttons_config, max_cols=4):
    """Create a responsive row of buttons that adapts to screen size"""
    cols = ResponsiveHelper.get_layout_columns()
    cols = min(cols, max_cols)
    
    # Create grid layout
    button_grid = ResponsiveGridLayout(base_cols=cols)
    button_grid.adaptive_height = True
    button_grid.size_hint_y = None
    button_grid.height = button_grid.minimum_height
    
    # Add buttons
    for config in buttons_config:
        if config.get('icon'):
            button = create_responsive_icon_button(**config)
        else:
            button = create_responsive_button(**config)
        button_grid.add_widget(button)
    
    return button_grid


def create_responsive_action_bar(actions_list):
    """Create a responsive action bar with buttons
    
    Args:
        actions_list: List of dicts with button configuration
    """
    action_bar = ResponsiveButtonGrid(base_cols=len(actions_list))
    action_bar.orientation = 'horizontal'
    action_bar.size_hint_y = None
    action_bar.height = ResponsiveHelper.get_touch_target_size()
    
    for action in actions_list:
        if action.get('icon'):
            button = create_responsive_icon_button(**action)
        else:
            button = create_responsive_button(**action)
        action_bar.add_widget(button)
    
    return action_bar 