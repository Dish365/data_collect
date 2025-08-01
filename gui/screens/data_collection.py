from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp

from utils.cross_platform_toast import toast
from kivymd.uix.menu import MDDropdownMenu

import json
import threading
import uuid

from widgets.loading_overlay import LoadingOverlay
from widgets.responsive_layout import ResponsiveHelper

# KV file loaded by main app after theme initialization

class DataCollectionScreen(Screen):
    project_id = StringProperty(None, allownone=True)
    project_list = ListProperty([])
    project_map = {}
    project_menu = None
    questions_data = []
    response_widgets = []
    current_respondent_id = StringProperty(None, allownone=True)
    _is_loading_form = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.answered_questions = set()
        self.total_questions = 0
        self.progress_value = 0.0
        self.loading_overlay = LoadingOverlay()
        
        # Bind to window resize for responsive updates
        from kivy.core.window import Window
        Window.bind(size=self.on_window_resize)

    def on_enter(self):
        self.clear_current_form()
        if hasattr(self.ids, 'top_bar'):
            self.ids.top_bar.set_title("Collect Data")
            self.ids.top_bar.set_current_screen("data_collection")
        Clock.schedule_once(self._delayed_load, 0)
        self.update_responsive_layout()

    def on_window_resize(self, window, size):
        """Handle window resize for responsive layout adjustments"""
        try:
            Clock.schedule_once(lambda dt: self.update_responsive_layout(), 0.1)
        except Exception as e:
            print(f"Error handling window resize in data collection: {e}")

    def update_responsive_layout(self):
        """Update layout based on current screen size"""
        try:
            category = ResponsiveHelper.get_screen_size_category()
            is_landscape = ResponsiveHelper.is_landscape()
            
            print(f"DataCollection: Updating responsive layout for {category} {'landscape' if is_landscape else 'portrait'}")
            
            # Update form layout
            self.update_form_layout(category, is_landscape)
            
            # Update existing question widgets
            self.update_question_widgets_responsive()
            
        except Exception as e:
            print(f"Error updating responsive layout in data collection: {e}")

    def update_form_layout(self, category, is_landscape):
        """Update form layout based on screen size and orientation"""
        if not hasattr(self.ids, 'form_container'):
            return
            
        container = self.ids.form_container
        side_panel = self.ids.side_panel
        form_canvas = self.ids.form_canvas
        
        # Use responsive helper to determine layout
        use_sidebar = ResponsiveHelper.should_use_sidebar()
        content_width = ResponsiveHelper.get_content_width_ratio()
        sidebar_width = ResponsiveHelper.get_sidebar_width_ratio()
        
        if use_sidebar:
            container.orientation = 'horizontal'
            form_canvas.size_hint_x = content_width
            side_panel.size_hint_x = sidebar_width
            side_panel.opacity = 1
        else:
            container.orientation = 'vertical'
            form_canvas.size_hint_x = 1.0
            side_panel.size_hint_x = 0.0
            side_panel.opacity = 0

    def update_question_widgets_responsive(self):
        """Update existing question widgets for responsive layout"""
        try:
            for q, widget in self.response_widgets:
                if hasattr(widget, 'update_responsive'):
                    widget.update_responsive()
        except Exception as e:
            print(f"Error updating question widgets responsive: {e}")

    def _delayed_load(self, dt):
        self.load_projects()

    def load_projects(self):
        """Loads all projects from the backend API and syncs to local DB."""
        app = App.get_running_app()
        
        if not app.auth_service.is_authenticated():
            toast("Authentication required. Redirecting to login.")
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'login'), 0.5)
            return
        
        user_data = app.auth_service.get_user_data()
        if not user_data or not user_data.get('id'):
            toast("Invalid user session. Please log in again.")
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'login'), 0.5)
            return
        
        def _load_projects_thread():
            try:
                response = app.auth_service.make_authenticated_request('api/v1/projects/')
                
                if 'error' not in response:
                    api_projects = response.get('results', []) if 'results' in response else response
                    if isinstance(api_projects, list):
                        self._sync_projects_to_local(api_projects)
                
                conn = app.db_service.get_db_connection()
                try:
                    cursor = conn.cursor()
                    user_id = user_data.get('id')
                    cursor.execute("SELECT id, name FROM projects WHERE user_id = ? ORDER BY name", (user_id,))
                    projects = cursor.fetchall()
                    Clock.schedule_once(lambda dt: self._update_projects_ui(projects, user_id))
                except Exception as e:
                    print(f"Error loading projects from local DB: {e}")
                    Clock.schedule_once(lambda dt: toast(f"Error loading projects: {str(e)}"))
                finally:
                    if conn:
                        conn.close()
            except Exception as e:
                print(f"Error loading projects: {e}")
                Clock.schedule_once(lambda dt: toast(f"Error loading projects: {str(e)}"))
        
        threading.Thread(target=_load_projects_thread, daemon=True).start()
    
    def _sync_projects_to_local(self, api_projects):
        """Sync projects from API to local database."""
        app = App.get_running_app()
        user_data = app.auth_service.get_user_data()
        user_id = user_data.get('id') if user_data else None
        
        if not user_id:
            return
            
        conn = app.db_service.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE user_id = ? AND sync_status != 'pending'", (user_id,))
            
            for project in api_projects:
                cursor.execute("""
                    INSERT OR REPLACE INTO projects 
                    (id, name, description, user_id, sync_status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    project.get('id'),
                    project.get('name'),
                    project.get('description', ''),
                    user_id,
                    'synced',
                    project.get('created_at'),
                    project.get('updated_at')
                ))
            
            conn.commit()
            print(f"Synced {len(api_projects)} projects to local database")
        except Exception as e:
            print(f"Error syncing projects to local database: {e}")
        finally:
            if conn:
                conn.close()
    
    def _update_projects_ui(self, projects, user_id):
        """Update the UI with loaded projects."""
        if not projects:
            toast("No projects found. Create a project first to collect data.")
            self.project_list = []
            self.project_map = {}
            self.project_id = None
            self.current_respondent_id = None
            self._update_project_spinner_text('No Projects Available')
            self._show_empty_state("No projects found", "Go to the Projects page to create a new project first.")
            self._update_submit_button()
            return
            
        self.project_list = [p['name'] for p in projects]
        self.project_map = {p['name']: p['id'] for p in projects}
        self.project_id = None
        self.current_respondent_id = None
        self._update_project_spinner_text('Select Project')
        self.ids.form_canvas.clear_widgets()
        self._update_submit_button()
        print(f"Loaded {len(projects)} projects for user {user_id}")

    def _update_project_spinner_text(self, text):
        """Update project spinner text safely"""
        try:
            if hasattr(self.ids, 'project_spinner'):
                # KivyMD 2.0.1 structure: text is in child component
                if hasattr(self.ids.project_spinner, 'children') and self.ids.project_spinner.children:
                    self.ids.project_spinner.children[0].text = text
        except Exception as e:
            print(f"Error updating project spinner text: {e}")

    def open_project_menu(self):
        if self.project_menu:
            self.project_menu.dismiss()
        menu_items = [
            {
                "text": name,
                "on_release": lambda x=name: self.on_project_selected(None, x)
            }
            for name in self.project_list
        ]
        self.project_menu = MDDropdownMenu(
            caller=self.ids.project_spinner,
            items=menu_items,
            width=dp(200)
        )
        self.project_menu.open()

    def on_project_selected(self, spinner, text):
        """Handle project selection with comprehensive error handling"""
        try:
            print(f"Project selected: {text}")
            
            if self.project_menu:
                self.project_menu.dismiss()
                
            if text == 'Select Project' or text not in self.project_map:
                self.project_id = None
                self.current_respondent_id = None
                self._update_project_spinner_text('Select Project')
                self.ids.form_canvas.clear_widgets()
                self._update_submit_button()
                return
                
            self.project_id = self.project_map[text]
            self._update_project_spinner_text(text)
            self.current_respondent_id = None
            
            self.loading_overlay.show("Loading form...")
            print(f"Loading form for project ID: {self.project_id}")
            self.load_form()
            self._update_submit_button()
            
        except Exception as e:
            print(f"Error in on_project_selected: {e}")
            import traceback
            traceback.print_exc()
            toast(f"Error selecting project: {str(e)}")
            self.project_id = None
            self.current_respondent_id = None
            self._update_project_spinner_text('Select Project')
            self.ids.form_canvas.clear_widgets()
            self._update_submit_button()
            self.loading_overlay.hide()

    def load_form(self):
        """Load the form questions for the selected project"""
        if self._is_loading_form:
            print("[DEBUG] load_form called while already loading. Skipping duplicate call.")
            return
        self._is_loading_form = True
        try:
            print(f"[DEBUG] Starting to load form for project: {self.project_id}")
            self.ids.form_canvas.clear_widgets()
            self.response_widgets = []
            self.answered_questions = set()
            
            # Hide empty state
            empty_state = self.ids.get('empty_state')
            try:
                if empty_state:
                    empty_state.opacity = 0
            except ReferenceError:
                pass
            
            app = App.get_running_app()
            if not app or not hasattr(app, 'form_service'):
                raise Exception("Form service not available")
                
            questions, error = app.form_service.load_questions(self.project_id)
            if error:
                print(f"Error loading questions: {error}")
                toast(f"Error loading form: {error}")
                self._show_empty_state("Error loading form", error)
                return
                
            if not questions:
                print("No questions found for project")
                self._show_empty_state("No questions found", "This form doesn't have any questions yet")
                return
                
            print(f"Loaded {len(questions)} questions")
            self.questions_data = questions
            self.total_questions = len(questions)
            
            # Create question widgets using KV templates
            for i, q in enumerate(questions):
                try:
                    widget = self.create_question_widget_kv(q, i)
                    if widget:
                        self.ids.form_canvas.add_widget(widget)
                        self.response_widgets.append((q, widget))
                        self.track_answer_progress(q.get('id', ''))
                except Exception as e:
                    print(f"Error creating widget for question {i}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            self.show_form_controls()
            self.update_progress()
            self.populate_question_overview()
            
            print(f"[DEBUG] Current form_canvas children after load: {len(self.ids.form_canvas.children)}")
            print("Form loading completed successfully")
            
        except Exception as e:
            print(f"Error in load_form: {e}")
            import traceback
            traceback.print_exc()
            toast(f"Error loading form: {str(e)}")
            self._show_empty_state("Error loading form", str(e))
        finally:
            self._is_loading_form = False
            self.loading_overlay.hide()

    def create_question_widget_kv(self, question_data, index):
        """Create a question widget using KV templates"""
        q_type = question_data.get('response_type') or question_data.get('question_type', 'text')
        q_text = question_data.get('question_text', '').replace("'", "\\'")  # Escape quotes
        q_id = question_data.get('id', '')
        options = question_data.get('options') or []
        
        # Ensure options is a list and clean it
        if not options or not isinstance(options, list):
            options = []
        options = [opt for opt in options if isinstance(opt, str) and opt.strip()]
        if not options and q_type in ['choice', 'choice_single', 'choice_multiple']:
            options = ["Option 1", "Option 2"]
        
        # Create the appropriate widget using KV Builder
        try:
            if q_type in ['text', 'long_text', 'numeric', 'location']:
                return self._create_text_widget_kv(q_text, q_type, index, q_id)
            elif q_type in ['choice', 'choice_single', 'choice_multiple']:
                return self._create_choice_widget_kv(q_text, q_type, options, index, q_id)
            elif q_type == 'scale':
                return self._create_scale_widget_kv(q_text, index, q_id)
            elif q_type in ['date', 'datetime']:
                return self._create_date_widget_kv(q_text, q_type, index, q_id)
            else:
                return self._create_text_widget_kv(q_text, 'text', index, q_id)
        except Exception as e:
            print(f"Error creating widget for question {index}: {e}")
            return self._create_error_widget_kv(index, str(e))

    def _create_text_widget_kv(self, question_text, q_type, index, q_id):
        """Create text input widget using KV"""
        hint_text = {
            'text': "Enter your answer",
            'long_text': "Enter your detailed answer",
            'numeric': "Enter a number",
            'location': "Location (latitude, longitude)"
        }.get(q_type, "Enter your answer")
        
        multiline = "True" if q_type == 'long_text' else "False"
        input_filter = "'int'" if q_type == 'numeric' else "None"
        height = "dp(80)" if q_type == 'long_text' else "dp(48)"
        
        kv_string = f"""
QuestionCard:
    question_id: '{q_id}'

    QuestionHeader:
        question_number: '{index + 1}'
        question_text: '{question_text}'

    TextAnswer:
        hint_text: '{hint_text}'
        multiline: {multiline}
        input_filter: {input_filter}

        MDTextField:
            height: {height}
            on_text: root.parent.parent.parent.track_answer_progress('{q_id}')
"""
        
        widget = Builder.load_string(kv_string)
        self._setup_text_widget_references(widget, q_id)
        return widget

    def _create_choice_widget_kv(self, question_text, q_type, options, index, q_id):
        """Create choice widget using KV"""
        allow_multiple = q_type == 'choice_multiple'
        group_name = f"group_{q_id}" if not allow_multiple else ""
        
        # Build options KV
        options_kv = ""
        for i, option in enumerate(options):
            option_text = option.replace("'", "\\'")  # Escape quotes
            options_kv += f"""
        ChoiceOption:
            option_text: '{option_text}'
            group_name: '{group_name}'
            question_id: '{q_id}'

            MDCheckbox:
                on_active: root.parent.parent.parent.parent.parent.track_answer_progress('{q_id}')
"""
        
        kv_string = f"""
QuestionCard:
    question_id: '{q_id}'

    QuestionHeader:
        question_number: '{index + 1}'
        question_text: '{question_text}'

    ChoiceAnswer:
        options: {options}
        allow_multiple: {allow_multiple}
        question_id: '{q_id}'

{options_kv}
"""
        
        widget = Builder.load_string(kv_string)
        self._setup_choice_widget_references(widget, q_id, options)
        return widget

    def _create_scale_widget_kv(self, question_text, index, q_id):
        """Create scale widget using KV"""
        kv_string = f"""
QuestionCard:
    question_id: '{q_id}'

    QuestionHeader:
        question_number: '{index + 1}'
        question_text: '{question_text}'

    ScaleAnswer:
        question_id: '{q_id}'

        MDSlider:
            on_value: root.parent.parent.parent.track_answer_progress('{q_id}'); root.parent.children[0].text = str(int(self.value))
"""
        
        widget = Builder.load_string(kv_string)
        self._setup_scale_widget_references(widget, q_id)
        return widget

    def _create_date_widget_kv(self, question_text, q_type, index, q_id):
        """Create date widget using KV"""
        hint_text = "YYYY-MM-DD" if q_type == 'date' else "YYYY-MM-DD HH:MM"
        
        kv_string = f"""
QuestionCard:
    question_id: '{q_id}'

    QuestionHeader:
        question_number: '{index + 1}'
        question_text: '{question_text}'

    TextAnswer:
        hint_text: '{hint_text}'
        multiline: False
        input_filter: None

        MDTextField:
            on_text: root.parent.parent.parent.track_answer_progress('{q_id}')
"""
        
        widget = Builder.load_string(kv_string)
        self._setup_text_widget_references(widget, q_id)
        return widget

    def _create_error_widget_kv(self, index, error_message):
        """Create error widget using KV"""
        kv_string = f"""
MDCard:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(80)
    padding: dp(16)
    md_bg_color: app.theme_cls.error_color
    elevation: 1
    radius: [dp(8)]

    MDLabel:
        text: 'Error loading question {index + 1}'
        theme_text_color: "Custom"
        text_color: app.theme_cls.on_error
        bold: True

    MDLabel:
        text: '{error_message}'
        theme_text_color: "Custom"
        text_color: app.theme_cls.on_error
        font_size: "12sp"
"""
        
        return Builder.load_string(kv_string)

    def _setup_text_widget_references(self, widget, q_id):
        """Setup references for text widget"""
        try:
            # Find the text field and status indicator
            widget.answer_status = self._find_widget_by_id(widget, 'answer_status')
            widget.response_field = self._find_text_field(widget)
            widget.question_id = q_id
        except Exception as e:
            print(f"Error setting up text widget references: {e}")

    def _setup_choice_widget_references(self, widget, q_id, options):
        """Setup references for choice widget"""
        try:
            widget.answer_status = self._find_widget_by_id(widget, 'answer_status')
            widget.checkboxes = self._find_checkboxes(widget)
            widget.options = options
            widget.question_id = q_id
        except Exception as e:
            print(f"Error setting up choice widget references: {e}")

    def _setup_scale_widget_references(self, widget, q_id):
        """Setup references for scale widget"""
        try:
            widget.answer_status = self._find_widget_by_id(widget, 'answer_status')
            widget.response_field = self._find_slider(widget)
            widget.value_label = self._find_value_label(widget)
            widget.question_id = q_id
        except Exception as e:
            print(f"Error setting up scale widget references: {e}")

    def _find_widget_by_id(self, root, widget_id):
        """Find widget by ID in widget tree"""
        if hasattr(root, 'id') and root.id == widget_id:
            return root
        for child in getattr(root, 'children', []):
            result = self._find_widget_by_id(child, widget_id)
            if result:
                return result
        return None

    def _find_text_field(self, root):
        """Find MDTextField in widget tree"""
        from kivymd.uix.textfield import MDTextField
        if isinstance(root, MDTextField):
            return root
        for child in getattr(root, 'children', []):
            result = self._find_text_field(child)
            if result:
                return result
        return None

    def _find_checkboxes(self, root):
        """Find all MDCheckbox widgets in tree"""
        from kivymd.uix.selectioncontrol import MDCheckbox
        checkboxes = []
        
        def collect_checkboxes(widget):
            if isinstance(widget, MDCheckbox):
                checkboxes.append(widget)
            for child in getattr(widget, 'children', []):
                collect_checkboxes(child)
        
        collect_checkboxes(root)
        return checkboxes

    def _find_slider(self, root):
        """Find MDSlider in widget tree"""
        from kivymd.uix.slider import MDSlider
        if isinstance(root, MDSlider):
            return root
        for child in getattr(root, 'children', []):
            result = self._find_slider(child)
            if result:
                return result
        return None

    def _find_value_label(self, root):
        """Find value label for slider"""
        # Look for label with id 'value_label'
        return self._find_widget_by_id(root, 'value_label')

    def track_answer_progress(self, question_id):
        """Track progress when answers change"""
        try:
            print(f"[DEBUG] track_answer_progress called for question_id={question_id}")
            widget = None
            q_data = None
            
            # Find the widget and question data
            for q, w in self.response_widgets:
                if q.get('id', '') == question_id:
                    widget = w
                    q_data = q
                    break
            
            if not widget or not q_data:
                print(f"No widget or question data found for question_id {question_id}")
                self.update_progress()
                return
            
            q_type = q_data.get('response_type') or q_data.get('question_type', 'text')
            is_answered = self._check_question_answered(widget, q_type)
            
            # Update answered questions set
            if is_answered:
                self.answered_questions.add(question_id)
                self._update_answer_status_indicator(widget, True)
            else:
                self.answered_questions.discard(question_id)
                self._update_answer_status_indicator(widget, False)
            
            self.update_progress()
        except Exception as e:
            print(f"Error tracking answer progress: {e}")

    def _check_question_answered(self, widget, q_type):
        """Check if a question is answered based on its type"""
        try:
            if q_type in ('text', 'long_text', 'numeric', 'date', 'datetime', 'location'):
                if hasattr(widget, 'response_field') and widget.response_field:
                    value = widget.response_field.text
                    return bool(value and value.strip())
            elif q_type in ('choice', 'choice_single', 'choice_multiple'):
                if hasattr(widget, 'checkboxes'):
                    return any(cb.active for cb in widget.checkboxes)
            elif q_type == 'scale':
                if hasattr(widget, 'response_field') and widget.response_field:
                    return widget.response_field.value is not None
            return False
        except Exception as e:
            print(f"Error checking if question answered: {e}")
            return False

    def _update_answer_status_indicator(self, widget, is_answered):
        """Update the visual answer status indicator"""
        try:
            if hasattr(widget, 'answer_status') and widget.answer_status:
                if is_answered:
                    widget.answer_status.md_bg_color = [0.2, 0.8, 0.2, 1]  # Green
                else:
                    widget.answer_status.md_bg_color = [0.8, 0.8, 0.8, 1]  # Gray
        except Exception as e:
            print(f"Error updating answer status indicator: {e}")

    def update_progress(self):
        """Update progress bar and statistics"""
        try:
            if self.total_questions > 0:
                self.progress_value = len(self.answered_questions) / self.total_questions
                if hasattr(self.ids, 'form_progress'):
                    self.ids.form_progress.value = self.progress_value * 100
                if hasattr(self.ids, 'progress_text'):
                    self.ids.progress_text.text = f"{len(self.answered_questions)}/{self.total_questions}"
                if hasattr(self.ids, 'question_count_label'):
                    self.ids.question_count_label.text = f"{self.total_questions} Questions"
                if hasattr(self.ids, 'completion_status'):
                    if self.progress_value == 0:
                        status = "Not Started"
                    elif self.progress_value < 1.0:
                        percentage = int(self.progress_value * 100)
                        status = f"{percentage}% Complete"
                    else:
                        status = "Complete"
                    self.ids.completion_status.text = status
        except Exception as e:
            print(f"Error updating progress: {e}")

    def show_form_controls(self):
        """Show progress section and form controls"""
        try:
            if hasattr(self.ids, 'progress_section'):
                self.ids.progress_section.opacity = 1
            if hasattr(self.ids, 'form_actions'):
                self.ids.form_actions.opacity = 1
        except Exception as e:
            print(f"Error showing form controls: {e}")

    def populate_question_overview(self):
        """Populate the side panel with question overview"""
        try:
            if not hasattr(self.ids, 'question_overview'):
                return
                
            overview_box = self.ids.question_overview
            overview_box.clear_widgets()
            
            for i, q in enumerate(self.questions_data):
                try:
                    q_text = q.get('question_text', '').replace("'", "\\'")
                    q_type = q.get('response_type') or q.get('question_type', 'text')
                    
                    # Truncate long text
                    display_text = q_text[:25] + "..." if len(q_text) > 25 else q_text
                    
                    # Get readable type name
                    type_map = {
                        'text': 'Text',
                        'long_text': 'Text',
                        'numeric': 'Number',
                        'choice': 'Choice',
                        'choice_single': 'Choice',
                        'choice_multiple': 'Multi',
                        'scale': 'Scale',
                        'date': 'Date',
                        'datetime': 'DateTime',
                        'location': 'Location'
                    }
                    type_display = type_map.get(q_type, 'Input')
                    
                    kv_string = f"""
OverviewItem:
    question_number: '{i + 1}'
    question_text: '{display_text}'
    question_type: '{type_display}'
"""
                    
                    item_card = Builder.load_string(kv_string)
                    overview_box.add_widget(item_card)
                    
                except Exception as e:
                    print(f"Error creating overview item for question {i}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error populating question overview: {e}")

    def clear_current_form(self):
        """Clear all form responses"""
        try:
            self._clear_form()
            self.answered_questions.clear()
            self.update_progress()
            if hasattr(self.ids, 'question_overview'):
                self.ids.question_overview.clear_widgets()
            toast("Form cleared")
        except Exception as e:
            print(f"Error clearing form: {e}")
            toast("Error clearing form")

    def save_draft(self):
        """Save current form as draft"""
        try:
            answered_count = len(self.answered_questions)
            if answered_count > 0:
                toast(f"Draft saved with {answered_count} answers")
            else:
                toast("No answers to save as draft")
        except Exception as e:
            print(f"Error saving draft: {e}")
            toast("Error saving draft")

    def _update_submit_button(self):
        """Update submit button text based on current state"""
        try:
            if hasattr(self.ids, 'submit_button') and self.ids.submit_button.children:
                button_text = self.ids.submit_button.children[0]
                if self.project_id:
                    if self.current_respondent_id:
                        button_text.text = "Submit Additional Response"
                    else:
                        button_text.text = "Submit New Response"
                else:
                    button_text.text = "Submit"
        except Exception as e:
            print(f"Error updating submit button: {e}")

    def submit_response(self):
        """Submit the form response"""
        if not self.project_id:
            toast("Please select a project first")
            return
        
        if not self.response_widgets:
            toast("No form questions loaded")
            return
        
        try:
            self.ids.submit_button.children[0].text = "Submitting..."
            self.ids.submit_button.disabled = True
        except:
            pass
        
        threading.Thread(target=self._submit_in_thread, daemon=True).start()

    def _submit_in_thread(self):
        """Background thread for form submission"""
        try:
            app = App.get_running_app()
            responses_data = []
            
            for q, widget in self.response_widgets:
                q_type = q.get('response_type') or q.get('question_type', 'text')
                q_id = q.get('id', '')
                answer = self._collect_answer_from_widget(widget, q_type)
                
                if answer and str(answer).strip():
                    responses_data.append({
                        'question_id': q_id,
                        'response_value': str(answer),
                        'metadata': {
                            'question_type': q_type,
                            'question_text': q.get('question_text', ''),
                            'device_type': self.get_device_type(),
                            'screen_size': self.get_screen_dimensions()
                        }
                    })
            
            if not responses_data:
                total_questions = len(self.questions_data)
                Clock.schedule_once(lambda dt: toast(f"Please answer at least one question before submitting. You have {total_questions} question(s) to answer."))
                Clock.schedule_once(lambda dt: self._reset_submit_button())
                return
            
            # Create respondent if needed
            if not self.current_respondent_id:
                respondent_data = app.data_collection_service.create_respondent(
                    project_id=self.project_id,
                    is_anonymous=True,
                    consent_given=True
                )
                self.current_respondent_id = respondent_data['respondent_id']
            
            # Submit responses
            result = app.data_collection_service.submit_form_responses(
                project_id=self.project_id,
                respondent_id=self.current_respondent_id,
                responses_data=responses_data,
                location_data=None,
                device_info={
                    'device_type': self.get_device_type(),
                    'screen_dimensions': self.get_screen_dimensions(),
                    'answered_questions': len(responses_data),
                    'total_questions': len(self.questions_data)
                }
            )
            
            Clock.schedule_once(lambda dt: self._handle_submission_success(result, len(responses_data), len(self.questions_data)))
            
        except Exception as e:
            error_message = str(e)
            print(f"Error submitting form: {error_message}")
            Clock.schedule_once(lambda dt: toast(f"Submission error: {error_message}"))
            Clock.schedule_once(lambda dt: self._reset_submit_button())

    def _collect_answer_from_widget(self, widget, q_type):
        """Collect answer from widget based on question type"""
        try:
            if q_type in ('text', 'long_text', 'numeric', 'date', 'datetime', 'location'):
                if hasattr(widget, 'response_field') and widget.response_field:
                    return widget.response_field.text
            elif q_type in ('choice', 'choice_single', 'choice_multiple'):
                if hasattr(widget, 'checkboxes') and hasattr(widget, 'options'):
                    selected = []
                    for i, checkbox in enumerate(widget.checkboxes):
                        if checkbox.active and i < len(widget.options):
                            selected.append(widget.options[i])
                    
                    if q_type == 'choice_multiple':
                        return selected
                    else:
                        return selected[0] if selected else None
            elif q_type == 'scale':
                if hasattr(widget, 'response_field') and widget.response_field:
                    return str(int(widget.response_field.value))
            return None
        except Exception as e:
            print(f"Error collecting answer from widget: {e}")
            return None

    def get_device_type(self):
        """Get current device type for metadata"""
        try:
            return ResponsiveHelper.get_screen_size_category()
        except:
            return "unknown"

    def get_screen_dimensions(self):
        """Get screen dimensions for metadata"""
        try:
            from kivy.core.window import Window
            return f"{Window.width}x{Window.height}"
        except:
            return "unknown"

    def _handle_submission_success(self, result, answered_count, total_count):
        """Handle successful form submission"""
        completion_rate = int((answered_count / total_count) * 100) if total_count > 0 else 0
        success_message = f"Response submitted successfully! {answered_count}/{total_count} questions answered ({completion_rate}%)"
        toast(success_message)
        
        self.current_respondent_id = None
        self._clear_form()
        self.answered_questions.clear()
        self.update_progress()
        self._reset_submit_button()
        self.hide_form_controls()

    def hide_form_controls(self):
        """Hide form controls after submission"""
        try:
            if hasattr(self.ids, 'progress_section'):
                self.ids.progress_section.opacity = 0
            if hasattr(self.ids, 'form_actions'):
                self.ids.form_actions.opacity = 0
            if hasattr(self.ids, 'side_panel'):
                self.ids.side_panel.opacity = 0
        except Exception as e:
            print(f"Error hiding form controls: {e}")

    def _clear_form(self):
        """Clear all form responses"""
        for q, widget in self.response_widgets:
            q_type = q.get('response_type') or q.get('question_type', 'text')
            
            try:
                if q_type in ('text', 'long_text', 'numeric', 'location', 'date', 'datetime'):
                    if hasattr(widget, 'response_field') and widget.response_field:
                        widget.response_field.text = ""
                elif q_type in ('choice', 'choice_single', 'choice_multiple'):
                    if hasattr(widget, 'checkboxes'):
                        for cb in widget.checkboxes:
                            cb.active = False
                elif q_type == 'scale':
                    if hasattr(widget, 'response_field') and widget.response_field:
                        widget.response_field.value = 3
                
                self._update_answer_status_indicator(widget, False)
                        
            except Exception as e:
                print(f"Error clearing widget for question type {q_type}: {e}")

    def _show_empty_state(self, title="No form loaded", message="Select a project above to load its data collection form"):
        """Show empty state display"""
        try:
            self.ids.form_canvas.clear_widgets()
            self.hide_form_controls()
            
            # Show the empty state defined in KV
            if hasattr(self.ids, 'empty_state'):
                self.ids.empty_state.opacity = 1
                    
        except Exception as e:
            print(f"Error showing empty state: {e}")

    def _reset_submit_button(self):
        """Reset submit button to normal state"""
        try:
            self.ids.submit_button.disabled = False
            self._update_submit_button()
        except Exception as e:
            print(f"Error resetting submit button: {e}")