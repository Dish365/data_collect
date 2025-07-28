from kivy.uix.screenmanager import Screen
from widgets.form_fields import create_form_field
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty
from kivy.app import App
from utils.cross_platform_toast import toast
import threading
from kivymd.uix.menu import MDDropdownMenu

from kivy.lang import Builder

import json

from services.form_service import FormService
from widgets.loading_overlay import LoadingOverlay

Builder.load_file("kv/form_builder.kv")

class FormBuilderScreen(Screen):
    project_id = StringProperty(None, allownone=True)
    project_list = ListProperty([])
    project_map = {}  # Maps project name to id
    project_menu = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        self.form_service = FormService(app.auth_service, app.db_service, app.sync_service)
        self.questions_data = []
        
        # Initialize loading overlay
        self.loading_overlay = LoadingOverlay()
        
        # Response type display mapping
        self.response_type_display = {
            'text_short': 'Short Text',
            'text_long': 'Long Text',
            'numeric_integer': 'Number (Integer)',
            'numeric_decimal': 'Number (Decimal)',
            'choice_single': 'Single Choice',
            'choice_multiple': 'Multiple Choice',
            'scale_rating': 'Rating Scale',
            'date': 'Date',
            'datetime': 'Date & Time',
            'geopoint': 'GPS Location',
            'geoshape': 'GPS Area',
            'image': 'Photo/Image',
            'audio': 'Audio Recording',
            'video': 'Video Recording',
            'file': 'File Upload',
            'signature': 'Digital Signature',
            'barcode': 'Barcode/QR Code',
        }
    
    def on_enter(self):
        """Called when the screen is entered."""
        try:
            # Set top bar title for consistency
            if hasattr(self.ids, 'top_bar'):
                self.ids.top_bar.set_title("Form Builder")
            
            # Check if user is authenticated
            app = App.get_running_app()
            if not app.auth_service.is_authenticated():
                toast("Please log in to access Form Builder")
                Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'login'), 0.5)
                return
            
            # Load projects
            self.load_projects()
            
            # Initialize responsive layout
            self.update_responsive_layout()
            
            # Reset form state
            self.ids.form_canvas.clear_widgets()
            self.project_id = None
            # Update the empty state and question count
            self.update_question_count()
            self.update_empty_state()
            
        except Exception as e:
            print(f"Error in form builder on_enter: {e}")
            toast(f"Error initializing Form Builder: {str(e)}")
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'dashboard'), 1)

    def load_projects(self):
        """Loads all projects from the backend API and syncs to local DB."""
        app = App.get_running_app()
        
        # Ensure user is authenticated and has valid user data
        if not app.auth_service.is_authenticated():
            toast("Authentication required. Redirecting to login.")
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'login'), 0.5)
            return
        
        user_data = app.auth_service.get_user_data()
        if not user_data or not user_data.get('id'):
            toast("Invalid user session. Please log in again.")
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'login'), 0.5)
            return
        
        # Start loading in background thread
        def _load_projects_thread():
            try:
                # First try to get projects from backend API
                response = app.auth_service.make_authenticated_request('api/v1/projects/')
                
                if 'error' not in response:
                    # Sync backend projects to local database
                    api_projects = response.get('results', []) if 'results' in response else response
                    if isinstance(api_projects, list):
                        self._sync_projects_to_local(api_projects)
                
                # Now load from local database (single source of truth)
                conn = app.db_service.get_db_connection()
                try:
                    cursor = conn.cursor()
                    user_id = user_data.get('id')
                    cursor.execute("SELECT id, name FROM projects WHERE user_id = ? ORDER BY name", (user_id,))
                    projects = cursor.fetchall()
                    
                    # Update UI on main thread
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
        
        # Start background loading
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
            
            # Clear existing projects for this user that are synced (not pending local changes)
            cursor.execute("DELETE FROM projects WHERE user_id = ? AND sync_status != 'pending'", (user_id,))
            
            # Insert/update projects from API
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
            # Show helpful message and allow user to create projects
            toast("No projects found. Create a project first to build forms.")
            self.project_list = []
            self.project_map = {}
            if hasattr(self.ids, 'project_spinner'):
                self.ids.project_spinner.text = 'No Projects Available'
            self.project_id = None
            self.ids.form_canvas.clear_widgets()
            
            # Create no projects state using KV component
            from kivy.lang import Builder
            no_projects_widget = Builder.load_string('''
NoProjectsState:
''')
            self.ids.form_canvas.add_widget(no_projects_widget)
            
            print(f"No projects found for user {user_id}")
            return
            
        self.project_list = [p['name'] for p in projects]
        self.project_map = {p['name']: p['id'] for p in projects}
        if hasattr(self.ids, 'project_spinner'):
            self.ids.project_spinner.text = 'Select Project'
        self.project_id = None
        self.ids.form_canvas.clear_widgets()
        
        print(f"Loaded {len(projects)} projects for user {user_id}")
        
        # Update UI elements
        self.update_question_count()
        self.update_empty_state()

    def open_project_menu(self):
        if self.project_menu:
            self.project_menu.dismiss()
        menu_items = [
            {
                "text": name,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=name: self.on_project_selected(None, x)
            }
            for name in self.project_list
        ]
        self.project_menu = MDDropdownMenu(
            caller=self.ids.project_spinner,
            items=menu_items,
            width_mult=4
        )
        self.project_menu.open()

    def on_project_selected(self, spinner, text):
        """Handle project selection from dropdown menu."""
        try:
            if self.project_menu:
                self.project_menu.dismiss()
            
            if text == 'Select Project' or text not in self.project_map:
                self.project_id = None
                if hasattr(self.ids, 'project_spinner'):
                    self.ids.project_spinner.text = 'Select Project'
                self.ids.form_canvas.clear_widgets()
                self.update_question_count()
                self.update_empty_state()
                return
            
            self.project_id = self.project_map[text]
            if hasattr(self.ids, 'project_spinner'):
                self.ids.project_spinner.text = text
            
            # Update top bar title to show selected project
            if hasattr(self.ids, 'top_bar'):
                self.ids.top_bar.set_title(f"Form Builder - {text}")
            
            # Show loading overlay
            self.show_loader(True, "Loading form...")
            
            self.load_form()
        except Exception as e:
            print(f"Error selecting project: {e}")
            toast(f"Error selecting project: {str(e)}")
            # Hide loading overlay on error
            self.show_loader(False)

    def load_form(self):
        """Loads the questions for the current project."""
        self.show_loader(True)
        self.ids.form_canvas.clear_widgets()

        def _load_in_thread():
            try:
                questions, error = self.form_service.load_questions(self.project_id)
                if error:
                    raise Exception(error)
                self.questions_data = questions
                Clock.schedule_once(lambda dt: self._update_ui_with_questions())
            except Exception as e:
                error_message = str(e)  # Capture the error message
                Clock.schedule_once(lambda dt: toast(f"Error: {error_message}"))
            finally:
                Clock.schedule_once(lambda dt: self.show_loader(False, "Loading form..."))

        threading.Thread(target=_load_in_thread).start()

    def _update_ui_with_questions(self):
        """Populates the UI with question widgets using the new form fields."""
        question_number = 1
        for q_data in self.questions_data:
            # Get response type from the data - check both question_type (local DB) and response_type (API)
            response_type = q_data.get('response_type') or q_data.get('question_type', 'text_short')
            question_text = q_data.get('question_text', '')
            options = q_data.get('options') or []
            
            # Parse options if they're stored as JSON string
            if isinstance(options, str):
                try:
                    options = json.loads(options)
                except:
                    options = []
            
            # Ensure choice fields have at least default options if none are provided
            if response_type in ['choice_single', 'choice_multiple'] and (not options or len(options) == 0):
                options = ['Option 1', 'Option 2']
            
            print(f"Loading question: {question_text}, type: {response_type}, options: {options}")
            
            # Create the appropriate form field
            try:
                field = create_form_field(
                    response_type=response_type,
                    question_text=question_text,
                    options=options
                )
                
                # Set question number and other properties
                field.question_number = str(question_number)
                
                # Set the question text in the editable field
                if hasattr(field, 'question_input') and question_text:
                    field.question_input.text = question_text
                
                # Set additional properties for choice fields
                if hasattr(field, 'selected_option') and response_type == 'choice_single':
                    # For single choice, we might want to set a default if available
                    pass
                elif hasattr(field, 'selected_options') and response_type == 'choice_multiple':
                    # For multiple choice, we might want to set defaults if available
                    pass
                
                self.ids.form_canvas.add_widget(field)
                question_number += 1
                
            except Exception as e:
                print(f"Error creating form field for question {question_text}: {e}")
                # Fallback to basic text field
                field = create_form_field(
                    response_type='text_short',
                    question_text=question_text
                )
                field.question_number = str(question_number)
                if hasattr(field, 'question_input') and question_text:
                    field.question_input.text = question_text
                self.ids.form_canvas.add_widget(field)
                question_number += 1
        
        # Update UI elements after loading questions
        self.update_question_count()
        self.update_empty_state()

    def update_question_count(self):
        """Updates the question count (for internal tracking only)."""
        question_count = len([w for w in self.ids.form_canvas.children if hasattr(w, 'response_type')])
        # Question count chip has been removed from UI for better space utilization
        # Count is still tracked internally for functionality
        print(f"FormBuilder: Current question count: {question_count}")
    
    def update_empty_state(self):
        """Shows or hides the empty state based on whether there are questions."""
        question_count = len([w for w in self.ids.form_canvas.children if hasattr(w, 'response_type')])
        
        # Find empty state widget
        empty_state = None
        for child in self.ids.form_canvas.children:
            if hasattr(child, 'id') and getattr(child, 'id', None) == 'empty_state':
                empty_state = child
                break
        
        if question_count == 0:
            # Show empty state if not already shown
            if not empty_state:
                # Create empty state widget using KV component
                from kivy.lang import Builder
                empty_state = Builder.load_string('''
EmptyFormState:
    id: 'empty_state'
''')
                self.ids.form_canvas.add_widget(empty_state)
        else:
            # Hide empty state if it exists
            if empty_state:
                self.ids.form_canvas.remove_widget(empty_state)

    def add_question(self, response_type):
        """Adds a new question widget to the form canvas."""
        if not self.project_id:
            toast("Select a project first.")
            return
        
        try:
            # Calculate question number based on existing questions
            question_number = len([w for w in self.ids.form_canvas.children if hasattr(w, 'response_type')]) + 1
            
            # Create a new form field based on response type with empty question text
            display_name = self.response_type_display.get(response_type, response_type)
            field = create_form_field(
                response_type=response_type,
                question_text="",  # Start with empty question text for user to fill
                options=['Option 1', 'Option 2'] if 'choice' in response_type else None
            )
            
            # Set question number
            field.question_number = str(question_number)
            
            # Set placeholder text in the question input
            if hasattr(field, 'question_input'):
                display_name_lower = display_name.lower() if display_name else "question"
                field.question_input.hint_text = f"Enter your {display_name_lower} question here..."
            
            self.ids.form_canvas.add_widget(field)
            
            # Update UI elements
            self.update_question_count()
            self.update_empty_state()
            
            toast(f"Added Question {question_number} ({display_name})")
            
        except Exception as e:
            print(f"Error adding question of type {response_type}: {e}")
            toast(f"Error adding question: {str(e)}")

    def remove_question_widget(self, widget_instance):
        """Removes a question widget from the UI."""
        self.ids.form_canvas.remove_widget(widget_instance)

    def save_form(self):
        """Collects data from all form field widgets and saves the form."""
        if not self.project_id:
            toast("Select a project first.")
            return
        
        questions_to_save = []
        validation_errors = []
        question_widgets = []
        
        # Collect only question widgets (not spacers)
        for widget in self.ids.form_canvas.children:
            if hasattr(widget, 'response_type') and hasattr(widget, 'get_value'):
                question_widgets.append(widget)
        
        # Reverse to get correct order (since children are added in reverse)
        question_widgets.reverse()
        
        for i, widget in enumerate(question_widgets, 1):
            # Get question text from the editable field
            question_text = widget.get_question_text()
            response_type = widget.response_type
            
            # Update question number to maintain order
            widget.question_number = str(i)
            
            # Validate the field (includes question text validation)
            is_valid, field_errors = widget.validate()
            if not is_valid:
                validation_errors.extend([f"Question {i}: {error}" for error in field_errors])
                continue
            
            # Get the value/options for choice fields
            options = []
            allow_multiple = False
            
            if hasattr(widget, 'options') and response_type in ['choice_single', 'choice_multiple']:
                # Get the latest option texts from the input widgets
                option_inputs = getattr(widget, 'option_inputs', [])
                options = [input_widget.text.strip() for input_widget in option_inputs if input_widget.text.strip()]
                if len(options) < 2:
                    validation_errors.append(f"Question {i}: Choice questions need at least 2 options")
                    continue
            else:
                options = []
            
            # Determine if multiple answers are allowed based on response type
            allow_multiple = (response_type == 'choice_multiple')
            
            # Map to backend format
            questions_to_save.append({
                'question_text': question_text,
                'response_type': response_type,  # Using the new response type format
                'options': options,
                'allow_multiple': allow_multiple,
                'order_index': i - 1  # 0-based index for backend
            })
        
        # Check for validation errors
        if validation_errors:
            error_message = "Please fix the following issues:\n" + "\n".join(validation_errors)
            toast(error_message)
            return
            
        # Check if we have any questions to save
        if not questions_to_save:
            toast("Add at least one question before saving.")
            return
            
        self.show_loader(True)

        def _save_in_thread():
            try:
                result = self.form_service.save_questions(self.project_id, questions_to_save)
                Clock.schedule_once(lambda dt: toast(result.get('message', 'Form saved successfully!')))
            except Exception as e:
                error_message = str(e)  # Capture the error message
                Clock.schedule_once(lambda dt: toast(f"Error saving: {error_message}"))
            finally:
                Clock.schedule_once(lambda dt: self.show_loader(False))

        threading.Thread(target=_save_in_thread).start()

    def show_loader(self, show=True, message="Loading..."):
        if show:
            self.loading_overlay.show(message)
        else:
            self.loading_overlay.hide()

    def preview_questions(self):
        """Show a dialog previewing the current form questions."""
        questions = []
        question_widgets = []
        
        # Collect only question widgets (not spacers)
        for widget in self.ids.form_canvas.children:
            if hasattr(widget, 'response_type') and hasattr(widget, 'get_value'):
                question_widgets.append(widget)
        
        # Reverse to get correct order
        question_widgets.reverse()
        
        for i, widget in enumerate(question_widgets, 1):
            response_type = widget.response_type
            question_text = widget.get_question_text()  # Get from editable field
            display_name = self.response_type_display.get(response_type, response_type)
            
            if not question_text:
                question_text = "[No question text entered]"
            
            q = {
                'number': i,
                'question': question_text,
                'type': display_name
            }
            
            # Add options for choice fields
            if hasattr(widget, 'options') and widget.options:
                q['options'] = widget.options
                q['allow_multiple'] = (response_type == 'choice_multiple')
            
            questions.append(q)

        # Create preview dialog using KV component
        from kivy.lang import Builder
        preview_content = Builder.load_string(f'''
FormPreviewContent:
    questions_data: {repr(questions)}
''')
        
        dialog = MDDialog(
            title="Form Preview",
            type="custom",
            content_cls=preview_content,
            auto_dismiss=True,
        )
        
        # Add close button programmatically since we can't bind in string
        from kivymd.uix.button import MDButton, MDButtonText
        close_button = MDButton(
            style="text",
            on_release=lambda x: dialog.dismiss()
        )
        close_button.add_widget(MDButtonText(text="Close"))
        dialog.buttons = [close_button]
        
        dialog.open()

    # Legacy methods for backward compatibility
    def add_question_block(self):
        """Legacy method - redirects to add_question with default type"""
        self.add_question('text_short')

    def load_questions(self):
        """Legacy method - redirects to load_form"""
        self.load_form()
    
    def add_question_item(self, question):
        """Legacy method - now handled by _update_ui_with_questions"""
        pass
    
    def delete_question(self, question_id):
        """Legacy method - questions are now managed through the UI"""
        pass

    def _map_type_to_block(self, question_type):
        """Legacy mapping function for backward compatibility"""
        type_map = {
            'text': 'text_short',
            'long_text': 'text_long', 
            'choice': 'choice_single',
            'numeric': 'numeric_integer'
        }
        return type_map.get(question_type, question_type)

    def _map_type_to_backend(self, block_type):
        """Legacy mapping function for backward compatibility"""
        # Now we use the response_type directly
        return block_type 

    def on_window_resize(self, width, height):
        """Handle window resize for responsive layout adjustments"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            
            # Determine screen size category and orientation
            category = ResponsiveHelper.get_screen_size_category()
            is_landscape = ResponsiveHelper.is_landscape()
            
            print(f"FormBuilder: Window resized to {width}x{height} - {category} {'landscape' if is_landscape else 'portrait'}")
            
            # Update responsive properties
            self.update_responsive_layout()
            
        except Exception as e:
            print(f"Error handling window resize in form builder: {e}")
    
    def update_responsive_layout(self):
        """Update layout based on current screen size"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            
            category = ResponsiveHelper.get_screen_size_category()
            is_landscape = ResponsiveHelper.is_landscape()
            
            # Adjust sidebar width for different screen sizes
            if category in ["tablet", "large_tablet"]:
                if is_landscape:
                    # Reduce sidebar width in landscape for more content space
                    print("FormBuilder: Using tablet landscape layout (28% sidebar)")
                    self.set_sidebar_width(0.28)  # 28% width for landscape tablets
                else:
                    # Use standard width in portrait
                    print("FormBuilder: Using tablet portrait layout (32% sidebar)")
                    self.set_sidebar_width(0.32)  # 32% width for portrait tablets
            else:
                # Use mobile layout with more sidebar space
                print("FormBuilder: Using mobile layout (35% sidebar)")
                self.set_sidebar_width(0.35)  # Wider sidebar for mobile
            
            # Update spacing throughout the form
            spacing = ResponsiveHelper.get_responsive_spacing()
            padding = ResponsiveHelper.get_responsive_padding()
            
            # Apply to main layout if it exists
            # This will be enhanced when we implement the responsive layout
            
        except Exception as e:
            print(f"Error updating responsive layout in form builder: {e}")
    
    def set_sidebar_width(self, width_ratio):
        """Set the sidebar width ratio and adjust form canvas accordingly"""
        try:
            if hasattr(self.ids, 'sidebar_card'):
                self.ids.sidebar_card.size_hint = (width_ratio, 1)
                print(f"FormBuilder: Set sidebar width to {width_ratio*100}%")
                
                # Find and update the form canvas width to fill remaining space
                # The form canvas should take the remaining width
                form_canvas_width = 1.0 - width_ratio
                
                # Find the form canvas container (right panel)
                main_layout = None
                for child in self.children:
                    if hasattr(child, 'orientation') and child.orientation == 'vertical':
                        for subchild in child.children:
                            if hasattr(subchild, 'orientation') and subchild.orientation == 'horizontal':
                                main_layout = subchild
                                break
                        break
                
                if main_layout:
                    for widget in main_layout.children:
                        if hasattr(widget, 'size_hint') and widget != self.ids.sidebar_card:
                            widget.size_hint = (form_canvas_width, 1)
                            print(f"FormBuilder: Set form canvas width to {form_canvas_width*100}%")
                            break
                            
        except Exception as e:
            print(f"Error setting sidebar width: {e}") 