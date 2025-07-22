"""
Tablet-Optimized Analytics Stat Card Widget
Enhanced stat display for medium tablets (9-11 inches)
"""

from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.progressbar import MDProgressBar
from kivymd.toast import toast
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty


class TabletAnalyticsStatCard(ButtonBehavior, MDCard):
    """
    Enhanced Analytics Stat Card optimized for tablets
    Features: Larger touch targets, better visual hierarchy, animations, interactive elements
    """
    
    # Card properties
    title = StringProperty("")
    value = StringProperty("")
    icon = StringProperty("chart-line")
    note = StringProperty("")
    color = ListProperty([0.2, 0.6, 1.0, 1])
    
    # Enhanced properties for tablets
    trend_value = NumericProperty(0)  # For showing trends (+/- values)
    trend_direction = StringProperty("neutral")  # "up", "down", "neutral"
    progress_value = NumericProperty(0)  # For progress indicators (0-100)
    show_progress = BooleanProperty(False)
    is_interactive = BooleanProperty(True)
    
    # Animation properties
    hover_elevation = NumericProperty(6)
    normal_elevation = NumericProperty(3)
    
    def __init__(self, **kwargs):
        # Set tablet-optimized defaults
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(160))  # Taller for tablets
        kwargs.setdefault('elevation', 3)
        kwargs.setdefault('radius', [12, 12, 12, 12])
        kwargs.setdefault('padding', [dp(20), dp(16), dp(20), dp(16)])
        kwargs.setdefault('spacing', dp(12))
        kwargs.setdefault('md_bg_color', [1, 1, 1, 1])
        
        super().__init__(**kwargs)
        
        # Build tablet-optimized layout
        Clock.schedule_once(self._build_tablet_layout, 0)
        
        # Bind properties for dynamic updates
        self.bind(
            title=self._update_title,
            value=self._update_value,
            icon=self._update_icon,
            note=self._update_note,
            color=self._update_color,
            trend_value=self._update_trend,
            progress_value=self._update_progress
        )
    
    def _build_tablet_layout(self, dt):
        """Build the tablet-optimized card layout"""
        self.clear_widgets()
        
        # Main container
        main_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(12)
        )
        
        # Header section with icon and title
        header_section = self._create_header_section()
        main_layout.add_widget(header_section)
        
        # Value section with enhanced typography
        value_section = self._create_value_section()
        main_layout.add_widget(value_section)
        
        # Progress section (if enabled)
        if self.show_progress:
            progress_section = self._create_progress_section()
            main_layout.add_widget(progress_section)
        
        # Note section with additional info
        note_section = self._create_note_section()
        main_layout.add_widget(note_section)
        
        self.add_widget(main_layout)
    
    def _create_header_section(self):
        """Create the header section with icon and title"""
        header_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(12),
            size_hint_y=None,
            height=dp(40)
        )
        
        # Icon with enhanced styling for tablets
        self.icon_widget = MDIconButton(
            icon=self.icon,
            theme_icon_color="Custom",
            icon_color=self.color,
            disabled=True,
            size_hint_x=None,
            width=dp(40),
            user_font_size="24sp"  # Larger for tablets
        )
        
        # Title with tablet-appropriate typography
        self.title_label = MDLabel(
            text=self.title,
            font_style="H6",  # Larger font for tablets
            theme_text_color="Primary",
            bold=True,
            halign="left",
            valign="center"
        )
        
        header_layout.add_widget(self.icon_widget)
        header_layout.add_widget(self.title_label)
        
        return header_layout
    
    def _create_value_section(self):
        """Create the value section with trend indicators"""
        value_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48)  # Larger for tablet readability
        )
        
        # Main value with enhanced typography
        self.value_label = MDLabel(
            text=self.value,
            font_style="H3",  # Very large for tablets
            theme_text_color="Primary",
            bold=True,
            halign="left",
            valign="center",
            size_hint_x=0.7
        )
        
        # Trend indicator (if applicable)
        self.trend_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(4),
            size_hint_x=0.3
        )
        
        if self.trend_value != 0:
            trend_icon = "trending-up" if self.trend_direction == "up" else "trending-down" if self.trend_direction == "down" else "trending-neutral"
            trend_color = [0.2, 0.8, 0.2, 1] if self.trend_direction == "up" else [0.8, 0.2, 0.2, 1] if self.trend_direction == "down" else [0.6, 0.6, 0.6, 1]
            
            self.trend_icon = MDIconButton(
                icon=trend_icon,
                theme_icon_color="Custom",
                icon_color=trend_color,
                disabled=True,
                size_hint_x=None,
                width=dp(24),
                user_font_size="16sp"
            )
            
            self.trend_label = MDLabel(
                text=f"{'+' if self.trend_value > 0 else ''}{self.trend_value:.1f}%",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=trend_color,
                bold=True,
                halign="left",
                size_hint_y=None,
                height=dp(20)
            )
            
            self.trend_layout.add_widget(self.trend_icon)
            self.trend_layout.add_widget(self.trend_label)
        
        value_layout.add_widget(self.value_label)
        value_layout.add_widget(self.trend_layout)
        
        return value_layout
    
    def _create_progress_section(self):
        """Create optional progress bar section"""
        progress_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(4),
            size_hint_y=None,
            height=dp(20)
        )
        
        self.progress_bar = MDProgressBar(
            value=self.progress_value,
            size_hint_y=None,
            height=dp(4),
            color=self.color
        )
        
        progress_label = MDLabel(
            text=f"{self.progress_value:.0f}% Complete",
            font_style="Caption",
            theme_text_color="Secondary",
            halign="left",
            size_hint_y=None,
            height=dp(16)
        )
        
        progress_layout.add_widget(self.progress_bar)
        progress_layout.add_widget(progress_label)
        
        return progress_layout
    
    def _create_note_section(self):
        """Create the note/description section"""
        self.note_label = MDLabel(
            text=self.note,
            font_style="Body2",  # Readable size for tablets
            theme_text_color="Secondary",
            halign="left",
            size_hint_y=None,
            height=dp(32),  # More space for tablet readability
            text_size=(None, None)
        )
        
        return self.note_label
    
    # Animation and interaction methods
    def on_enter(self):
        """Handle hover/touch enter with tablet-appropriate animation"""
        if not self.is_interactive:
            return
            
        # Elevation animation
        anim = Animation(
            elevation=self.hover_elevation,
            duration=0.2,
            transition='out_cubic'
        )
        anim.start(self)
        
        # Scale animation for better tablet feedback
        scale_anim = Animation(
            size=(self.width * 1.02, self.height * 1.02),
            duration=0.2,
            transition='out_cubic'
        )
        # scale_anim.start(self)  # Commented out to avoid layout issues
    
    def on_leave(self):
        """Handle hover/touch leave"""
        if not self.is_interactive:
            return
            
        # Return to normal elevation
        anim = Animation(
            elevation=self.normal_elevation,
            duration=0.2,
            transition='out_cubic'
        )
        anim.start(self)
    
    def on_release(self):
        """Handle card press with tablet feedback"""
        if not self.is_interactive:
            return
            
        # Ripple effect for tablets
        ripple_anim = Animation(
            md_bg_color=[0.9, 0.9, 0.9, 1],
            duration=0.1
        ) + Animation(
            md_bg_color=[1, 1, 1, 1],
            duration=0.2
        )
        ripple_anim.start(self)
        
        # Provide haptic-like feedback through toast
        toast(f"📊 {self.title}: {self.value}")
        
        # Call any custom callback
        if hasattr(self, 'on_card_press'):
            self.on_card_press()
    
    # Property update methods
    def _update_title(self, instance, value):
        """Update title dynamically"""
        if hasattr(self, 'title_label'):
            self.title_label.text = value
    
    def _update_value(self, instance, value):
        """Update value with animation"""
        if hasattr(self, 'value_label'):
            # Animate value change
            anim = Animation(
                opacity=0,
                duration=0.1
            ) + Animation(
                opacity=1,
                duration=0.1
            )
            
            def update_text(*args):
                self.value_label.text = value
            
            anim.bind(on_complete=lambda *args: update_text())
            anim.start(self.value_label)
    
    def _update_icon(self, instance, value):
        """Update icon dynamically"""
        if hasattr(self, 'icon_widget'):
            self.icon_widget.icon = value
    
    def _update_note(self, instance, value):
        """Update note text"""
        if hasattr(self, 'note_label'):
            self.note_label.text = value
    
    def _update_color(self, instance, value):
        """Update color scheme"""
        if hasattr(self, 'icon_widget'):
            self.icon_widget.icon_color = value
        if hasattr(self, 'progress_bar'):
            self.progress_bar.color = value
    
    def _update_trend(self, instance, value):
        """Update trend indicator"""
        # Rebuild layout to show/hide trend
        Clock.schedule_once(self._build_tablet_layout, 0)
    
    def _update_progress(self, instance, value):
        """Update progress bar value"""
        if hasattr(self, 'progress_bar'):
            # Animate progress change
            anim = Animation(
                value=value,
                duration=0.5,
                transition='out_cubic'
            )
            anim.start(self.progress_bar)


class TabletAnalyticsStatGrid(MDBoxLayout):
    """
    Container for multiple stat cards optimized for tablets
    Handles responsive layout and spacing
    """
    
    def __init__(self, **kwargs):
        kwargs.setdefault('orientation', 'horizontal')
        kwargs.setdefault('spacing', dp(16))  # Tablet-appropriate spacing
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(160))
        
        super().__init__(**kwargs)
        
        self.stat_cards = []
    
    def add_stat_card(self, title, value, icon, note="", color=None, trend_value=0, trend_direction="neutral", **kwargs):
        """Add a stat card to the grid"""
        if color is None:
            color = [0.2, 0.6, 1.0, 1]
        
        card = TabletAnalyticsStatCard(
            title=title,
            value=str(value),
            icon=icon,
            note=note,
            color=color,
            trend_value=trend_value,
            trend_direction=trend_direction,
            **kwargs
        )
        
        self.stat_cards.append(card)
        self.add_widget(card)
        
        return card
    
    def update_stat_card(self, index, **kwargs):
        """Update a specific stat card"""
        if 0 <= index < len(self.stat_cards):
            card = self.stat_cards[index]
            for key, value in kwargs.items():
                if hasattr(card, key):
                    setattr(card, key, value)
    
    def clear_stats(self):
        """Clear all stat cards"""
        self.clear_widgets()
        self.stat_cards.clear()


class TabletAnalyticsMetricCard(MDCard):
    """
    Enhanced metric card for detailed analytics display on tablets
    Features: Charts, comparisons, drill-down capabilities
    """
    
    metric_name = StringProperty("")
    metric_value = StringProperty("")
    metric_unit = StringProperty("")
    comparison_value = StringProperty("")
    comparison_period = StringProperty("vs last period")
    
    def __init__(self, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(200))  # Taller for tablets
        kwargs.setdefault('elevation', 3)
        kwargs.setdefault('radius', [16, 16, 16, 16])
        kwargs.setdefault('padding', [dp(24), dp(20), dp(24), dp(20)])
        kwargs.setdefault('spacing', dp(16))
        kwargs.setdefault('md_bg_color', [1, 1, 1, 1])
        
        super().__init__(**kwargs)
        
        Clock.schedule_once(self._build_metric_layout, 0)
    
    def _build_metric_layout(self, dt):
        """Build the enhanced metric card layout"""
        self.clear_widgets()
        
        # Header with metric name
        header_label = MDLabel(
            text=self.metric_name,
            font_style="H5",
            theme_text_color="Primary",
            bold=True,
            size_hint_y=None,
            height=dp(32)
        )
        self.add_widget(header_label)
        
        # Value section with unit
        value_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48)
        )
        
        value_label = MDLabel(
            text=self.metric_value,
            font_style="H2",  # Very large for tablets
            theme_text_color="Primary",
            bold=True,
            halign="left",
            size_hint_x=None,
            width=dp(120)
        )
        
        unit_label = MDLabel(
            text=self.metric_unit,
            font_style="H6",
            theme_text_color="Secondary",
            halign="left",
            valign="bottom"
        )
        
        value_layout.add_widget(value_label)
        value_layout.add_widget(unit_label)
        self.add_widget(value_layout)
        
        # Comparison section
        if self.comparison_value:
            comparison_layout = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(8),
                size_hint_y=None,
                height=dp(24)
            )
            
            comparison_label = MDLabel(
                text=f"{self.comparison_value} {self.comparison_period}",
                font_style="Caption",
                theme_text_color="Secondary",
                halign="left"
            )
            
            comparison_layout.add_widget(comparison_label)
            self.add_widget(comparison_layout)
        
        # Action section for drill-down
        action_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(32)
        )
        
        drill_down_btn = MDIconButton(
            icon="chevron-right",
            theme_icon_color="Primary",
            size_hint_x=None,
            width=dp(32),
            on_release=lambda x: self._handle_drill_down()
        )
        
        action_layout.add_widget(drill_down_btn)
        self.add_widget(action_layout)
    
    def _handle_drill_down(self):
        """Handle drill-down action"""
        toast(f"📊 Drilling down into {self.metric_name}")
        # Implement drill-down logic here


# Utility functions for tablet analytics widgets
def create_tablet_stat_cards_from_data(data_dict, container):
    """
    Utility function to create stat cards from data dictionary
    Optimized for tablet layout and spacing
    """
    if not isinstance(container, TabletAnalyticsStatGrid):
        container = TabletAnalyticsStatGrid()
    
    # Color scheme for different types of metrics
    color_scheme = {
        'responses': [0.2, 0.6, 1.0, 1],     # Blue
        'questions': [0.2, 0.8, 0.6, 1],     # Green  
        'completion': [1.0, 0.6, 0.2, 1],    # Orange
        'participants': [0.6, 0.2, 0.8, 1],  # Purple
        'quality': [0.8, 0.6, 0.2, 1],       # Gold
        'time': [0.6, 0.8, 0.2, 1]           # Lime
    }
    
    # Icon mapping for different metrics
    icon_mapping = {
        'responses': 'database',
        'questions': 'help-circle',
        'completion': 'chart-line',
        'participants': 'account-group',
        'quality': 'shield-check',
        'time': 'clock'
    }
    
    for key, value in data_dict.items():
        # Determine metric type and styling
        metric_type = 'responses'  # default
        for type_key in color_scheme.keys():
            if type_key.lower() in key.lower():
                metric_type = type_key
                break
        
        # Format the title
        title = key.replace('_', ' ').title()
        
        # Add appropriate emoji prefix
        emoji_map = {
            'responses': '📊',
            'questions': '❓',
            'completion': '📈',
            'participants': '👥',
            'quality': '🛡️',
            'time': '🕒'
        }
        title = f"{emoji_map.get(metric_type, '📊')} {title}"
        
        # Create the card
        container.add_stat_card(
            title=title,
            value=str(value),
            icon=icon_mapping.get(metric_type, 'chart-line'),
            color=color_scheme.get(metric_type, [0.2, 0.6, 1.0, 1]),
            note=f"Current {metric_type}"
        )
    
    return container


def animate_stat_card_values(cards, new_values, duration=0.5):
    """
    Animate stat card value changes for smooth transitions
    Optimized for tablet performance
    """
    for i, (card, new_value) in enumerate(zip(cards, new_values)):
        # Stagger animations for better visual effect
        delay = i * 0.1
        
        def update_card_value(card_ref, value, *args):
            card_ref.value = str(value)
        
        Clock.schedule_once(
            lambda dt, c=card, v=new_value: update_card_value(c, v),
            delay
        )


def create_responsive_stat_layout(window_width):
    """
    Create responsive stat card layout based on tablet orientation
    """
    if window_width < 800:  # Portrait tablet
        return {
            'cols': 2,
            'spacing': dp(12),
            'card_width': dp(160)
        }
    elif window_width < 1200:  # Landscape tablet
        return {
            'cols': 4,
            'spacing': dp(16),
            'card_width': dp(180)
        }
    else:  # Large tablet
        return {
            'cols': 4,
            'spacing': dp(20),
            'card_width': dp(200)
        }