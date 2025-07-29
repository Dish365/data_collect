"""
Data Exploration Service for handling data exploration functionality - Business Logic Only
"""

import json
import threading
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any, Optional
from kivy.clock import Clock
from utils.cross_platform_toast import toast


class DataExplorationService:
    """Service for handling data exploration operations - Business Logic Only"""
    
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
            
        # Set loading state
        Clock.schedule_once(lambda dt: self.screen.set_loading(True), 0)
        
        # Load data summary first
        Clock.schedule_once(lambda dt: self._load_data_summary(project_id), 0.5)
    
    def _load_data_summary(self, project_id: str):
        """Load data summary and then initialize the exploration interface"""
        try:
            # Run the request in a separate thread to avoid async issues
            def make_request():
                try:
                    result = self.analytics_service.get_data_summary(project_id)
                    # Schedule the UI update on the main thread
                    Clock.schedule_once(lambda dt: self._handle_summary_result(project_id, result), 0.1)
                except Exception as e:
                    error_result = {'error': f'Request failed: {str(e)}'}
                    Clock.schedule_once(lambda dt: self._handle_summary_result(project_id, error_result), 0.1)
            
            # Start the request in a separate thread
            thread = threading.Thread(target=make_request)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error(f"Failed to load data summary: {str(e)}"), 0.1)
    
    def _handle_summary_result(self, project_id: str, summary_result):
        """Handle the result of the data summary request"""
        try:
            print(f"[DEBUG] _handle_summary_result called with: {summary_result}")
            
            if 'error' in summary_result:
                print(f"[DEBUG] Error in summary result: {summary_result['error']}")
                self._show_error(summary_result['error'])
                return
            
            # Set loading to false
            self.screen.set_loading(False)
            
            # Load initial data
            self._load_project_questions(project_id)
            self._load_initial_data(project_id)
            
        except Exception as e:
            print(f"[DEBUG] Exception in _handle_summary_result: {str(e)}")
            self._show_error(f"Failed to process data summary: {str(e)}")
    
    def _load_data_page(self, project_id: str):
        """Load data for current page with current filters"""
        try:
            # Show loading state
            Clock.schedule_once(lambda dt: self.screen.set_loading(True), 0)
            
            # Prepare filters
            search = self.screen.get_search_text()
            respondent_filter = self.screen.get_respondent_filter()
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
        """Fetch data from backend and display in UI"""
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
            Clock.schedule_once(lambda dt: toast(f"Failed to fetch data: {str(e)}"), 0.1)
    
    def _handle_data_result(self, result):
        """Handle the result of the data fetch request"""
        try:
            # Set loading to false
            self.screen.set_loading(False)
            
            if 'error' in result:
                self._show_error(result['error'])
                return
            
            # Store results
            self.current_data = result.get('data', [])
            pagination = result.get('pagination', {})
            self.total_count = pagination.get('total_count', 0)
            self.total_pages = pagination.get('total_pages', 0)
            
            # Update filter options
            self.filter_options = result.get('filter_options', {})
            
            # Update screen with data
            self.screen.update_data_display(self.current_data, pagination)
            
        except Exception as e:
            self._show_error(f"Failed to process data: {str(e)}")
    
    def apply_filters(self, project_id: str):
        """Apply current filters and reload data with visual feedback"""
        # Get current filter values from screen
        search = self.screen.get_search_text()
        respondent_filter = self.screen.get_respondent_filter()
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
        Clock.schedule_once(lambda dt: self.screen.update_filter_status(filters_applied), 0)
        
        # Reset to first page and reload data
        self.current_page = 1
        self._load_data_page(project_id)
        
        # Show user-friendly toast message
        if filters_applied:
            filter_count = len(filters_applied)
            toast(f"Applied {filter_count} filter{'s' if filter_count > 1 else ''}")
        else:
            toast("Loading all data")
    
    def clear_filters(self, project_id: str):
        """Clear all filters and reload data with visual feedback"""
        # Clear internal filter state
        self.current_filters = {}
        
        # Update visual indicators
        Clock.schedule_once(lambda dt: self.screen.update_filter_status([]), 0)
        
        # Reset to first page and reload data
        self.current_page = 1
        self._load_data_page(project_id)
        
        # Show confirmation message
        toast("All filters cleared")
    
    def load_previous_page(self, project_id: str):
        """Load previous page of data"""
        if self.current_page > 1:
            self.current_page -= 1
            self._load_data_page(project_id)
    
    def load_next_page(self, project_id: str):
        """Load next page of data"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._load_data_page(project_id)
    
    def show_question_filter_menu(self, project_id: str):
        """Show question filter dropdown menu"""
        if not self.project_questions:
            toast("Loading questions...")
            self._load_project_questions(project_id)
            return
        
        # Create menu items data
        menu_items_data = [
            {"text": "All Questions", "question": None}
        ]
        
        # Add all loaded questions
        for question in self.project_questions[:20]:  # Limit for performance
            display_text = question[:55] + "..." if len(question) > 55 else question
            menu_items_data.append({
                "text": display_text,
                "question": question
            })
        
        # Delegate menu display to screen (if needed for UI implementation)
        # For now, this is a placeholder for the menu functionality
        pass
    
    def select_question_filter(self, project_id: str, question_text: Optional[str]):
        """Select a question filter"""
        if question_text:
            self.current_filters['question_filter'] = question_text
        else:
            self.current_filters.pop('question_filter', None)
        
        # Apply filters with updated selection
        self.apply_filters(project_id)
    
    def toggle_response_selection(self, response_id: str, active: bool):
        """Toggle selection of individual response"""
        if active:
            self.selected_responses.add(response_id)
        else:
            self.selected_responses.discard(response_id)
        
        # Update selection info in UI
        Clock.schedule_once(lambda dt: self.screen.update_selection_info(len(self.selected_responses)), 0)
    
    def toggle_page_selection(self, active: bool):
        """Toggle selection of all responses on current page"""
        for row in self.current_data[:12]:
            response_id = str(row.get('response_id', ''))
            if response_id:
                if active:
                    self.selected_responses.add(response_id)
                else:
                    self.selected_responses.discard(response_id)
        
        # Update selection info in UI
        Clock.schedule_once(lambda dt: self.screen.update_selection_info(len(self.selected_responses)), 0)
    
    def sample_random(self, project_id: str):
        """Select random sample of responses"""
        try:
            sample_size = self.screen.get_sample_size()
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
                        search=self.screen.get_search_text(),
                        question_filter=self.current_filters.get('question_filter'),
                        respondent_filter=self.screen.get_respondent_filter()
                    )
                    Clock.schedule_once(lambda dt: self._handle_sampling_result(result, 'random'), 0.1)
                except Exception as e:
                    Clock.schedule_once(lambda dt: toast(f"Sampling failed: {str(e)}"), 0.1)
            
            thread = threading.Thread(target=make_request)
            thread.daemon = True
            thread.start()
            
        except ValueError:
            toast("Please enter a valid sample size")
    
    def sample_first_n(self, project_id: str):
        """Select first N responses"""
        try:
            sample_size = self.screen.get_sample_size()
            self.sample_size = min(sample_size, 500)
            
            def make_request():
                try:
                    result = self.analytics_service.explore_project_data(
                        project_id=project_id,
                        page=1,
                        page_size=self.sample_size,
                        search=self.screen.get_search_text(),
                        question_filter=self.current_filters.get('question_filter'),
                        respondent_filter=self.screen.get_respondent_filter()
                    )
                    Clock.schedule_once(lambda dt: self._handle_sampling_result(result, 'first'), 0.1)
                except Exception as e:
                    Clock.schedule_once(lambda dt: toast(f"Sampling failed: {str(e)}"), 0.1)
            
            thread = threading.Thread(target=make_request)
            thread.daemon = True
            thread.start()
            
        except ValueError:
            toast("Please enter a valid sample size")
    
    def sample_latest_n(self, project_id: str):
        """Select latest N responses"""
        self.sample_first_n(project_id)  # Same as first N since data is sorted by date DESC
    
    def sample_high_quality(self, project_id: str):
        """Select high quality responses only"""
        try:
            sample_size = self.screen.get_sample_size()
            self.sample_size = min(sample_size, 500)
            
            def make_request():
                try:
                    result = self.analytics_service.explore_project_data(
                        project_id=project_id,
                        page=1,
                        page_size=min(self.sample_size * 2, 500),  # Get more to filter by quality
                        search=self.screen.get_search_text(),
                        question_filter=self.current_filters.get('question_filter'),
                        respondent_filter=self.screen.get_respondent_filter()
                    )
                    Clock.schedule_once(lambda dt: self._handle_sampling_result(result, 'quality'), 0.1)
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
                Clock.schedule_once(lambda dt: self.screen.update_selection_info(len(self.selected_responses)), 0)
                
                toast(f"Selected {len(self.selected_responses)} responses ({sample_type} sampling)")
            else:
                toast("Failed to load data for sampling")
        except Exception as e:
            toast(f"Sampling error: {str(e)}")
    
    def select_all_responses(self, project_id: str):
        """Select all responses with current filters"""
        toast("Loading all responses for selection...")
        
        def make_request():
            try:
                # Get all responses with current filters
                result = self.analytics_service.explore_project_data(
                    project_id=project_id,
                    page=1,
                    page_size=500,  # Max for performance
                    search=self.screen.get_search_text(),
                    question_filter=self.current_filters.get('question_filter'),
                    respondent_filter=self.screen.get_respondent_filter()
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
                
                # Update UI
                Clock.schedule_once(lambda dt: self.screen.update_selection_info(len(self.selected_responses)), 0)
                
                toast(f"Selected {len(self.selected_responses)} responses")
            else:
                toast("Failed to select all responses")
        except Exception as e:
            toast(f"Selection error: {str(e)}")
    
    def clear_selection(self):
        """Clear all selected responses"""
        self.selected_responses.clear()
        Clock.schedule_once(lambda dt: self.screen.update_selection_info(0), 0)
        toast("Selection cleared")
    
    def export_selected_responses(self):
        """Export selected responses"""
        if not self.selected_responses:
            toast("No responses selected for export")
            return
        
        toast(f" Exporting {len(self.selected_responses)} selected responses...")
        # TODO: Implement actual export functionality
    
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
    
    def _load_initial_data(self, project_id: str):
        """Load initial data for preview"""
        self.current_page = 1
        self._load_data_page(project_id)
    
    def _show_error(self, error_message: str):
        """Show error message to user"""
        Clock.schedule_once(lambda dt: self.screen.set_loading(False), 0)
        Clock.schedule_once(lambda dt: self.screen.show_error(error_message), 0)

    # Analytics backend methods
    def _make_analytics_request(self, endpoint: str, method: str = 'GET', data: Dict = None) -> Dict:
        """Make authenticated request to analytics backend"""
        try:
            import requests
            base_url = "http://127.0.0.1:8001"
            url = f"{base_url}/api/v1/analytics/descriptive/{endpoint}"
            
            session = requests.Session()
            session.headers.update({
                'Content-Type': 'application/json',
                'User-Agent': 'DataCollect-GUI/1.0'
            })
            
            if method == 'GET':
                response = session.get(url, timeout=30)
            elif method == 'POST':
                if data:
                    response = session.post(url, json=data, timeout=60)
                else:
                    response = session.post(url, timeout=60)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, dict) and 'status' in result:
                    if result['status'] == 'success':
                        return result.get('data', {})
                    else:
                        return {'error': result.get('message', 'Unknown error')}
                return result
            else:
                try:
                    error_detail = response.json()
                    error_msg = error_detail.get('detail', f'HTTP {response.status_code}')
                    return {'error': error_msg}
                except:
                    return {'error': f'HTTP {response.status_code}: {response.text}'}
                
        except Exception as e:
            return {'error': f'Request error: {str(e)}'}

    def explore_project_data_backend(self, project_id: str, page: int = 1, page_size: int = 50, 
                           search: str = None, question_filter: str = None,
                           respondent_filter: str = None, date_from: str = None, 
                           date_to: str = None) -> Dict:
        """Explore project data with filtering and pagination via backend"""
        try:
            params = [('page', str(page)), ('page_size', str(page_size))]
            if search:
                params.append(('search', search))
            if question_filter:
                params.append(('question_filter', question_filter))
            if respondent_filter:
                params.append(('respondent_filter', respondent_filter))
            if date_from:
                params.append(('date_from', date_from))
            if date_to:
                params.append(('date_to', date_to))
            
            url = f'project/{project_id}/explore-data'
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            result = self._make_analytics_request(url, method='GET')
            return result
            
        except Exception as e:
            return {'error': f'Data exploration failed: {str(e)}'}

    def get_data_summary_backend(self, project_id: str) -> Dict:
        """Get quick data summary with types and samples via backend"""
        try:
            result = self._make_analytics_request(f'project/{project_id}/data-summary')
            return result
            
        except Exception as e:
            return {'error': f'Data summary failed: {str(e)}'} 