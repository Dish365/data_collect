from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.lang import Builder

# Load the KV file
Builder.load_file("kv/stat_card.kv")


class StatCard(MDCard):
    """Modern statistics card widget using KivyMD 2.0.1 Material Design"""
    
    title = StringProperty("")
    value = StringProperty("0")
    icon = StringProperty("chart-line")
    note = StringProperty("")
    
    def __init__(self, title="", value="0", icon="chart-line", note="", **kwargs):
        # Set properties before calling super().__init__
        self.title = title
        self.value = value
        self.icon = icon
        self.note = note
        
        super().__init__(**kwargs)
        
        # Setup responsive properties
        self.update_responsive_properties()
        
        # Bind to window resize for responsive updates
        Window.bind(on_resize=self._on_window_resize)
    
    def _on_window_resize(self, *args):
        """Handle window resize for responsive updates"""
        self.update_responsive_properties()
    
    def update_responsive_properties(self):
        """Update card properties based on screen size"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            
            category = ResponsiveHelper.get_screen_size_category()
            
            # Responsive card sizing
            height_map = {
                "phone": dp(120),
                "small_tablet": dp(140),
                "tablet": dp(160),
                "large_tablet": dp(180)
            }
            
            self.size_hint_x = 1  # Allow card to expand
            self.size_hint_y = None
            self.height = height_map.get(category, dp(140))
            
        except Exception as e:
            print(f"Error updating StatCard responsive properties: {e}")
            # Fallback to default values
            self.size_hint_x = 1
            self.size_hint_y = None
            self.height = dp(140)
    
    def update_value(self, new_value):
        """Update the displayed value"""
        self.value = str(new_value)
    
    def update_title(self, new_title):
        """Update the displayed title"""
        self.title = new_title
    
    def update_icon(self, new_icon):
        """Update the displayed icon"""
        self.icon = new_icon
        
    def update_note(self, new_note):
        """Update the displayed note"""
        self.note = new_note


class AnimatedStatCard(StatCard):
    """Enhanced stat card with animation capabilities"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_animations()
    
    def setup_animations(self):
        """Setup animation properties"""
        from kivy.animation import Animation
        self.animation = Animation(elevation=4, duration=0.2)
        self.reverse_animation = Animation(elevation=2, duration=0.2)
    
    def on_touch_down(self, touch):
        """Handle touch down with animation"""
        if self.collide_point(*touch.pos):
            self.animation.start(self)
            return True
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        """Handle touch up with animation"""
        if self.collide_point(*touch.pos):
            self.reverse_animation.start(self)
        return super().on_touch_up(touch)


class TrendStatCard(StatCard):
    """Stat card with trend indicator"""
    
    trend = StringProperty("neutral")  # up, down, neutral
    trend_value = StringProperty("")
    
    def __init__(self, trend="neutral", trend_value="", **kwargs):
        self.trend = trend
        self.trend_value = trend_value
        super().__init__(**kwargs)
    
    def get_trend_icon(self):
        """Get icon based on trend"""
        if self.trend == "up":
            return "trending-up"
        elif self.trend == "down":
            return "trending-down"
        else:
            return None
    
    def get_trend_color(self):
        """Get color based on trend"""
        if self.trend == "up":
            return "Custom"  # Green
        elif self.trend == "down":
            return "Custom"  # Red
        else:
            return "Secondary"
