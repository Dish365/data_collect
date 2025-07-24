"""
Data Exploration Service for handling data exploration functionality.
"""

import json
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.clock import Clock


class DataExplorationService:
    """Service for handling data exploration operations"""
    
    def __init__(self, analytics_service, screen):
        self.analytics_service = analytics_service
        self.screen = screen
        self.current_data = []
        self.current_page = 1
        self.page_size = 50
        self.total_count = 0
        self.total_pages = 0
        self.current_filters = {}
        self.filter_options = {}
        
    def explore_project_data(self, project_id: str):
        """Main method to start data exploration for a project"""
        if not project_id:
            toast("📊 Please select a project first")
            return
            
        # Get the content area for data exploration
        content = self.screen.get_tab_content('data_exploration')
        if not content:
            toast("❌ Could not access data exploration area")
            return
            
        content.clear_widgets()
        
        # Show loading state
        loading_card = self._create_loading_card()
        content.add_widget(loading_card)
        
        # Load data summary first
        Clock.schedule_once(lambda dt: self._load_data_summary(project_id, content), 0.5)
    
    def _load_data_summary(self, project_id: str, content):
        """Load data summary and then initialize the exploration interface"""
        try:
            # Run the request in a separate thread to avoid async issues
            def make_request():
                try:
                    result = self.analytics_service.get_data_summary(project_id)
                    # Schedule the UI update on the main thread
                    Clock.schedule_once(lambda dt: self._handle_summary_result(project_id, content, result), 0.1)
                except Exception as e:
                    error_result = {'error': f'Request failed: {str(e)}'}
                    Clock.schedule_once(lambda dt: self._handle_summary_result(project_id, content, error_result), 0.1)
            
            # Start the request in a separate thread
            thread = threading.Thread(target=make_request)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self._show_error_state(content, f"Failed to load data summary: {str(e)}")
    
    def _handle_summary_result(self, project_id: str, content, summary_result):
        """Handle the result of the data summary request"""
        try:
            print(f"[DEBUG] _handle_summary_result called with: {summary_result}")
            
            if 'error' in summary_result:
                print(f"[DEBUG] Error in summary result: {summary_result['error']}")
                self._show_error_state(content, summary_result['error'])
                return
            
            # Clear loading state
            content.clear_widgets()
            
            # Create exploration interface
            self._create_exploration_interface(project_id, content, summary_result)
            
        except Exception as e:
            print(f"[DEBUG] Exception in _handle_summary_result: {str(e)}")
            self._show_error_state(content, f"Failed to process data summary: {str(e)}")
    
    def _create_exploration_interface(self, project_id: str, content, summary_result):
        """Create the main data exploration interface"""
        try:
            # Data summary card
            summary_card = self._create_summary_card(summary_result)
            content.add_widget(summary_card)
            
            # Filters card
            filters_card = self._create_filters_card(project_id)
            content.add_widget(filters_card)
            
            # Data table card
            data_card = self._create_data_table_card(project_id)
            content.add_widget(data_card)
            
            # Load initial data
            self._load_data_page(project_id)
            
        except Exception as e:
            self._show_error_state(content, f"Failed to create exploration interface: {str(e)}")
    
    def _create_summary_card(self, summary_result):
        """Create data summary overview card"""
        print(f"[DEBUG] _create_summary_card called with: {summary_result}")
        
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(200),
            padding=dp(20),
            spacing=dp(16),
            md_bg_color=(0.99, 0.98, 1.0, 1),
            elevation=3,
            radius=[16, 16, 16, 16]
        )
        
        # Header
        header = MDLabel(
            text="📊 Data Overview",
            font_style="H5",
            theme_text_color="Primary",
            bold=True,
            size_hint_y=None,
            height=dp(32)
        )
        card.add_widget(header)
        
        # Summary stats grid
        if 'summary' in summary_result:
            summary = summary_result['summary']
            print(f"[DEBUG] Summary data: {summary}")
            
            stats_grid = GridLayout(
                cols=4,
                spacing=dp(16),
                size_hint_y=None,
                height=dp(120)
            )
            
            stats = [
                ("📈 Total Responses", f"{summary.get('total_responses', 0):,}"),
                ("👥 Respondents", f"{summary.get('unique_respondents', 0):,}"),
                ("❓ Questions", f"{summary.get('unique_questions', 0)}"),
                ("✅ Quality Score", f"{summary.get('avg_quality_score', 0):.1f}%")
            ]
            
            for label, value in stats:
                stat_container = MDBoxLayout(
                    orientation="vertical",
                    spacing=dp(4),
                    size_hint_y=None,
                    height=dp(120)
                )
                
                stat_label = MDLabel(
                    text=label,
                    font_style="Caption",
                    theme_text_color="Secondary",
                    halign="center",
                    size_hint_y=None,
                    height=dp(16)
                )
                
                stat_value = MDLabel(
                    text=value,
                    font_style="H6",
                    theme_text_color="Primary",
                    bold=True,
                    halign="center",
                    size_hint_y=None,
                    height=dp(32)
                )
                
                stat_container.add_widget(stat_label)
                stat_container.add_widget(stat_value)
                stats_grid.add_widget(stat_container)
            
            card.add_widget(stats_grid)
        else:
            print(f"[DEBUG] No 'summary' key found in summary_result")
            # Add a message when no summary data is available
            no_data_label = MDLabel(
                text="📭 No data available for this project",
                font_style="Body1",
                theme_text_color="Secondary",
                halign="center"
            )
            card.add_widget(no_data_label)
        
        return card
    
    def _create_filters_card(self, project_id: str):
        """Create filters interface card"""
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(160),
            padding=dp(20),
            spacing=dp(12),
            md_bg_color=(0.99, 0.98, 1.0, 1),
            elevation=3,
            radius=[16, 16, 16, 16]
        )
        
        # Header
        header = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(32)
        )
        
        filter_icon = MDIconButton(
            icon="filter-variant",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            size_hint=(None, None),
            size=(dp(32), dp(32))
        )
        
        filter_label = MDLabel(
            text="🔍 Filter & Search Data",
            font_style="H6",
            theme_text_color="Primary",
            bold=True
        )
        
        header.add_widget(filter_icon)
        header.add_widget(filter_label)
        card.add_widget(header)
        
        # Filters row
        filters_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(48)
        )
        
        # Search field
        self.search_field = MDTextField(
            hint_text="Search responses...",
            size_hint_x=0.4,
            on_text_validate=lambda x: self._apply_filters(project_id)
        )
        filters_row.add_widget(self.search_field)
        
        # Question filter dropdown button
        self.question_filter_btn = MDRaisedButton(
            text="All Questions",
            size_hint_x=0.25,
            on_release=lambda x: self._show_question_filter_menu(project_id)
        )
        filters_row.add_widget(self.question_filter_btn)
        
        # Respondent filter field
        self.respondent_field = MDTextField(
            hint_text="Respondent ID...",
            size_hint_x=0.25,
            on_text_validate=lambda x: self._apply_filters(project_id)
        )
        filters_row.add_widget(self.respondent_field)
        
        # Apply filters button
        apply_btn = MDRaisedButton(
            text="Apply",
            size_hint_x=0.1,
            md_bg_color=(0.2, 0.6, 1.0, 1),
            on_release=lambda x: self._apply_filters(project_id)
        )
        filters_row.add_widget(apply_btn)
        
        card.add_widget(filters_row)
        
        # Action buttons row
        actions_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(40)
        )
        
        clear_btn = MDFlatButton(
            text="Clear Filters",
            theme_text_color="Custom",
            text_color=(0.6, 0.6, 0.6, 1),
            on_release=lambda x: self._clear_filters(project_id)
        )
        actions_row.add_widget(clear_btn)
        
        # Spacer
        actions_row.add_widget(MDLabel())
        
        export_btn = MDFlatButton(
            text="📥 Export Data",
            theme_text_color="Custom",
            text_color=(0.2, 0.6, 1.0, 1),
            on_release=lambda x: self._export_data()
        )
        actions_row.add_widget(export_btn)
        
        card.add_widget(actions_row)
        
        return card
    
    def _create_data_table_card(self, project_id: str):
        """Create data table display card"""
        self.data_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(600),
            padding=dp(20),
            spacing=dp(16),
            md_bg_color=(1, 1, 1, 1),
            elevation=3,
            radius=[16, 16, 16, 16]
        )
        
        # Header
        header_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(32)
        )
        
        table_icon = MDIconButton(
            icon="table",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            size_hint=(None, None),
            size=(dp(32), dp(32))
        )
        
        table_label = MDLabel(
            text="📋 Response Data",
            font_style="H6",
            theme_text_color="Primary",
            bold=True
        )
        
        # Page info label
        self.page_info_label = MDLabel(
            text="",
            font_style="Body2",
            theme_text_color="Secondary",
            halign="right"
        )
        
        header_row.add_widget(table_icon)
        header_row.add_widget(table_label)
        header_row.add_widget(self.page_info_label)
        self.data_card.add_widget(header_row)
        
        # Table container with fixed height
        self.table_container = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(480)  # Fixed height
        )
        self.data_card.add_widget(self.table_container)
        
        # Pagination controls
        pagination_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(48)
        )
        
        self.prev_btn = MDIconButton(
            icon="chevron-left",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            on_release=lambda x: self._load_previous_page(project_id)
        )
        
        self.next_btn = MDIconButton(
            icon="chevron-right", 
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            on_release=lambda x: self._load_next_page(project_id)
        )
        
        pagination_row.add_widget(MDLabel())  # Spacer
        pagination_row.add_widget(self.prev_btn)
        pagination_row.add_widget(self.next_btn)
        pagination_row.add_widget(MDLabel())  # Spacer
        
        self.data_card.add_widget(pagination_row)
        
        return self.data_card
    
    def _load_data_page(self, project_id: str):
        """Load data for current page with current filters"""
        try:
            # Show loading in table
            self.table_container.clear_widgets()
            loading_label = MDLabel(
                text="⏳ Loading data...",
                halign="center",
                theme_text_color="Secondary"
            )
            self.table_container.add_widget(loading_label)
            
            # Prepare filters
            search = self.search_field.text if hasattr(self, 'search_field') and self.search_field.text else None
            respondent_filter = self.respondent_field.text if hasattr(self, 'respondent_field') and self.respondent_field.text else None
            question_filter = self.current_filters.get('question_filter')
            
            # Load data
            Clock.schedule_once(
                lambda dt: self._fetch_and_display_data(
                    project_id, search, question_filter, respondent_filter
                ), 0.5
            )
            
        except Exception as e:
            toast(f"❌ Error loading data: {str(e)}")
    
    def _fetch_and_display_data(self, project_id: str, search: str, question_filter: str, respondent_filter: str):
        """Fetch data from backend and display in table"""
        try:
            # Run the request in a separate thread to avoid async issues
            def make_request():
                try:
                    result = self.analytics_service.explore_project_data(
                        project_id=project_id,
                        page=self.current_page,
                        page_size=self.page_size,
                        search=search,
                        question_filter=question_filter,
                        respondent_filter=respondent_filter
                    )
                    
                    # Schedule the UI update on the main thread
                    Clock.schedule_once(lambda dt: self._handle_data_result(result), 0.1)
                    
                except Exception as e:
                    error_result = {'error': f'Request failed: {str(e)}'}
                    Clock.schedule_once(lambda dt: self._handle_data_result(error_result), 0.1)
            
            # Start the request in a separate thread
            thread = threading.Thread(target=make_request)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self._show_table_error(f"Failed to fetch data: {str(e)}")
    
    def _handle_data_result(self, result):
        """Handle the result of the data fetch request"""
        try:
            if 'error' in result:
                self._show_table_error(result['error'])
                return
            
            # Store results
            self.current_data = result.get('data', [])
            pagination = result.get('pagination', {})
            self.total_count = pagination.get('total_count', 0)
            self.total_pages = pagination.get('total_pages', 0)
            
            # Update filter options
            self.filter_options = result.get('filter_options', {})
            
            # Display data
            self._display_data_table()
            self._update_pagination_controls()
            
        except Exception as e:
            self._show_table_error(f"Failed to process data: {str(e)}")
    
    def _display_data_table(self):
        """Display data in a table format using simple layout"""
        try:
            self.table_container.clear_widgets()
            
            if not self.current_data:
                no_data_label = MDLabel(
                    text="📭 No data found with current filters",
                    halign="center",
                    theme_text_color="Secondary",
                    font_style="Body1"
                )
                self.table_container.add_widget(no_data_label)
                return
            
            # Create table layout with fixed height
            table_layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(2),
                size_hint_y=None,
                height=dp(480),  # Fixed height instead of adaptive
                padding=[dp(8), dp(8), dp(8), dp(8)]
            )
            
            # Header row
            if self.current_data:
                header_card = MDCard(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(48),
                    padding=[dp(12), dp(8), dp(12), dp(8)],
                    md_bg_color=(0.9, 0.9, 0.9, 1),
                    elevation=1
                )
                
                headers = ["Question", "Response", "Respondent", "Date", "Type"]
                for header in headers:
                    label = MDLabel(
                        text=header,
                        font_style="Subtitle2",
                        theme_text_color="Primary",
                        bold=True,
                        size_hint_x=0.2
                    )
                    header_card.add_widget(label)
                
                table_layout.add_widget(header_card)
            
            # Data rows - limit to 20 rows for better performance
            for i, row in enumerate(self.current_data[:20]):
                row_card = MDCard(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(60),
                    padding=[dp(12), dp(8), dp(12), dp(8)],
                    spacing=dp(8),
                    md_bg_color=(1, 1, 1, 1) if i % 2 == 0 else (0.98, 0.98, 0.98, 1),
                    elevation=1
                )
                
                # Question (truncated)
                question_text = str(row.get('question_text', ''))[:30] + "..." if len(str(row.get('question_text', ''))) > 30 else str(row.get('question_text', ''))
                question_label = MDLabel(
                    text=question_text,
                    font_style="Body2",
                    theme_text_color="Primary",
                    size_hint_x=0.2
                )
                row_card.add_widget(question_label)
                
                # Response (truncated)
                response_value = str(row.get('response_value', ''))[:20] + "..." if len(str(row.get('response_value', ''))) > 20 else str(row.get('response_value', ''))
                response_label = MDLabel(
                    text=response_value,
                    font_style="Body2",
                    theme_text_color="Primary",
                    size_hint_x=0.2
                )
                row_card.add_widget(response_label)
                
                # Respondent
                respondent_label = MDLabel(
                    text=str(row.get('respondent_id', ''))[:15],
                    font_style="Body2",
                    theme_text_color="Secondary",
                    size_hint_x=0.2
                )
                row_card.add_widget(respondent_label)
                
                # Date
                date_str = str(row.get('collected_at', ''))[:10] if row.get('collected_at') else ''
                date_label = MDLabel(
                    text=date_str,
                    font_style="Body2",
                    theme_text_color="Secondary",
                    size_hint_x=0.2
                )
                row_card.add_widget(date_label)
                
                # Type
                type_label = MDLabel(
                    text=str(row.get('response_type_name', ''))[:15],
                    font_style="Body2",
                    theme_text_color="Secondary",
                    size_hint_x=0.2
                )
                row_card.add_widget(type_label)
                
                table_layout.add_widget(row_card)
            
            # Add the table layout directly to container (no nested scroll)
            self.table_container.add_widget(table_layout)
            
        except Exception as e:
            self._show_table_error(f"Failed to display table: {str(e)}")
    
    def _update_pagination_controls(self):
        """Update pagination controls and info"""
        try:
            # Update page info
            if hasattr(self, 'page_info_label'):
                if self.total_count > 0:
                    start_record = ((self.current_page - 1) * self.page_size) + 1
                    end_record = min(self.current_page * self.page_size, self.total_count)
                    self.page_info_label.text = f"Showing {start_record}-{end_record} of {self.total_count:,}"
                else:
                    self.page_info_label.text = "No records found"
            
            # Update button states
            if hasattr(self, 'prev_btn'):
                self.prev_btn.disabled = self.current_page <= 1
            if hasattr(self, 'next_btn'):
                self.next_btn.disabled = self.current_page >= self.total_pages
                
        except Exception as e:
            print(f"Error updating pagination: {e}")
    
    def _apply_filters(self, project_id: str):
        """Apply current filters and reload data"""
        self.current_page = 1  # Reset to first page
        self._load_data_page(project_id)
        toast("🔍 Filters applied")
    
    def _clear_filters(self, project_id: str):
        """Clear all filters and reload data"""
        if hasattr(self, 'search_field'):
            self.search_field.text = ""
        if hasattr(self, 'respondent_field'):
            self.respondent_field.text = ""
        if hasattr(self, 'question_filter_btn'):
            self.question_filter_btn.text = "All Questions"
        
        self.current_filters = {}
        self.current_page = 1
        self._load_data_page(project_id)
        toast("🧹 Filters cleared")
    
    def _load_previous_page(self, project_id: str):
        """Load previous page of data"""
        if self.current_page > 1:
            self.current_page -= 1
            self._load_data_page(project_id)
    
    def _load_next_page(self, project_id: str):
        """Load next page of data"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._load_data_page(project_id)
    
    def _show_question_filter_menu(self, project_id: str):
        """Show question filter dropdown menu"""
        if not self.filter_options.get('questions'):
            toast("📋 Loading question options...")
            return
        
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "All Questions",
                "height": dp(56),
                "on_release": lambda x="": self._select_question_filter(project_id, None)
            }
        ]
        
        for question in self.filter_options.get('questions', [])[:10]:  # Limit to 10 for UI
            menu_items.append({
                "viewclass": "OneLineListItem", 
                "text": question[:50] + "..." if len(question) > 50 else question,
                "height": dp(56),
                "on_release": lambda x=question: self._select_question_filter(project_id, x)
            })
        
        self.question_menu = MDDropdownMenu(
            caller=self.question_filter_btn,
            items=menu_items,
            width_mult=4,
            max_height=dp(400)
        )
        self.question_menu.open()
    
    def _select_question_filter(self, project_id: str, question_text: Optional[str]):
        """Select a question filter"""
        if hasattr(self, 'question_menu'):
            self.question_menu.dismiss()
        
        if question_text:
            self.question_filter_btn.text = (question_text[:20] + "...") if len(question_text) > 20 else question_text
            self.current_filters['question_filter'] = question_text
        else:
            self.question_filter_btn.text = "All Questions"
            self.current_filters.pop('question_filter', None)
        
        self._apply_filters(project_id)
    
    def _export_data(self):
        """Export current data (placeholder)"""
        toast("📥 Export functionality coming soon!")
    
    def _create_loading_card(self):
        """Create loading state card"""
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(200),
            padding=dp(40),
            spacing=dp(20),
            md_bg_color=(0.98, 0.98, 0.98, 1),
            elevation=2,
            radius=[16, 16, 16, 16]
        )
        
        loading_label = MDLabel(
            text="🔍 Loading data exploration...",
            font_style="H6",
            theme_text_color="Secondary",
            halign="center"
        )
        
        card.add_widget(loading_label)
        return card
    
    def _show_error_state(self, content, error_message: str):
        """Show error state in content area"""
        content.clear_widgets()
        
        error_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(200),
            padding=dp(40),
            spacing=dp(20),
            md_bg_color=(1.0, 0.95, 0.95, 1),
            elevation=2,
            radius=[16, 16, 16, 16]
        )
        
        error_label = MDLabel(
            text=f"❌ {error_message}",
            font_style="Body1",
            theme_text_color="Error",
            halign="center"
        )
        
        error_card.add_widget(error_label)
        content.add_widget(error_card)
        
        toast(f"❌ {error_message}")
    
    def _show_table_error(self, error_message: str):
        """Show error in table area"""
        self.table_container.clear_widgets()
        
        error_label = MDLabel(
            text=f"❌ {error_message}",
            halign="center",
            theme_text_color="Error",
            font_style="Body1"
        )
        self.table_container.add_widget(error_label)
        toast(f"❌ {error_message}") 