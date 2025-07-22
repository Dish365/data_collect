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
        if not project_id:
            return
            
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
        """Display text analysis results"""
        if not hasattr(self.analytics_screen.ids, 'qualitative_content'):
            return
            
        content = self.analytics_screen.ids.qualitative_content
        content.clear_widgets()
        
        print(f"[DEBUG] Text analysis results: {results}")
        
        if not results or 'error' in results:
            error_msg = results.get('error', 'No results available') if results else 'No results available'
            if 'Cannot connect to analytics backend' in str(error_msg):
                content.add_widget(self.analytics_screen.create_backend_error_widget())
            else:
                content.add_widget(self.analytics_screen.create_empty_state_widget(
                    f"Text Analysis Error: {error_msg}"
                ))
            return
        
        # Extract text analysis data
        text_data = None
        if 'analyses' in results and 'text' in results['analyses']:
            text_data = results['analyses']['text']
        elif 'text_analysis' in results:
            text_data = results['text_analysis']
        
        if text_data:
            self._create_text_overview_card(content, results)
            self._create_text_analysis_cards(content, text_data)
        else:
            content.add_widget(self.analytics_screen.create_empty_state_widget(
                "No text analysis results found"
            ))
    
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