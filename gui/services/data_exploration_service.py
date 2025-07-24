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
        self.project_questions = []
        self.selected_responses = set()
        self.sample_size = 50
        
    def explore_project_data(self, project_id: str):
        """Main method to start data exploration for a project"""
        if not project_id:
            toast("Please select a project first")
            return
            
        # Get the content area for data exploration
        content = self.screen.get_tab_content('data_exploration')
        if not content:
            toast("Could not access data exploration area")
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
            # Create comprehensive layout for researchers
            cards_layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(12),
                size_hint_y=None,
                height=dp(950),  # Increased height for better appearance
                padding=[dp(8), dp(8), dp(8), dp(8)]
            )
            
            # Filters card with real data loading
            filters_card = self._create_filters_card(project_id)
            cards_layout.add_widget(filters_card)
            
            # Response selection and sampling card
            selection_card = self._create_selection_card(project_id)
            cards_layout.add_widget(selection_card)
            
            # Data preview card
            preview_card = self._create_data_preview_card(project_id)
            cards_layout.add_widget(preview_card)
            
            # Add directly to content without nested scroll
            content.add_widget(cards_layout)
            
            # Load initial data with real questions
            self._load_project_questions(project_id)
            self._load_initial_data(project_id)
            
        except Exception as e:
            self._show_error_state(content, f"Failed to create exploration interface: {str(e)}")
    
    
    def _create_filters_card(self, project_id: str):
        """Create modern filters interface card with improved styling and alignment"""
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(160),
            padding=[dp(16), dp(16), dp(16), dp(16)],
            spacing=dp(12),
            md_bg_color=(0.98, 0.99, 1.0, 1),
            elevation=3
        )
        
        # Header with modern styling
        header = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(36)
        )
        
        filter_icon = MDIconButton(
            icon="filter-variant",
            theme_icon_color="Custom",
            icon_color=(0.13, 0.59, 0.95, 1),  # Material Blue
            disabled=True,
            size_hint=(None, None),
            size=(dp(32), dp(32))
        )
        
        filter_label = MDLabel(
            text="Filter & Search Data",
            font_style="H6",
            theme_text_color="Primary",
            bold=True,
            size_hint_y=None,
            height=dp(36)
        )
        
        # Status indicator for active filters
        self.filter_status_label = MDLabel(
            text="",
            font_style="Caption",
            theme_text_color="Secondary",
            halign="right",
            size_hint_y=None,
            height=dp(36)
        )
        
        header.add_widget(filter_icon)
        header.add_widget(filter_label)
        header.add_widget(self.filter_status_label)
        card.add_widget(header)
        
        # Main filters row with better proportions
        filters_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(56),
            padding=[dp(0), dp(4), dp(0), dp(4)]
        )
        
        # Search field with icon and improved styling
        search_container = MDBoxLayout(
            orientation="horizontal",
            size_hint_x=0.35,
            spacing=dp(4)
        )
        
        self.search_field = MDTextField(
            hint_text="Search responses...",
            mode="rectangle",
            size_hint_x=1.0,
            on_text_validate=lambda x: self._apply_filters(project_id),
            line_color_focus=(0.13, 0.59, 0.95, 1),
            line_color_normal=(0.6, 0.6, 0.6, 0.5)
        )
        
        search_icon = MDIconButton(
            icon="magnify",
            theme_icon_color="Custom",
            icon_color=(0.6, 0.6, 0.6, 1),
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            pos_hint={"center_y": 0.5},
            on_release=lambda x: self._apply_filters(project_id)
        )
        
        search_container.add_widget(self.search_field)
        filters_row.add_widget(search_container)
        
        # Question filter dropdown with modern styling
        self.question_filter_btn = MDRaisedButton(
            text="All Questions",
            size_hint_x=0.25,
            md_bg_color=(0.95, 0.97, 1.0, 1),
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1),
            elevation=2,
            icon="chevron-down",
            icon_color=(0.6, 0.6, 0.6, 1),
            on_release=lambda x: self._show_question_filter_menu(project_id)
        )
        filters_row.add_widget(self.question_filter_btn)
        
        # Respondent filter field with improved styling
        self.respondent_field = MDTextField(
            hint_text="Respondent ID...",
            size_hint_x=0.2,
            mode="rectangle",
            on_text_validate=lambda x: self._apply_filters(project_id),
            line_color_focus=(0.13, 0.59, 0.95, 1),
            line_color_normal=(0.6, 0.6, 0.6, 0.5)
        )
        filters_row.add_widget(self.respondent_field)
        
        # Action buttons with modern styling
        buttons_container = MDBoxLayout(
            orientation="horizontal",
            size_hint_x=0.2,
            spacing=dp(8)
        )
        
        # Apply filters button
        apply_btn = MDRaisedButton(
            text="Apply",
            size_hint_x=0.6,
            md_bg_color=(0.13, 0.59, 0.95, 1),  # Material Blue
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            elevation=3,
            icon="filter-check",
            icon_color=(1, 1, 1, 1),
            on_release=lambda x: self._apply_filters(project_id)
        )
        buttons_container.add_widget(apply_btn)
        
        # Clear filters button
        clear_btn = MDIconButton(
            icon="filter-remove",
            theme_icon_color="Custom",
            icon_color=(0.76, 0.76, 0.76, 1),
            size_hint_x=0.4,
            on_release=lambda x: self._clear_filters(project_id)
        )
        buttons_container.add_widget(clear_btn)
        
        filters_row.add_widget(buttons_container)
        card.add_widget(filters_row)
        
        # Filter summary row (shows when filters are active)
        self.filter_summary_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(0),  # Initially hidden
            spacing=dp(8),
            padding=[dp(4), dp(0), dp(4), dp(0)]
        )
        
        self.filter_summary_label = MDLabel(
            text="",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20)
        )
        
        self.filter_summary_row.add_widget(self.filter_summary_label)
        card.add_widget(self.filter_summary_row)
        
        return card
    
    def _create_data_table_card(self, project_id: str):
        """Create data table display card"""
        self.data_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(400),  # Increased height for better appearance
            padding=[dp(8), dp(8), dp(8), dp(8)],
            spacing=dp(6),
            md_bg_color=(1, 1, 1, 1),
            elevation=2
        )
        
        # Header - smaller
        header_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(24)
        )
        
        table_icon = MDIconButton(
            icon="table",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            size_hint=(None, None),
            size=(dp(24), dp(24))
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
        
        # Table container - smaller
        self.table_container = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(280),  # Much smaller height
            padding=[dp(4), dp(4), dp(4), dp(4)]
        )
        self.data_card.add_widget(self.table_container)
        
        # Pagination controls - smaller
        pagination_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(32),  # Smaller height
            padding=[dp(4), dp(4), dp(4), dp(4)]
        )
        
        self.prev_btn = MDIconButton(
            icon="chevron-left",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            on_release=lambda x: self._load_previous_page(project_id)
        )
        
        self.next_btn = MDIconButton(
            icon="chevron-right", 
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            size_hint=(None, None),
            size=(dp(24), dp(24)),
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
            # Show loading in data container
            if hasattr(self, 'data_container'):
                self.data_container.clear_widgets()
                loading_label = MDLabel(
                    text="⏳ Loading data...",
                    halign="center",
                    theme_text_color="Secondary"
                )
                self.data_container.add_widget(loading_label)
            
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
            toast(f"Error loading data: {str(e)}")
    
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
        """Display data with response selection checkboxes"""
        try:
            if not hasattr(self, 'data_container'):
                return
                
            self.data_container.clear_widgets()
            
            if not self.current_data:
                # Simple no data state
                no_data_container = MDBoxLayout(
                    orientation="vertical",
                    spacing=dp(16),
                    size_hint_y=None,
                    height=dp(200),
                    padding=[dp(40), dp(40), dp(40), dp(40)]
                )
                
                no_data_label = MDLabel(
                    text="📭 No data found with current filters",
                    halign="center",
                    theme_text_color="Secondary",
                    font_style="H6"
                )
                
                no_data_hint = MDLabel(
                    text="Try adjusting your search criteria or clearing filters",
                    halign="center",
                    theme_text_color="Hint",
                    font_style="Body2"
                )
                
                no_data_container.add_widget(no_data_label)
                no_data_container.add_widget(no_data_hint)
                self.data_container.add_widget(no_data_container)
                return
            
            # Create table layout with selection
            table_layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(2),
                size_hint_y=None,
                height=dp(280),
                padding=[dp(2), dp(2), dp(2), dp(2)]
            )
            
            # Header row with checkbox
            if self.current_data:
                header_row = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(32),
                    padding=[dp(8), dp(4), dp(8), dp(4)],
                    spacing=dp(4)
                )
                
                # Select all checkbox
                from kivymd.uix.selectioncontrol import MDCheckbox
                select_all_checkbox = MDCheckbox(
                    size_hint=(None, None),
                    size=(dp(20), dp(20)),
                    active=False,
                    on_active=lambda checkbox, active: self._toggle_page_selection(active)
                )
                header_row.add_widget(select_all_checkbox)
                
                headers = [
                    ("📋 Question", 0.28),
                    ("💬 Response", 0.23), 
                    ("👤 Respondent", 0.18),
                    ("📅 Date", 0.15),
                    ("🏷️ Type", 0.08),
                    ("ID", 0.08)
                ]
                
                for header_text, width in headers:
                    header_label = MDLabel(
                        text=header_text,
                        font_style="Subtitle2",
                        theme_text_color="Primary",
                        bold=True,
                        halign="left",
                        size_hint_x=width
                    )
                    header_row.add_widget(header_label)
                
                table_layout.add_widget(header_row)
            
            # Data rows with selection checkboxes
            for i, row in enumerate(self.current_data[:12]):  # Show fewer for better UI
                response_id = str(row.get('response_id', ''))
                
                row_layout = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(36),
                    padding=[dp(8), dp(2), dp(8), dp(2)],
                    spacing=dp(4)
                )
                
                # Selection checkbox
                from kivymd.uix.selectioncontrol import MDCheckbox
                checkbox = MDCheckbox(
                    size_hint=(None, None),
                    size=(dp(20), dp(20)),
                    active=response_id in self.selected_responses,
                    on_active=lambda checkbox, active, resp_id=response_id: self._toggle_response_selection(resp_id, active)
                )
                row_layout.add_widget(checkbox)
                
                # Question
                question_text = str(row.get('question_text', ''))
                question_display = (question_text[:25] + "...") if len(question_text) > 25 else question_text
                question_label = MDLabel(
                    text=question_display,
                    font_style="Body2",
                    theme_text_color="Primary",
                    size_hint_x=0.28,
                    halign="left"
                )
                row_layout.add_widget(question_label)
                
                # Response
                response_value = str(row.get('response_value', ''))
                response_display = (response_value[:18] + "...") if len(response_value) > 18 else response_value
                response_label = MDLabel(
                    text=response_display,
                    font_style="Body2",
                    theme_text_color="Primary",
                    size_hint_x=0.23,
                    halign="left"
                )
                row_layout.add_widget(response_label)
                
                # Respondent
                respondent_text = str(row.get('respondent_id', ''))[:10]
                respondent_label = MDLabel(
                    text=respondent_text,
                    font_style="Body2",
                    theme_text_color="Secondary",
                    size_hint_x=0.18,
                    halign="left"
                )
                row_layout.add_widget(respondent_label)
                
                # Date
                date_str = str(row.get('collected_at', ''))[:10] if row.get('collected_at') else 'N/A'
                date_label = MDLabel(
                    text=date_str,
                    font_style="Caption",
                    theme_text_color="Secondary",
                    size_hint_x=0.15,
                    halign="center"
                )
                row_layout.add_widget(date_label)
                
                # Type
                type_text = str(row.get('response_type_name', ''))[:6]
                type_label = MDLabel(
                    text=type_text,
                    font_style="Caption",
                    theme_text_color="Secondary",
                    size_hint_x=0.08,
                    halign="center"
                )
                row_layout.add_widget(type_label)
                
                # Response ID (short)
                id_display = response_id[:6] if response_id else 'N/A'
                id_label = MDLabel(
                    text=id_display,
                    font_style="Caption",
                    theme_text_color="Hint",
                    size_hint_x=0.08,
                    halign="center"
                )
                row_layout.add_widget(id_label)
                
                table_layout.add_widget(row_layout)
            
            # Add the table layout to container
            self.data_container.add_widget(table_layout)
            
            # Update selection info
            self._update_selection_info()
            
        except Exception as e:
            self._show_data_error(f"Failed to display data: {str(e)}")
    
    def _update_pagination_controls(self):
        """Update pagination controls and info"""
        try:
            # Update page info
            if hasattr(self, 'preview_info_label'):
                if self.total_count > 0:
                    start_record = ((self.current_page - 1) * self.page_size) + 1
                    end_record = min(self.current_page * self.page_size, self.total_count)
                    self.preview_info_label.text = f"Page {self.current_page}/{self.total_pages} • {start_record}-{end_record} of {self.total_count:,}"
                else:
                    self.preview_info_label.text = "No records found"
            
            # Update button states
            if hasattr(self, 'prev_btn'):
                self.prev_btn.disabled = self.current_page <= 1
            if hasattr(self, 'next_btn'):
                self.next_btn.disabled = self.current_page >= self.total_pages
                
        except Exception as e:
            print(f"Error updating pagination: {e}")
    
    def _toggle_response_selection(self, response_id: str, active: bool):
        """Toggle selection of individual response"""
        if active:
            self.selected_responses.add(response_id)
        else:
            self.selected_responses.discard(response_id)
        
        self._update_selection_info()
    
    def _toggle_page_selection(self, active: bool):
        """Toggle selection of all responses on current page"""
        for row in self.current_data[:12]:
            response_id = str(row.get('response_id', ''))
            if response_id:
                if active:
                    self.selected_responses.add(response_id)
                else:
                    self.selected_responses.discard(response_id)
        
        self._update_selection_info()
        # Refresh display to update checkboxes
        self._display_data_table()
    
    def _update_selection_info(self):
        """Update the selection information label"""
        if hasattr(self, 'selection_info_label'):
            count = len(self.selected_responses)
            if count == 0:
                self.selection_info_label.text = "No responses selected"
            elif count == 1:
                self.selection_info_label.text = "1 response selected"
            else:
                self.selection_info_label.text = f"{count:,} responses selected"
    
    def _sample_random(self, project_id: str):
        """Select random sample of responses"""
        try:
            sample_size = int(self.sample_size_field.text) if self.sample_size_field.text else 50
            self.sample_size = min(sample_size, 500)  # Max 500 for performance
            
            # Clear current selection
            self.selected_responses.clear()
            
            # Load enough data to sample from
            def make_request():
                try:
                    result = self.analytics_service.explore_project_data(
                        project_id=project_id,
                        page=1,
                        page_size=min(self.sample_size * 3, 500),  # Get more than needed
                        search=self.search_field.text if hasattr(self, 'search_field') and self.search_field.text else None,
                        question_filter=self.current_filters.get('question_filter'),
                        respondent_filter=self.respondent_field.text if hasattr(self, 'respondent_field') and self.respondent_field.text else None
                    )
                    Clock.schedule_once(lambda dt: self._handle_sampling_result(result, 'random'), 0.1)
                except Exception as e:
                    Clock.schedule_once(lambda dt: toast(f"Sampling failed: {str(e)}"), 0.1)
            
            thread = threading.Thread(target=make_request)
            thread.daemon = True
            thread.start()
            
        except ValueError:
            toast("Please enter a valid sample size")
    
    def _handle_sampling_result(self, result, sample_type: str):
        """Handle the result of sampling request"""
        try:
            if 'error' not in result and 'data' in result:
                data = result.get('data', [])
                sample_size = min(self.sample_size, len(data))
                
                if sample_type == 'random':
                    import random
                    sampled_data = random.sample(data, sample_size) if len(data) >= sample_size else data
                elif sample_type == 'first':
                    sampled_data = data[:sample_size]
                elif sample_type == 'latest':
                    sampled_data = data[:sample_size]  # Already sorted by date DESC
                elif sample_type == 'quality':
                    # Sort by quality score if available
                    quality_data = [d for d in data if d.get('data_quality_score', 0) >= 80]
                    sampled_data = quality_data[:sample_size] if quality_data else data[:sample_size]
                else:
                    sampled_data = data[:sample_size]
                
                # Select the sampled responses
                self.selected_responses.clear()
                for row in sampled_data:
                    response_id = str(row.get('response_id', ''))
                    if response_id:
                        self.selected_responses.add(response_id)
                
                # Update UI
                self._update_selection_info()
                if hasattr(self, 'data_container'):
                    self._display_data_table()
                
                toast(f"Selected {len(self.selected_responses)} responses ({sample_type} sampling)")
            else:
                toast("Failed to load data for sampling")
        except Exception as e:
            toast(f"Sampling error: {str(e)}")
    
    def _sample_first_n(self, project_id: str):
        """Select first N responses"""
        try:
            sample_size = int(self.sample_size_field.text) if self.sample_size_field.text else 50
            self.sample_size = min(sample_size, 500)
            
            def make_request():
                try:
                    result = self.analytics_service.explore_project_data(
                        project_id=project_id,
                        page=1,
                        page_size=self.sample_size,
                        search=self.search_field.text if hasattr(self, 'search_field') and self.search_field.text else None,
                        question_filter=self.current_filters.get('question_filter'),
                        respondent_filter=self.respondent_field.text if hasattr(self, 'respondent_field') and self.respondent_field.text else None
                    )
                    Clock.schedule_once(lambda dt: self._handle_sampling_result(result, 'first'), 0.1)
                except Exception as e:
                    Clock.schedule_once(lambda dt: toast(f"Sampling failed: {str(e)}"), 0.1)
            
            thread = threading.Thread(target=make_request)
            thread.daemon = True
            thread.start()
            
        except ValueError:
            toast("Please enter a valid sample size")
    
    def _sample_latest_n(self, project_id: str):
        """Select latest N responses"""
        self._sample_first_n(project_id)  # Same as first N since data is sorted by date DESC
    
    def _sample_high_quality(self, project_id: str):
        """Select high quality responses only"""
        try:
            sample_size = int(self.sample_size_field.text) if self.sample_size_field.text else 50
            self.sample_size = min(sample_size, 500)
            
            def make_request():
                try:
                    result = self.analytics_service.explore_project_data(
                        project_id=project_id,
                        page=1,
                        page_size=min(self.sample_size * 2, 500),  # Get more to filter by quality
                        search=self.search_field.text if hasattr(self, 'search_field') and self.search_field.text else None,
                        question_filter=self.current_filters.get('question_filter'),
                        respondent_filter=self.respondent_field.text if hasattr(self, 'respondent_field') and self.respondent_field.text else None
                    )
                    Clock.schedule_once(lambda dt: self._handle_sampling_result(result, 'quality'), 0.1)
                except Exception as e:
                    Clock.schedule_once(lambda dt: toast(f"Sampling failed: {str(e)}"), 0.1)
            
            thread = threading.Thread(target=make_request)
            thread.daemon = True  
            thread.start()
            
        except ValueError:
            toast("Please enter a valid sample size")
    
    def _select_all_responses(self, project_id: str):
        """Select all responses with current filters"""
        toast("Loading all responses for selection...")
        
        def make_request():
            try:
                # Get all responses with current filters
                result = self.analytics_service.explore_project_data(
                    project_id=project_id,
                    page=1,
                    page_size=500,  # Max for performance
                    search=self.search_field.text if hasattr(self, 'search_field') and self.search_field.text else None,
                    question_filter=self.current_filters.get('question_filter'),
                    respondent_filter=self.respondent_field.text if hasattr(self, 'respondent_field') and self.respondent_field.text else None
                )
                Clock.schedule_once(lambda dt: self._handle_select_all_result(result), 0.1)
            except Exception as e:
                                    Clock.schedule_once(lambda dt: toast(f"Failed to load all responses: {str(e)}"), 0.1)
        
        thread = threading.Thread(target=make_request)
        thread.daemon = True
        thread.start()
    
    def _handle_select_all_result(self, result):
        """Handle the result of select all request"""
        try:
            if 'error' not in result and 'data' in result:
                data = result.get('data', [])
                self.selected_responses.clear()
                
                for row in data:
                    response_id = str(row.get('response_id', ''))
                    if response_id:
                        self.selected_responses.add(response_id)
                
                self._update_selection_info()
                if hasattr(self, 'data_container'):
                    self._display_data_table()
                
                toast(f"Selected {len(self.selected_responses)} responses")
            else:
                toast("Failed to select all responses")
        except Exception as e:
            toast(f"Selection error: {str(e)}")
    
    def _clear_selection(self):
        """Clear all selected responses"""
        self.selected_responses.clear()
        self._update_selection_info()
        if hasattr(self, 'data_container'):
            self._display_data_table()
        toast("Selection cleared")
    
    def _export_selected_responses(self):
        """Export selected responses"""
        if not self.selected_responses:
            toast("No responses selected for export")
            return
        
        toast(f"📤 Exporting {len(self.selected_responses)} selected responses...")
        # TODO: Implement actual export functionality
    
    def _show_data_error(self, error_message: str):
        """Show error in data container"""
        if hasattr(self, 'data_container'):
            self.data_container.clear_widgets()
            
            error_container = MDBoxLayout(
                orientation="vertical",
                spacing=dp(16),
                size_hint_y=None,
                height=dp(200),
                padding=[dp(40), dp(40), dp(40), dp(40)]
            )
            
            error_label = MDLabel(
                text=f"❌ {error_message}",
                halign="center",
                theme_text_color="Error",
                font_style="Body1"
            )
            
            error_container.add_widget(error_label)
            self.data_container.add_widget(error_container)
        
        toast(f"{error_message}")
    
    def _apply_filters(self, project_id: str):
        """Apply current filters and reload data with visual feedback"""
        # Get current filter values
        search = self.search_field.text if hasattr(self, 'search_field') and self.search_field.text else None
        respondent_filter = self.respondent_field.text if hasattr(self, 'respondent_field') and self.respondent_field.text else None
        question_filter = self.current_filters.get('question_filter')
        
        # Build filter summary for UI
        filters_applied = []
        if search:
            filters_applied.append(f"Search: '{search[:15]}{'...' if len(search) > 15 else ''}'")
        if respondent_filter:
            filters_applied.append(f"Respondent: '{respondent_filter}'")
        if question_filter:
            filters_applied.append(f"Question: '{question_filter[:20]}{'...' if len(question_filter) > 20 else ''}'")
        
        # Update filter status indicators
        self._update_filter_status(filters_applied)
        
        # Reset to first page and reload data
        self.current_page = 1
        self._load_data_page(project_id)
        
        # Show user-friendly toast message
        if filters_applied:
            filter_count = len(filters_applied)
            toast(f"Applied {filter_count} filter{'s' if filter_count > 1 else ''}")
        else:
            toast("Loading all data")
    
    def _clear_filters(self, project_id: str):
        """Clear all filters and reload data with visual feedback"""
        # Clear all filter input fields
        if hasattr(self, 'search_field'):
            self.search_field.text = ""
        if hasattr(self, 'respondent_field'):
            self.respondent_field.text = ""
        if hasattr(self, 'question_filter_btn'):
            self.question_filter_btn.text = "All Questions"
        
        # Clear internal filter state
        self.current_filters = {}
        
        # Update visual indicators
        self._update_filter_status([])
        
        # Reset to first page and reload data
        self.current_page = 1
        self._load_data_page(project_id)
        
        # Show confirmation message
        toast("All filters cleared")
    
    def _update_filter_status(self, filters_applied: list):
        """Update visual indicators for active filters"""
        try:
            # Update status label in header
            if hasattr(self, 'filter_status_label'):
                if filters_applied:
                    self.filter_status_label.text = f"{len(filters_applied)} active"
                    self.filter_status_label.theme_text_color = "Custom"
                    self.filter_status_label.text_color = (0.13, 0.59, 0.95, 1)  # Material Blue
                else:
                    self.filter_status_label.text = ""
            
            # Update summary row
            if hasattr(self, 'filter_summary_row') and hasattr(self, 'filter_summary_label'):
                if filters_applied:
                    # Show summary row
                    self.filter_summary_row.height = dp(24)
                    self.filter_summary_label.text = "Active filters: " + " • ".join(filters_applied)
                else:
                    # Hide summary row
                    self.filter_summary_row.height = dp(0)
                    self.filter_summary_label.text = ""
                    
        except Exception as e:
            print(f"[DEBUG] Error updating filter status: {str(e)}")
    
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
        """Show modern question filter dropdown menu with improved styling"""
        if not self.project_questions:
            toast("Loading questions...")
            self._load_project_questions(project_id)
            return
        
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "All Questions",
                "height": dp(48),
                "theme_text_color": "Custom",
                "text_color": (0.2, 0.2, 0.2, 1),
                "on_release": lambda x="": self._select_question_filter(project_id, None)
            }
        ]
        
        # Add separator
        menu_items.append({
            "viewclass": "OneLineListItem",
            "text": "─" * 50,
            "height": dp(1),
            "disabled": True
        })
        
        # Show all loaded questions with better formatting
        for i, question in enumerate(self.project_questions[:20]):  # Limit for performance
            display_text = question[:55] + "..." if len(question) > 55 else question
            menu_items.append({
                "viewclass": "OneLineListItem", 
                "text": f"  {display_text}",
                "height": dp(44),
                "theme_text_color": "Custom",
                "text_color": (0.3, 0.3, 0.3, 1),
                "on_release": lambda x=question: self._select_question_filter(project_id, x)
            })
        
        # Show count of available questions if there are more
        if len(self.project_questions) > 20:
            menu_items.append({
                "viewclass": "OneLineListItem",
                "text": f"  ... and {len(self.project_questions) - 20} more questions",
                "height": dp(36),
                "theme_text_color": "Custom", 
                "text_color": (0.6, 0.6, 0.6, 1),
                "on_release": lambda x="": None,
                "disabled": True
            })
        elif len(self.project_questions) > 1:
            menu_items.append({
                "viewclass": "OneLineListItem",
                "text": f"  Total: {len(self.project_questions)} questions",
                "height": dp(32),
                "theme_text_color": "Custom",
                "text_color": (0.6, 0.6, 0.6, 1),
                "on_release": lambda x="": None,
                "disabled": True
            })
        
        self.question_menu = MDDropdownMenu(
            caller=self.question_filter_btn,
            items=menu_items,
            width_mult=6,
            max_height=dp(400),
            elevation=4
        )
        self.question_menu.open()
    
    def _select_question_filter(self, project_id: str, question_text: Optional[str]):
        """Select a question filter with improved visual feedback"""
        if hasattr(self, 'question_menu'):
            self.question_menu.dismiss()
        
        if question_text:
            # Set button text with truncation for better UI
            display_text = (question_text[:18] + "...") if len(question_text) > 18 else question_text
            self.question_filter_btn.text = display_text
            self.question_filter_btn.md_bg_color = (0.90, 0.95, 1.0, 1)  # Slightly blue tint when active
            self.current_filters['question_filter'] = question_text
        else:
            self.question_filter_btn.text = "All Questions"
            self.question_filter_btn.md_bg_color = (0.95, 0.97, 1.0, 1)  # Reset to normal color
            self.current_filters.pop('question_filter', None)
        
        # Apply filters with updated UI
        self._apply_filters(project_id)
    
    def _export_data(self):
        """Export current data (placeholder)"""
        if self.selected_responses:
            toast(f"📥 Exporting {len(self.selected_responses)} selected responses...")
        else:
            toast("📥 Export functionality coming soon!")
    
    def _load_project_questions(self, project_id: str):
        """Load actual questions from the project"""
        try:
            def make_request():
                try:
                    # Use the same endpoint to get filter options
                    result = self.analytics_service.explore_project_data(
                        project_id=project_id,
                        page=1,
                        page_size=1  # Just need filter options
                    )
                    Clock.schedule_once(lambda dt: self._handle_questions_result(result), 0.1)
                except Exception as e:
                    Clock.schedule_once(lambda dt: toast(f"Failed to load questions: {str(e)}"), 0.1)
            
            thread = threading.Thread(target=make_request)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            toast(f"Error loading questions: {str(e)}")
    
    def _handle_questions_result(self, result):
        """Handle the result of questions loading"""
        try:
            if 'error' not in result and 'data' in result:
                filter_options = result.get('filter_options', {})
                self.project_questions = filter_options.get('questions', [])
                toast(f"Loaded {len(self.project_questions)} questions")
            else:
                toast("Failed to load project questions")
        except Exception as e:
            toast(f"Error processing questions: {str(e)}")
    
    def _create_selection_card(self, project_id: str):
        """Create response selection and sampling card"""
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(140),
            padding=[dp(12), dp(12), dp(12), dp(12)],
            spacing=dp(8),
            md_bg_color=(0.98, 1.0, 0.98, 1),
            elevation=2
        )
        
        # Header
        header = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(48)
        )
        
        header_icon = MDIconButton(
            icon="checkbox-multiple-marked",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.7, 0.2, 1),
            disabled=True,
            size_hint=(None, None),
            size=(dp(28), dp(28))
        )
        
        header_label = MDLabel(
            text="🎯 Response Selection & Sampling",
            font_style="H6",
            theme_text_color="Primary",
            bold=True
        )
        
        header.add_widget(header_icon)
        header.add_widget(header_label)
        card.add_widget(header)
        
        # Selection controls row
        controls_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(40),
            padding=[dp(4), dp(4), dp(4), dp(4)]
        )
        
        # Sample size field
        self.sample_size_field = MDTextField(
            hint_text="Sample size",
            text=str(self.sample_size),
            size_hint_x=0.15,
            mode="rectangle",
            input_filter="int"
        )
        controls_row.add_widget(self.sample_size_field)
        
        # Sample random button
        sample_random_btn = MDRaisedButton(
            text="Random Sample",
            size_hint_x=0.2,
            md_bg_color=(0.2, 0.7, 0.2, 1),
            on_release=lambda x: self._sample_random(project_id)
        )
        controls_row.add_widget(sample_random_btn)
        
        # Select all button
        select_all_btn = MDRaisedButton(
            text="Select All",
            size_hint_x=0.15,
            md_bg_color=(0.2, 0.6, 1.0, 1),
            on_release=lambda x: self._select_all_responses(project_id)
        )
        controls_row.add_widget(select_all_btn)
        
        # Clear selection button
        clear_btn = MDFlatButton(
            text="Clear",
            size_hint_x=0.1,
            theme_text_color="Custom",
            text_color=(0.6, 0.6, 0.6, 1),
            on_release=lambda x: self._clear_selection()
        )
        controls_row.add_widget(clear_btn)
        
        # Selection info label
        self.selection_info_label = MDLabel(
            text="No responses selected",
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_x=0.4,
            halign="right"
        )
        controls_row.add_widget(self.selection_info_label)
        
        card.add_widget(controls_row)
        
        # Advanced sampling row
        advanced_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(32),
            padding=[dp(4), dp(4), dp(4), dp(4)]
        )
        
        # First N responses
        first_n_btn = MDFlatButton(
            text="First N",
            size_hint_x=0.12,
            theme_text_color="Custom",
            text_color=(0.2, 0.6, 1.0, 1),
            on_release=lambda x: self._sample_first_n(project_id)
        )
        advanced_row.add_widget(first_n_btn)
        
        # Latest N responses
        latest_n_btn = MDFlatButton(
            text="Latest N",
            size_hint_x=0.12,
            theme_text_color="Custom", 
            text_color=(0.2, 0.6, 1.0, 1),
            on_release=lambda x: self._sample_latest_n(project_id)
        )
        advanced_row.add_widget(latest_n_btn)
        
        # High quality only
        quality_btn = MDFlatButton(
            text="High Quality",
            size_hint_x=0.15,
            theme_text_color="Custom",
            text_color=(0.2, 0.6, 1.0, 1),
            on_release=lambda x: self._sample_high_quality(project_id)
        )
        advanced_row.add_widget(quality_btn)
        
        # Spacer and export button
        advanced_row.add_widget(MDLabel(size_hint_x=0.41))
        
        export_selected_btn = MDRaisedButton(
            text="Export Selected",
            size_hint_x=0.2,
            md_bg_color=(0.8, 0.4, 0.2, 1),
            on_release=lambda x: self._export_selected_responses()
        )
        advanced_row.add_widget(export_selected_btn)
        
        card.add_widget(advanced_row)
        
        return card
    
    def _create_data_preview_card(self, project_id: str):
        """Create data preview card with response selection"""
        self.preview_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(600),
            padding=[dp(12), dp(12), dp(12), dp(12)],
            spacing=dp(8),
            md_bg_color=(1, 1, 1, 1),
            elevation=2
        )
        
        # Header
        header_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(28)
        )
        
        preview_icon = MDIconButton(
            icon="table-eye",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            size_hint=(None, None),
            size=(dp(28), dp(28))
        )
        
        preview_label = MDLabel(
            text="📋 Data Preview & Selection",
            font_style="H6",
            theme_text_color="Primary",
            bold=True
        )
        
        # Status info
        self.preview_info_label = MDLabel(
            text="",
            font_style="Body2",
            theme_text_color="Secondary",
            halign="right"
        )
        
        header_row.add_widget(preview_icon)
        header_row.add_widget(preview_label)
        header_row.add_widget(self.preview_info_label)
        self.preview_card.add_widget(header_row)
        
        # Data container
        self.data_container = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(500),
            padding=[dp(4), dp(4), dp(4), dp(4)]
        )
        self.preview_card.add_widget(self.data_container)
        
        # Pagination controls
        pagination_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(32),
            padding=[dp(4), dp(4), dp(4), dp(4)]
        )
        
        self.prev_btn = MDIconButton(
            icon="chevron-left",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            size_hint=(None, None),
            size=(dp(28), dp(28)),
            on_release=lambda x: self._load_previous_page(project_id)
        )
        
        self.next_btn = MDIconButton(
            icon="chevron-right",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            size_hint=(None, None),
            size=(dp(28), dp(28)),
            on_release=lambda x: self._load_next_page(project_id)
        )
        
        pagination_row.add_widget(MDLabel())  # Spacer
        pagination_row.add_widget(self.prev_btn)
        pagination_row.add_widget(self.next_btn)
        pagination_row.add_widget(MDLabel())  # Spacer
        
        self.preview_card.add_widget(pagination_row)
        
        return self.preview_card
    
    def _load_initial_data(self, project_id: str):
        """Load initial data for preview"""
        self.current_page = 1
        self._load_data_page(project_id)
    
    def _create_loading_card(self):
        """Create enhanced loading state card"""
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(250),  # Increased height
            padding=[dp(40), dp(30), dp(40), dp(30)],  # Better padding
            spacing=dp(24),
            md_bg_color=(0.97, 0.98, 1.0, 1),  # Softer background
            elevation=3
        )
        
        # Loading icon
        loading_icon = MDIconButton(
            icon="loading",
            theme_icon_color="Custom",
            icon_color=(0.2, 0.6, 1.0, 1),
            disabled=True,
            size_hint=(None, None),
            size=(dp(64), dp(64))
        )
        
        loading_label = MDLabel(
            text="🔍 Loading data exploration...",
            font_style="H6",
            theme_text_color="Secondary",
            halign="center"
        )
        
        loading_hint = MDLabel(
            text="Please wait while we prepare your data",
            font_style="Body2",
            theme_text_color="Hint",
            halign="center"
        )
        
        card.add_widget(loading_icon)
        card.add_widget(loading_label)
        card.add_widget(loading_hint)
        return card
    
    def _show_error_state(self, content, error_message: str):
        """Show enhanced error state in content area"""
        content.clear_widgets()
        
        error_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(280),  # Increased height
            padding=[dp(40), dp(30), dp(40), dp(30)],  # Better padding
            spacing=dp(24),
            md_bg_color=(1.0, 0.96, 0.96, 1),  # Softer error background
            elevation=3
        )
        
        # Error icon
        error_icon = MDIconButton(
            icon="alert-circle-outline",
            theme_icon_color="Custom",
            icon_color=(0.8, 0.2, 0.2, 1),
            disabled=True,
            size_hint=(None, None),
            size=(dp(64), dp(64))
        )
        
        error_label = MDLabel(
            text=f"❌ {error_message}",
            font_style="H6",
            theme_text_color="Error",
            halign="center",
            text_size=(dp(400), None)
        )
        
        error_hint = MDLabel(
            text="Please try refreshing or contact support if the issue persists",
            font_style="Body2",
            theme_text_color="Secondary",
            halign="center"
        )
        
        # Retry button
        retry_btn = MDRaisedButton(
            text="🔄 Retry",
            size_hint=(None, None),
            size=(dp(120), dp(40)),
            pos_hint={'center_x': 0.5},
            md_bg_color=(0.2, 0.6, 1.0, 1),
            on_release=lambda x: content.clear_widgets()
        )
        
        error_card.add_widget(error_icon)
        error_card.add_widget(error_label)
        error_card.add_widget(error_hint)
        error_card.add_widget(retry_btn)
        content.add_widget(error_card)
        
        toast(f"{error_message}")
    
    def _show_table_error(self, error_message: str):
        """Show enhanced error in table area"""
        self.table_container.clear_widgets()
        
        error_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(200),
            padding=[dp(40), dp(40), dp(40), dp(40)]
        )
        
        error_icon = MDIconButton(
            icon="table-remove",
            theme_icon_color="Custom",
            icon_color=(0.8, 0.2, 0.2, 1),
            disabled=True,
            size_hint=(None, None),
            size=(dp(48), dp(48))
        )
        
        error_label = MDLabel(
            text=f"❌ {error_message}",
            halign="center",
            theme_text_color="Error",
            font_style="Body1"
        )
        
        error_container.add_widget(error_icon)
        error_container.add_widget(error_label)
        self.table_container.add_widget(error_container)
        toast(f"{error_message}") 