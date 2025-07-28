"""
Qualitative Analytics Handler
Specialized service for qualitative text analysis
"""

from typing import Dict, List, Any, Optional
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivy.metrics import dp
import threading
from kivy.clock import Clock


class QualitativeAnalyticsHandler:
    """Handler for qualitative analytics operations"""
    
    def __init__(self, analytics_service, analytics_screen):
        self.analytics_service = analytics_service
        self.analytics_screen = analytics_screen
    
    def run_text_analysis(self, project_id: str, analysis_config: Dict = None):
        """Run text analysis for a project"""
        print(f"[DEBUG] run_text_analysis called with project_id: {project_id}")
        
        if not project_id:
            print(f"[DEBUG] No project_id provided")
            return
        
        # First show the initial interface
        self._show_initial_qualitative_interface(project_id)
            
        self.analytics_screen.set_loading(True)
        threading.Thread(
            target=self._run_text_analysis_thread,
            args=(project_id, analysis_config),
            daemon=True
        ).start()
    
    def _run_text_analysis_thread(self, project_id: str, analysis_config: Dict):
        """Background thread for text analysis"""
        try:
            results = self.analytics_service.run_analysis(
                project_id, "text", analysis_config
            )
            
            Clock.schedule_once(
                lambda dt: self._display_text_analysis_results(results), 0
            )
        except Exception as e:
            print(f"Error in text analysis: {e}")
            Clock.schedule_once(
                lambda dt: self.analytics_screen.show_error("Text analysis failed"), 0
            )
        finally:
            Clock.schedule_once(
                lambda dt: self.analytics_screen.set_loading(False), 0
            )
    
    def _display_text_analysis_results(self, results):
        """Display text analysis results with fixed-height approach"""
        # Use the helper method to get the content area
        content = self.analytics_screen.get_tab_content('qualitative')
        
        if not content:
            print(f"[DEBUG] ERROR: Could not get qualitative content area")
            return
            
        content.clear_widgets()
        
        print(f"[DEBUG] Text analysis results: {results}")
        
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            if 'Cannot connect to analytics backend' in str(error_msg):
                content.add_widget(self.analytics_screen.create_backend_error_widget())
            else:
                content.add_widget(self._create_error_state_card(f"Text Analysis Error: {error_msg}"))
            return
        
        # Use fixed-height approach 
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.button import MDRaisedButton, MDIconButton
        
        # 1. Overview Card (Fixed Height)
        overview_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(240),  # Fixed height
            padding=dp(20),
            spacing=dp(12),
            md_bg_color=(0.98, 1.0, 0.98, 1),
            elevation=3,
            radius=[16, 16, 16, 16]
        )
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(40)
        )
        
        text_icon = MDIconButton(
            icon="text-box",
            theme_icon_color="Custom",
            icon_color=(0.6, 0.2, 0.8, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(48),
            user_font_size="24sp"
        )
        
        header_label = MDLabel(
            text="📝 Qualitative Text Analysis",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(text_icon)
        header_layout.add_widget(header_label)
        overview_card.add_widget(header_layout)
        
        # Extract overview information
        data_chars = results.get('data_characteristics', {})
        text_vars = data_chars.get('text_variables', [])
        
        # Check for text analysis summary
        text_analysis = results.get('analyses', {}).get('text', {})
        summary = text_analysis.get('summary', {})
        
        overview_text = f"""📝 Text Analysis Overview:

🔤 Text Fields Analyzed: {len(text_vars)}
📋 Total Text Entries: {summary.get('total_text_entries', 'N/A')}
📄 Fields: {', '.join(text_vars[:2])}{'...' if len(text_vars) > 2 else ''}

Status: Analysis completed successfully"""
        
        overview_label = MDLabel(
            text=overview_text,
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(120)
        )
        overview_card.add_widget(overview_label)
        
        # Analysis buttons
        buttons_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(48)
        )
        
        sentiment_btn = MDRaisedButton(
            text="😊 Sentiment Analysis",
            size_hint_x=1,
            height=dp(40),
            md_bg_color=(0.2, 0.8, 0.6, 1),
            font_size="14sp",
            on_release=lambda x: self._show_sentiment_analysis()
        )
        
        themes_btn = MDRaisedButton(
            text="🏷️ Theme Analysis",
            size_hint_x=1,
            height=dp(40),
            md_bg_color=(0.6, 0.2, 0.8, 1),
            font_size="14sp",
            on_release=lambda x: self._show_theme_analysis()
        )
        
        buttons_layout.add_widget(sentiment_btn)
        buttons_layout.add_widget(themes_btn)
        overview_card.add_widget(buttons_layout)
        
        content.add_widget(overview_card)
        
        # 2. Results Card (Fixed Height) - if we have text data
        text_data = None
        if 'analyses' in results and 'text' in results['analyses']:
            text_data = results['analyses']['text']
        elif 'text_analysis' in results:
            text_data = results['text_analysis']
        
        if text_data:
            results_card = self._create_fixed_height_text_results_card(text_data)
            content.add_widget(results_card)
        
        print(f"[DEBUG] Qualitative analytics interface created successfully!")
    
    def _show_initial_qualitative_interface(self, project_id: str):
        """Show initial qualitative analytics interface immediately"""
        print(f"[DEBUG] _show_initial_qualitative_interface called for project: {project_id}")
        
        # Use the helper method to get the content area
        content = self.analytics_screen.get_tab_content('qualitative')
        
        if not content:
            print(f"[DEBUG] ERROR: Could not get qualitative content area")
            return
            
        content.clear_widgets()
        
        # Use fixed-height approach for immediate display
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.button import MDRaisedButton, MDIconButton
        
        # 1. Initial Interface Card (Fixed Height)  
        initial_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(280),  # Fixed height
            padding=dp(20),
            spacing=dp(16),
            md_bg_color=(0.98, 1.0, 0.98, 1),
            elevation=3,
            radius=[16, 16, 16, 16]
        )
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(48)
        )
        
        qual_icon = MDIconButton(
            icon="text-box",
            theme_icon_color="Custom",
            icon_color=(0.6, 0.2, 0.8, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(48),
            user_font_size="24sp"
        )
        
        header_label = MDLabel(
            text="📝 Qualitative Text Analysis",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(qual_icon)
        header_layout.add_widget(header_label)
        initial_card.add_widget(header_layout)
        
        # Status message
        status_text = f"""🔄 Preparing Text Analysis...

📝 Scanning for text data and responses
🔤 Processing qualitative content
🎯 Preparing sentiment and theme analysis

Please wait while we analyze your text data."""
        
        status_label = MDLabel(
            text=status_text,
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(140)
        )
        initial_card.add_widget(status_label)
        
        # Quick action buttons (disabled during loading)
        buttons_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(48)
        )
        
        sentiment_btn = MDRaisedButton(
            text="😊 Sentiment",
            size_hint_x=1,
            height=dp(40),
            md_bg_color=(0.6, 0.6, 0.6, 1),
            font_size="14sp",
            disabled=True
        )
        
        themes_btn = MDRaisedButton(
            text="🏷️ Themes",
            size_hint_x=1,
            height=dp(40),
            md_bg_color=(0.6, 0.6, 0.6, 1),
            font_size="14sp",
            disabled=True
        )
        
        buttons_layout.add_widget(sentiment_btn)
        buttons_layout.add_widget(themes_btn)
        initial_card.add_widget(buttons_layout)
        
        content.add_widget(initial_card)
        print(f"[DEBUG] Initial qualitative interface created successfully!")
    
    def _create_fixed_height_text_results_card(self, text_data):
        """Create fixed-height text results card"""
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.button import MDRaisedButton, MDIconButton
        
        results_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(280),  # Fixed height
            padding=dp(20),
            spacing=dp(12),
            md_bg_color=(1.0, 0.99, 1.0, 1),
            elevation=3,
            radius=[16, 16, 16, 16]
        )
        
        # Header
        header_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(40)
        )
        
        results_icon = MDIconButton(
            icon="chart-donut",
            theme_icon_color="Custom",
            icon_color=(0.8, 0.4, 0.2, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(48),
            user_font_size="24sp"
        )
        
        header_label = MDLabel(
            text="📊 Text Analysis Results",
            font_style="H5",
            theme_text_color="Primary",
            bold=True
        )
        
        header_layout.add_widget(results_icon)
        header_layout.add_widget(header_label)
        results_card.add_widget(header_layout)
        
        # Text analysis summary
        text_analysis = text_data.get('text_analysis', {})
        if text_analysis:
            # Get the first field analysis as example
            first_field = list(text_analysis.keys())[0] if text_analysis else None
            field_data = text_analysis.get(first_field, {}) if first_field else {}
            
            results_text = f"""✅ Text Analysis Complete!

📝 Field Analyzed: {first_field or 'N/A'}
📊 Total Entries: {field_data.get('total_entries', 'N/A')}
📏 Average Length: {field_data.get('average_length', 0):.1f} characters
🔤 Word Count: {field_data.get('word_count', 'N/A')} total words
⭐ Unique Entries: {field_data.get('unique_entries', 'N/A')}"""
        else:
            results_text = "📝 Text analysis data processed\n\nResults ready for detailed review"
        
        results_label = MDLabel(
            text=results_text,
            font_style="Body1",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(140)
        )
        results_card.add_widget(results_label)
        
        # Action buttons
        action_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(48)
        )
        
        view_btn = MDRaisedButton(
            text="📊 View Details",
            size_hint_x=1,
            height=dp(40),
            md_bg_color=(0.6, 0.2, 0.8, 1),
            font_size="14sp",
            on_release=lambda x: self._show_detailed_text_results(text_data)
        )
        
        export_btn = MDRaisedButton(
            text="📤 Export",
            size_hint_x=0.7,
            height=dp(40),
            md_bg_color=(0.6, 0.6, 0.6, 1),
            font_size="14sp",
            on_release=lambda x: self._export_text_results(text_data)
        )
        
        action_layout.add_widget(view_btn)
        action_layout.add_widget(export_btn)
        results_card.add_widget(action_layout)
        
        return results_card
    
    def _create_error_state_card(self, message):
        """Create error state card"""
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        from kivymd.uix.button import MDIconButton
        
        error_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(200),  # Fixed height
            padding=dp(20),
            spacing=dp(16),
            md_bg_color=(1, 0.95, 0.95, 1),
            elevation=2,
            radius=[16, 16, 16, 16]
        )
        
        error_icon = MDIconButton(
            icon="alert-circle",
            theme_icon_color="Custom",
            icon_color=(0.8, 0.2, 0.2, 1),
            disabled=True,
            size_hint_x=None,
            width=dp(64),
            user_font_size="48sp"
        )
        
        error_label = MDLabel(
            text=message,
            font_style="Body1",
            theme_text_color="Custom",
            text_color=(0.8, 0.2, 0.2, 1),
            halign="center",
            size_hint_y=None,
            height=dp(80)
        )
        
        error_card.add_widget(error_icon)
        error_card.add_widget(error_label)
        
        return error_card
    
    def _show_sentiment_analysis(self):
        """Show sentiment analysis"""
        from utils.cross_platform_toast import toast
        toast("Sentiment analysis coming soon!")
    
    def _show_theme_analysis(self):
        """Show theme analysis"""
        from utils.cross_platform_toast import toast
        toast("Theme analysis coming soon!")
    
    def _show_detailed_text_results(self, text_data):
        """Show detailed text results"""
        from utils.cross_platform_toast import toast
        toast("Detailed text results view - coming soon!")
    
    def _export_text_results(self, text_data):
        """Export text results"""
        from utils.cross_platform_toast import toast
        toast("Text analysis export - coming soon!")
    
    def _create_text_overview_card(self, content, results):
        """Create text analysis overview card"""
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(180),
            elevation=2
        )
        
        # Header
        header = MDLabel(
            text="Text Analysis Overview",
            font_style="H6",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(32)
        )
        card.add_widget(header)
        
        # Extract overview information
        data_chars = results.get('data_characteristics', {})
        text_vars = data_chars.get('text_variables', [])
        
        # Check for text analysis summary
        text_analysis = results.get('analyses', {}).get('text', {})
        summary = text_analysis.get('summary', {})
        
        overview_text = f"""Text Fields Analyzed: {len(text_vars)}
Total Text Entries: {summary.get('total_text_entries', 'N/A')}
Fields: {', '.join(text_vars[:3])}{'...' if len(text_vars) > 3 else ''}"""
        
        overview_label = MDLabel(
            text=overview_text,
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(130)
        )
        card.add_widget(overview_label)
        
        content.add_widget(card)
    
    def _create_text_analysis_cards(self, content, text_data):
        """Create individual text analysis cards"""
        text_analysis = text_data.get('text_analysis', {})
        
        if not text_analysis:
            return
        
        for field_name, field_data in text_analysis.items():
            if isinstance(field_data, dict):
                card = self._create_text_field_card(field_name, field_data)
                content.add_widget(card)
    
    def _create_text_field_card(self, field_name: str, field_data: Dict):
        """Create a card for individual text field analysis"""
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(200),
            elevation=2
        )
        
        # Header
        header = MDLabel(
            text=f"Field: {field_name}",
            font_style="H6",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(32)
        )
        card.add_widget(header)
        
        # Text statistics
        stats_text = f"""Total Entries: {field_data.get('total_entries', 'N/A')}
Average Length: {field_data.get('average_length', 'N/A'):.1f} characters
Word Count: {field_data.get('word_count', 'N/A')} total words
Unique Entries: {field_data.get('unique_entries', 'N/A')}"""
        
        stats_label = MDLabel(
            text=stats_text,
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(150)
        )
        card.add_widget(stats_label)
        
        return card
    
    def create_sentiment_analysis_card(self, sentiment_results: Dict):
        """Create sentiment analysis results card"""
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(250),
            elevation=2
        )
        
        # Header
        header = MDLabel(
            text="Sentiment Analysis",
            font_style="H6",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(32)
        )
        card.add_widget(header)
        
        # Sentiment distribution
        sentiment_layout = MDGridLayout(
            cols=3,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(80)
        )
        
        # Create sentiment cards
        sentiments = ['positive', 'neutral', 'negative']
        colors = [(0.2, 0.8, 0.2, 1), (0.5, 0.5, 0.5, 1), (0.8, 0.2, 0.2, 1)]
        
        for sentiment, color in zip(sentiments, colors):
            sentiment_count = sentiment_results.get(f'{sentiment}_count', 0)
            sentiment_card = MDCard(
                orientation="vertical",
                padding=dp(8),
                md_bg_color=color[:3] + (0.2,),  # Lighter version
                elevation=1
            )
            
            sentiment_label = MDLabel(
                text=sentiment.title(),
                font_style="Caption",
                theme_text_color="Custom",
                text_color=color,
                halign="center",
                size_hint_y=None,
                height=dp(20)
            )
            
            count_label = MDLabel(
                text=str(sentiment_count),
                font_style="H6",
                theme_text_color="Custom",
                text_color=color,
                halign="center",
                size_hint_y=None,
                height=dp(30)
            )
            
            sentiment_card.add_widget(sentiment_label)
            sentiment_card.add_widget(count_label)
            sentiment_layout.add_widget(sentiment_card)
        
        card.add_widget(sentiment_layout)
        
        # Overall sentiment summary
        overall_sentiment = sentiment_results.get('overall_sentiment', 'neutral')
        confidence = sentiment_results.get('confidence', 0)
        
        summary_text = f"""Overall Sentiment: {overall_sentiment.title()}
Confidence: {confidence:.2f}
Total Analyzed: {sentiment_results.get('total_analyzed', 0)} responses"""
        
        summary_label = MDLabel(
            text=summary_text,
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(120)
        )
        card.add_widget(summary_label)
        
        return card
    
    def create_theme_analysis_card(self, themes: List[Dict]):
        """Create theme analysis results card"""
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(300),
            elevation=2
        )
        
        # Header
        header = MDLabel(
            text="Theme Analysis",
            font_style="H6",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(32)
        )
        card.add_widget(header)
        
        # Themes list
        themes_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_y=None,
            height=dp(250)
        )
        
        for i, theme in enumerate(themes[:5], 1):  # Show top 5 themes
            theme_card = MDCard(
                orientation="horizontal",
                padding=dp(8),
                spacing=dp(8),
                size_hint_y=None,
                height=dp(40),
                elevation=1
            )
            
            theme_number = MDLabel(
                text=f"{i}.",
                font_style="Subtitle2",
                theme_text_color="Primary",
                size_hint_x=None,
                width=dp(20)
            )
            
            theme_name = MDLabel(
                text=theme.get('name', f'Theme {i}'),
                font_style="Body1",
                theme_text_color="Primary"
            )
            
            theme_frequency = MDLabel(
                text=f"{theme.get('frequency', 0)} mentions",
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_x=None,
                width=dp(100)
            )
            
            theme_card.add_widget(theme_number)
            theme_card.add_widget(theme_name)
            theme_card.add_widget(theme_frequency)
            themes_layout.add_widget(theme_card)
        
        card.add_widget(themes_layout)
        
        return card
    
    def create_word_frequency_card(self, word_frequency: Dict):
        """Create word frequency analysis card"""
        card = MDCard(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(250),
            elevation=2
        )
        
        # Header
        header = MDLabel(
            text="Most Common Words",
            font_style="H6",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(32)
        )
        card.add_widget(header)
        
        # Word frequency list
        words_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_y=None,
            height=dp(200)
        )
        
        # Sort words by frequency and show top 10
        sorted_words = sorted(word_frequency.items(), key=lambda x: x[1], reverse=True)
        
        for word, frequency in sorted_words[:10]:
            word_layout = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(8),
                size_hint_y=None,
                height=dp(20)
            )
            
            word_label = MDLabel(
                text=word,
                font_style="Body2",
                theme_text_color="Primary",
                size_hint_x=0.7
            )
            
            freq_label = MDLabel(
                text=str(frequency),
                font_style="Body2",
                theme_text_color="Secondary",
                size_hint_x=0.3,
                halign="right"
            )
            
            word_layout.add_widget(word_label)
            word_layout.add_widget(freq_label)
            words_layout.add_widget(word_layout)
        
        card.add_widget(words_layout)
        
        return card
    
    def run_sentiment_analysis(self, project_id: str, text_fields: List[str] = None):
        """Run sentiment analysis specifically"""
        analysis_config = {
            'analysis_type': 'sentiment',
            'text_fields': text_fields or []
        }
        
        return self.run_text_analysis(project_id, analysis_config)
    
    def run_theme_analysis(self, project_id: str, text_fields: List[str] = None, num_themes: int = 5):
        """Run theme analysis specifically"""
        analysis_config = {
            'analysis_type': 'themes',
            'text_fields': text_fields or [],
            'num_themes': num_themes
        }
        
        return self.run_text_analysis(project_id, analysis_config) 