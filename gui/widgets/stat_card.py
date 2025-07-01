from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window

# Load the StatCard KV template
Builder.load_file("kv/stat_card.kv")

class StatCard(MDCard):
    """Statistics card widget for displaying analytics data"""
    
    title = StringProperty("")
    value = StringProperty("0")
    icon = StringProperty("chart-line")
    note = StringProperty("")  # Add note property for KV file
    
    def __init__(self, title="", value="0", icon="chart-line", note="", **kwargs):
        # Set properties before calling super().__init__
        self.title = title
        self.value = value
        self.icon = icon
        self.note = note
        
        super().__init__(**kwargs)
        
        # Configure card properties for responsive design
        self.update_responsive_properties()
        
        # Bind to window resize for responsive updates
        Window.bind(on_resize=self._on_window_resize)
        
        # The KV file will handle the layout, so we don't create it here
    
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
            self.elevation = 2
            self.radius = [dp(12)]
            
            print(f"StatCard: Updated height to {self.height} for {category}")
            
        except Exception as e:
            print(f"Error updating StatCard responsive properties: {e}")
            # Fallback to default values
            self.size_hint_x = 1
            self.size_hint_y = None
            self.height = dp(140)
            self.elevation = 2
            self.radius = [dp(12)]
    
    def update_value(self, new_value):
        """Update the displayed value"""
        print(f"StatCard.update_value called: {self.title} -> {new_value}")
        self.value = str(new_value)
    
    def update_title(self, new_title):
        """Update the displayed title"""
        print(f"StatCard.update_title called: {new_title}")
        self.title = new_title
    
    def update_icon(self, new_icon):
        """Update the displayed icon"""
        print(f"StatCard.update_icon called: {new_icon}")
        self.icon = new_icon
        
    def update_note(self, new_note):
        """Update the displayed note"""
        print(f"StatCard.update_note called: {new_note}")
        self.note = new_note

    def update_responsive_height(self, new_height):
        """Update the card height for responsive layout"""
        try:
            self.size_hint_y = None
            self.height = dp(new_height)
            print(f"StatCard: Height updated to {new_height}dp")
        except Exception as e:
            print(f"Error updating StatCard height: {e}")


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
    
    def setup_layout(self):
        """Setup layout with trend indicator"""
        main_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(4)
        )
        
        # Top row with icon and value
        top_row = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(32)
        )
        
        # Icon
        icon_btn = MDIconButton(
            icon=self.icon,
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            pos_hint={'center_y': 0.5},
            theme_icon_color="Primary",
            disabled=True
        )
        top_row.add_widget(icon_btn)
        
        # Value label
        value_label = MDLabel(
            text=self.value,
            font_style="H6",
            theme_text_color="Primary",
            bold=True,
            size_hint_x=1
        )
        top_row.add_widget(value_label)
        
        # Trend indicator
        trend_icon = self.get_trend_icon()
        if trend_icon:
            trend_btn = MDIconButton(
                icon=trend_icon,
                size_hint=(None, None),
                size=(dp(20), dp(20)),
                pos_hint={'center_y': 0.5},
                theme_icon_color=self.get_trend_color(),
                disabled=True
            )
            top_row.add_widget(trend_btn)
        
        # Title and trend row
        bottom_row = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(20)
        )
        
        # Title label
        title_label = MDLabel(
            text=self.title,
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_x=1
        )
        bottom_row.add_widget(title_label)
        
        # Trend value
        if self.trend_value:
            trend_label = MDLabel(
                text=self.trend_value,
                font_style="Caption",
                theme_text_color=self.get_trend_color(),
                size_hint_x=None,
                width=dp(40),
                halign="right"
            )
            bottom_row.add_widget(trend_label)
        
        main_layout.add_widget(top_row)
        main_layout.add_widget(bottom_row)
        
        self.add_widget(main_layout)
    
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
