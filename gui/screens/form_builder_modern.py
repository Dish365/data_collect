from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty
from kivy.app import App
from kivy.metrics import dp
from kivy.lang import Builder
from utils.cross_platform_toast import toast
from widgets.form_field_modern import create_form_field
from services.form_service_modern import ModernFormService as FormService
import threading
import json

# Load the modern KV file
# KV file loaded by main app after theme initialization

class FormBuilderScreen(Screen):
    """Modern, streamlined form builder screen"""
    
    project_id = StringProperty(None, allownone=True)
    project_list = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_map = {}
        self.project_menu = None
        self.questions_data = []
        
        # Initialize services
        app = App.get_running_app()
        self.form_service = FormService(app.auth_service, app.db_service, app.sync_service)
        
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
            'barcode': 'Barcode/QR Code'
        }
    
    def on_enter(self):
        """Called when the screen is entered"""
        try:
            print("Debug: Form builder on_enter called")
            
            # Set top bar title
            if hasattr(self.ids, 'top_bar'):
                self.ids.top_bar.set_title("Form Builder")
                self.ids.top_bar.set_current_screen("form_builder")
            
            # Check authentication
            app = App.get_running_app()
            if not app.auth_service.is_authenticated():
                toast("Please log in to access Form Builder")
                Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'login'), 0.5)
                return
            
            # Reset form state but preserve project selection if coming from project creation
            # Check if we have a selected project that was just created
            selected_project = getattr(app, '_selected_project_for_form_builder', None)
            if selected_project:
                self.project_id = selected_project.get('id')
                # Clear the temp variable
                delattr(app, '_selected_project_for_form_builder')
                
                # Load projects and then load the specific form
                Clock.schedule_once(lambda dt: self._load_projects_and_select(selected_project), 0.3)
            else:
                # Normal flow - reset and load projects
                self.reset_form()
                Clock.schedule_once(lambda dt: self.load_projects(), 0.5)
            
        except Exception as e:
            print(f"Error in form builder on_enter: {e}")
            toast(f"Error initializing Form Builder: {str(e)}")
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'dashboard'), 1)
    
    def load_projects(self):
        """Load projects in background thread"""
        def _load_projects_thread():
            try:
                app = App.get_running_app()
                
                # Check authentication
                if not app.auth_service.is_authenticated():
                    Clock.schedule_once(lambda dt: self._handle_auth_error())
                    return
                
                user_data = app.auth_service.get_user_data()
                if not user_data or not user_data.get('id'):
                    Clock.schedule_once(lambda dt: self._handle_auth_error())
                    return
                
                # Try to get projects from backend API
                response = app.auth_service.make_authenticated_request('api/v1/projects/')
                
                # Sync to local database if successful
                if 'error' not in response:
                    api_projects = response.get('results', []) if 'results' in response else response
                    if isinstance(api_projects, list):
                        self._sync_projects_to_local(api_projects, user_data.get('id'))
                
                # Load from local database
                projects = self._load_projects_from_local(user_data.get('id'))
                Clock.schedule_once(lambda dt: self._update_projects_ui(projects))
                
            except Exception as e:
                print(f"Error loading projects: {e}")
                Clock.schedule_once(lambda dt: toast(f"Error loading projects: {str(e)}"))
        
        threading.Thread(target=_load_projects_thread, daemon=True).start()
    
    def _sync_projects_to_local(self, api_projects, user_id):
        """Sync projects from API to local database"""
        app = App.get_running_app()
        conn = app.db_service.get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Clear existing synced projects
            cursor.execute("DELETE FROM projects WHERE user_id = ? AND sync_status != 'pending'", (user_id,))
            
            # Insert/update projects from API
            for project in api_projects:
                # Handle created_by field properly
                created_by = project.get('created_by')
                if isinstance(created_by, dict):
                    created_by = created_by.get('username') or created_by.get('id')
                elif not created_by:
                    created_by = user_id  # Use current user as fallback
                
                cursor.execute("""
                    INSERT OR REPLACE INTO projects 
                    (id, name, description, user_id, created_by, sync_status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project.get('id'),
                    project.get('name'),
                    project.get('description', ''),
                    user_id,
                    created_by,
                    'synced',
                    project.get('created_at'),
                    project.get('updated_at')
                ))
            
            conn.commit()
            print(f"Synced {len(api_projects)} projects to local database")
            
        except Exception as e:
            print(f"Error syncing projects to local database: {e}")
            # Don't fail completely, just log the error
        finally:
            if conn:
                conn.close()
    
    def _load_projects_from_local(self, user_id):
        """Load projects from local database"""
        app = App.get_running_app()
        conn = app.db_service.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description FROM projects WHERE user_id = ? ORDER BY name", (user_id,))
            return [{'id': row[0], 'name': row[1], 'description': row[2]} for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error loading projects from local DB: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def _update_projects_ui(self, projects):
        """Update the UI with loaded projects"""
        print(f"Debug: _update_projects_ui called with {len(projects) if projects else 0} projects")
        print(f"Debug: Projects data: {projects}")
        
        if not projects:
            # Show no projects state
            self.project_list = []
            self.project_map = {}
            self.project_id = None
            self._show_no_projects_state()
            print("Debug: No projects - showing no projects state")
            return
        
        # Update project data
        self.project_list = [p['name'] for p in projects]
        self.project_map = {p['name']: p['id'] for p in projects}
        
        print(f"Debug: Updated project_list to: {self.project_list}")
        print(f"Debug: Updated project_map to: {self.project_map}")
        
        # Update UI
        if hasattr(self.ids, 'project_selector'):
            # Update button text - find MDButtonText child
            for child in self.ids.project_selector.children:
                if hasattr(child, 'text'):
                    child.text = 'Select Project'
                    break
            print("Debug: Updated project selector button text")
        else:
            print("Debug: project_selector not found in ids")
        
        # Remove no projects state if it exists
        self._remove_no_projects_state()
        
        # Show empty form state
        from kivy.lang import Builder
        empty_state = Builder.load_string('''
EmptyFormState:
    id: 'empty_state'
''')
        if hasattr(self.ids, 'form_canvas'):
            self.ids.form_canvas.clear_widgets()
            self.ids.form_canvas.add_widget(empty_state)
        
        print(f"Loaded {len(projects)} projects successfully")
    
    def _show_no_projects_state(self):
        """Show the no projects state"""
        if hasattr(self.ids, 'form_canvas'):
            self.ids.form_canvas.clear_widgets()
            
            # Create no projects widget
            from kivy.lang import Builder
            no_projects_widget = Builder.load_string('''
NoProjectsState:
    id: 'no_projects_state'
''')
            self.ids.form_canvas.add_widget(no_projects_widget)
            
            # Also update project selector button
            if hasattr(self.ids, 'project_selector'):
                for child in self.ids.project_selector.children:
                    if hasattr(child, 'text'):
                        child.text = 'No Projects Available'
                        break
    
    def _handle_auth_error(self):
        """Handle authentication errors"""
        toast("Authentication required. Redirecting to login.")
        self.manager.current = 'login'
    
    def open_project_menu(self):
        """Open the project selection menu"""
        print("="*50)
        print("DEBUG: open_project_menu() called!")
        print(f"DEBUG: self.project_list = {self.project_list}")
        print(f"DEBUG: len(project_list) = {len(self.project_list) if self.project_list else 0}")
        
        if not self.project_list:
            toast("No projects available. Go to Projects to create one first.", duration=3)
            print("DEBUG: No projects available - showing toast")
            return
        
        try:
            print("DEBUG: Importing MDDropdownMenu...")
            from kivymd.uix.menu import MDDropdownMenu
            
            if self.project_menu:
                print("DEBUG: Dismissing existing menu")
                self.project_menu.dismiss()
            
            print("DEBUG: Creating menu items...")
            menu_items = []
            for name in self.project_list:
                print(f"DEBUG: Adding menu item: {name}")
                menu_items.append({
                    "text": name,
                    "on_release": lambda x=name: self.on_project_selected(x)
                })
            
            print(f"DEBUG: Created {len(menu_items)} menu items")
            
            print("DEBUG: Creating MDDropdownMenu...")
            self.project_menu = MDDropdownMenu(
                caller=self.ids.project_selector,
                items=menu_items,
                width=dp(250),
                max_height=dp(300)
            )
            
            print("DEBUG: Opening dropdown menu...")
            self.project_menu.open()
            print("DEBUG: Menu opened successfully!")
            
        except Exception as e:
            print(f"ERROR: Exception in open_project_menu: {e}")
            import traceback
            traceback.print_exc()
            toast(f"Error opening project list: {str(e)}", duration=3)
    
    def on_project_selected(self, project_name):
        """Handle project selection"""
        try:
            print(f"DEBUG: Project selected: {project_name}")
            print(f"DEBUG: Project ID: {self.project_map.get(project_name)}")
            
            if self.project_menu:
                self.project_menu.dismiss()
            
            # Update selected project
            self.project_id = self.project_map.get(project_name)
            
            if not self.project_id:
                toast("Error: Could not find project ID")
                return
            
            # Update UI - find and update the MDButtonText widget
            if hasattr(self.ids, 'project_selector'):
                # Find the MDButtonText child specifically
                from kivymd.uix.button import MDButtonText
                
                def find_and_update_text(widget):
                    if isinstance(widget, MDButtonText):
                        widget.text = project_name
                        print(f"DEBUG: Updated MDButtonText to: {project_name}")
                        return True
                    if hasattr(widget, 'children'):
                        for child in widget.children:
                            if find_and_update_text(child):
                                return True
                    return False
                
                if not find_and_update_text(self.ids.project_selector):
                    print("DEBUG: Could not find MDButtonText widget to update")
            
            # Update top bar title
            if hasattr(self.ids, 'top_bar'):
                self.ids.top_bar.set_title(f"Form Builder - {project_name}")
            
            # Show loading and load form
            self.show_loading(True, "Loading form questions...")
            
            # Load form questions with delay to ensure UI updates
            Clock.schedule_once(lambda dt: self.load_form(), 0.2)
            
        except Exception as e:
            print(f"Error selecting project: {e}")
            toast(f"Error selecting project: {str(e)}")
            self.show_loading(False)
    
    def load_form(self):
        """Load existing form questions for the selected project"""
        print(f"DEBUG: load_form() called for project_id: {self.project_id}")
        
        def _load_in_thread():
            try:
                print(f"DEBUG: Loading questions for project: {self.project_id}")
                questions, error = self.form_service.load_questions(self.project_id)
                
                print(f"DEBUG: Form service returned {len(questions) if questions else 0} questions")
                if error:
                    print(f"DEBUG: Form service error: {error}")
                    raise Exception(error)
                
                if questions:
                    print(f"DEBUG: First question sample: {questions[0] if questions else 'None'}")
                
                self.questions_data = questions
                Clock.schedule_once(lambda dt: self._update_ui_with_questions())
                
            except Exception as e:
                error_message = str(e)
                print(f"ERROR: Exception in load_form thread: {error_message}")
                import traceback
                traceback.print_exc()
                Clock.schedule_once(lambda dt: toast(f"Error loading form: {error_message}"))
            finally:
                Clock.schedule_once(lambda dt: self.show_loading(False))
        
        threading.Thread(target=_load_in_thread, daemon=True).start()
    
    def _update_ui_with_questions(self):
        """Update UI with loaded questions"""
        print(f"DEBUG: _update_ui_with_questions called with {len(self.questions_data) if self.questions_data else 0} questions")
        
        if not hasattr(self.ids, 'form_canvas'):
            print("DEBUG: form_canvas not found in ids")
            return
        
        # Clear existing widgets
        self.ids.form_canvas.clear_widgets()
        
        if not self.questions_data:
            print("DEBUG: No questions data - showing empty state")
            # Show empty form state
            from kivy.lang import Builder
            empty_state = Builder.load_string('''
EmptyFormState:
    id: 'empty_state'
''')
            self.ids.form_canvas.add_widget(empty_state)
            return
        
        print(f"DEBUG: Creating {len(self.questions_data)} form fields")
        
        # Sort questions by order_index to ensure proper ordering
        sorted_questions = sorted(self.questions_data, key=lambda x: x.get('order_index', 0))
        
        # Create form fields from questions data
        question_number = 1
        for q_data in sorted_questions:
            try:
                print(f"DEBUG: Processing question {question_number}: {q_data}")
                
                # Get response type and question text
                response_type = q_data.get('response_type') or q_data.get('question_type', 'text_short')
                question_text = q_data.get('question_text', '')
                options = q_data.get('options') or []
                is_required = q_data.get('is_required', True)
                
                # Parse options if they're JSON string
                if isinstance(options, str):
                    try:
                        options = json.loads(options)
                    except:
                        options = []
                
                # Ensure choice fields have default options
                if response_type in ['choice_single', 'choice_multiple'] and not options:
                    options = ['Option 1', 'Option 2']
                
                print(f"DEBUG: Creating field - type: {response_type}, text: {question_text[:50]}...")
                
                # Create the form field
                field = create_form_field(
                    response_type=response_type,
                    question_text=question_text,
                    options=options,
                    is_required=is_required
                )
                
                # Set question number and ID
                field.question_number = str(question_number)
                field.question_id = q_data.get('id')
                
                # Add to canvas with proper spacing
                self.ids.form_canvas.add_widget(field)
                question_number += 1
                
                print(f"DEBUG: Successfully added field {question_number - 1}")
                
            except Exception as e:
                print(f"ERROR: Error creating form field for question {question_number}: {e}")
                import traceback
                traceback.print_exc()
                
                # Create fallback text field
                try:
                    field = create_form_field(
                        response_type='text_short',
                        question_text=q_data.get('question_text', f'Question {question_number}'),
                        is_required=q_data.get('is_required', True)
                    )
                    field.question_number = str(question_number)
                    field.question_id = q_data.get('id')
                    self.ids.form_canvas.add_widget(field)
                    question_number += 1
                    print(f"DEBUG: Added fallback field for question {question_number - 1}")
                except Exception as fallback_error:
                    print(f"ERROR: Failed to create fallback field: {fallback_error}")
        
        print(f"DEBUG: Finished creating form fields. Total: {question_number - 1}")
    
    def add_question(self, response_type):
        """Add a new question to the form"""
        
        if not self.project_id:
            toast("Please select a project first to start building your form.", duration=3)
            return
        
        try:
            # Remove empty state if present
            self._remove_empty_state()
            
            # Calculate question number
            question_count = len([w for w in self.ids.form_canvas.children if hasattr(w, 'response_type')])
            question_number = question_count + 1
            
            # Create the form field
            field = create_form_field(
                response_type=response_type,
                question_text="",
                options=['Option 1', 'Option 2'] if 'choice' in response_type else []
            )
            
            # Set question number
            field.question_number = str(question_number)
            
            # Add to canvas (at top since children are reversed)
            self.ids.form_canvas.add_widget(field, index=len(self.ids.form_canvas.children))
            
            # Auto-focus on the question text input
            Clock.schedule_once(lambda dt: self._focus_new_question(field), 0.1)
            
            # Show success message with better formatting
            display_name = self.response_type_display.get(response_type, response_type)
            toast(f"✓ Added {display_name} question", duration=2)
            
        except Exception as e:
            print(f"Error adding question: {e}")
            toast(f"Failed to add question: {str(e)}", duration=3)
    
    def _focus_new_question(self, field):
        """Focus on the question text input of a new field"""
        try:
            if hasattr(field, 'question_input') and hasattr(field.question_input, 'focus'):
                field.question_input.focus = True
        except Exception as e:
            print(f"Could not focus question input: {e}")
    
    def save_form(self):
        """Save the current form with enhanced user feedback"""
        
        if not self.project_id:
            toast("Please select a project first to save your form.", duration=3)
            return
        
        try:
            # Collect all form fields
            form_fields = [w for w in self.ids.form_canvas.children if hasattr(w, 'response_type')]
            
            if not form_fields:
                toast("Add at least one question before saving your form.", duration=3)
                return
            
            # Reverse order (children are in reverse order)
            form_fields.reverse()
            
            # Validate and collect questions
            questions_to_save = []
            validation_errors = []
            empty_questions = []
            
            for i, field in enumerate(form_fields, 1):
                # Update question number
                field.question_number = str(i)
                
                # Check if question is empty
                question_text = field.get_question_text().strip()
                if not question_text:
                    empty_questions.append(i)
                    continue
                
                # Validate field
                is_valid, errors = field.validate()
                if not is_valid:
                    validation_errors.extend([f"Question {i}: {error}" for error in errors])
                    continue
                
                # Convert to save format
                question_data = field.to_dict()
                question_data['order_index'] = i - 1
                questions_to_save.append(question_data)
            
            # Check for empty questions first
            if empty_questions and not questions_to_save:
                # All questions are empty
                if len(empty_questions) == 1:
                    toast("Please enter text for your question before saving.", duration=3)
                else:
                    toast(f"Please enter text for your {len(empty_questions)} questions before saving.", duration=3)
                return
            elif empty_questions:
                # Some questions are empty but others have content
                empty_list = ", ".join([f"Q{q}" for q in empty_questions[:3]])
                if len(empty_questions) > 3:
                    empty_list += f" and {len(empty_questions) - 3} more"
                toast(f"Skipping empty questions: {empty_list}", duration=3)
            
            # Check for validation errors
            if validation_errors:
                error_count = len(validation_errors)
                if error_count == 1:
                    toast(f"Please fix: {validation_errors[0]}", duration=4)
                else:
                    toast(f"Please fix {error_count} validation errors. Check question fields.", duration=4)
                return
            
            # Check if we have any questions to save after filtering
            if not questions_to_save:
                toast("No valid questions to save. Please add and complete at least one question.", duration=3)
                return
            
            # Show progress and save
            questions_count = len(questions_to_save)
            self.show_loading(True, f"Saving {questions_count} question{'s' if questions_count != 1 else ''}...")
            self._save_form_async(questions_to_save)
            
        except Exception as e:
            print(f"Error saving form: {e}")
            toast(f"Failed to save form: {str(e)}", duration=3)
            self.show_loading(False)
    
    def _save_form_async(self, questions_to_save):
        """Save form in background thread"""
        def _save_in_thread():
            try:
                result = self.form_service.save_questions(self.project_id, questions_to_save)
                
                if 'error' in result:
                    error_message = result['error']
                    Clock.schedule_once(lambda dt: toast(f"Save failed: {error_message}", duration=3))
                else:
                    # Success message with status indication
                    questions_count = len(questions_to_save)
                    if result.get('status') == 'synced':
                        message = f"✓ Saved {questions_count} question{'s' if questions_count != 1 else ''} to cloud"
                    else:
                        message = f"✓ Saved {questions_count} question{'s' if questions_count != 1 else ''} locally"
                    
                    Clock.schedule_once(lambda dt: toast(message, duration=2))
                
            except Exception as e:
                error_message = str(e)
                Clock.schedule_once(lambda dt: toast(f"Save failed: {error_message}", duration=3))
            finally:
                Clock.schedule_once(lambda dt: self.show_loading(False))
        
        threading.Thread(target=_save_in_thread, daemon=True).start()
    
    def preview_form(self):
        """Preview the current form"""
        
        try:
            # Collect all form fields
            form_fields = [w for w in self.ids.form_canvas.children if hasattr(w, 'response_type')]
            
            if not form_fields:
                toast("Add questions to preview the form.")
                return
            
            # Reverse order to match actual form order (since children are in reverse)
            form_fields.reverse()
            questions = []
            
            for i, field in enumerate(form_fields, 1):
                # Get current question text from the field
                question_text = field.get_question_text()
                
                if not question_text.strip():
                    question_text = f"[Question {i} - no text entered]"
                
                display_name = self.response_type_display.get(field.response_type, field.response_type)
                
                question_info = {
                    'number': i,
                    'question': question_text,
                    'type': display_name,
                    'required': field.is_required
                }
                
                # Add options for choice fields - get current options from the field
                if field.response_type in ['choice_single', 'choice_multiple']:
                    # Filter out empty options
                    current_options = [opt.strip() for opt in field.options if opt.strip()] if field.options else []
                    if current_options:
                        question_info['options'] = current_options
                    else:
                        question_info['options'] = ['[No options set]']
                
                # Add scale info for rating fields
                if field.response_type == 'scale_rating':
                    question_info['scale_info'] = f"Scale: {field.min_value} to {field.max_value}"
                
                questions.append(question_info)
            
            print(f"DEBUG: Preview showing {len(questions)} questions")
            for q in questions:
                print(f"DEBUG: Q{q['number']}: {q['question'][:50]}... ({q['type']})")
            
            # Show preview dialog
            self._show_preview_dialog(questions)
            
        except Exception as e:
            print(f"Error creating preview: {e}")
            import traceback
            traceback.print_exc()
            toast(f"Error creating preview: {str(e)}")
    
    def _show_preview_dialog(self, questions):
        """Show the form preview dialog with improved UI"""
        try:
            from kivymd.uix.card import MDCard
            from kivymd.uix.label import MDLabel, MDIcon
            from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
            from kivymd.uix.boxlayout import MDBoxLayout
            from kivy.uix.popup import Popup
            from kivymd.uix.scrollview import MDScrollView
            from kivy.metrics import dp
            from kivy.app import App
            
            app = App.get_running_app()
            
            # Main container with Material Design styling
            main_container = MDBoxLayout(
                orientation='vertical',
                spacing=0,
                md_bg_color=(0.97, 0.97, 0.97, 1)  # Light gray background
            )
            
            # Header with better contrast
            header = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height=dp(70),
                elevation=3,
                md_bg_color=(0.1, 0.4, 0.8, 1),  # Darker blue for better contrast
                padding=dp(16),
                radius=[12, 12, 0, 0]
            )
            
            header_layout = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(12)
            )
            
            # Preview icon
            header_icon = MDIcon(
                icon="eye",  # Eye icon for preview
                size_hint=(None, None),
                size=(dp(32), dp(32)),
                theme_icon_color="Custom",
                icon_color=(1, 1, 1, 1)
            )
            header_layout.add_widget(header_icon)
            
            # Title and subtitle
            title_container = MDBoxLayout(orientation='vertical', spacing=dp(2))
            
            title_label = MDLabel(
                text="Form Preview",
                font_style="Headline",
                role="medium",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),  # Pure white for maximum contrast
                bold=True
            )
            title_container.add_widget(title_label)
            
            subtitle_label = MDLabel(
                text=f"{len(questions)} question{'s' if len(questions) != 1 else ''} ready for review",
                font_style="Body",
                role="small",
                theme_text_color="Custom",
                text_color=(0.95, 0.95, 0.95, 1)  # Lighter for better readability
            )
            title_container.add_widget(subtitle_label)
            
            header_layout.add_widget(title_container)
            header.add_widget(header_layout)
            main_container.add_widget(header)
            
            # Content area with proper padding
            content_container = MDBoxLayout(
                orientation='vertical',
                padding=[dp(16), dp(12), dp(16), dp(12)],
                spacing=dp(8)
            )
            
            # Scrollable questions area
            scroll = MDScrollView(
                bar_width=dp(4),
                scroll_type=['bars'],
                do_scroll_x=False
            )
            
            questions_layout = MDBoxLayout(
                orientation='vertical',
                spacing=dp(12),
                size_hint_y=None,
                height=dp(0),  # Will be calculated
                padding=[0, dp(8), 0, dp(8)]
            )
            
            total_height = 0
            
            # Create individual question cards
            for i, q in enumerate(questions):
                question_text = q.get('question', 'No question text')
                question_number = q.get('number', i + 1)
                question_type = q.get('type', 'Unknown')
                is_required = q.get('required', True)
                
                # Question card with nice styling
                question_card = MDCard(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(90) if 'options' not in q or not q['options'] else dp(120),
                    elevation=2,
                    md_bg_color=(1, 1, 1, 1),  # Pure white for cards
                    padding=dp(12),
                    spacing=dp(6),
                    radius=[8, 8, 8, 8]
                )
                
                # Question header
                question_header = MDBoxLayout(
                    orientation='horizontal',
                    spacing=dp(8),
                    size_hint_y=None,
                    height=dp(24)
                )
                
                # Question number badge
                number_badge = MDLabel(
                    text=f"Q{question_number}",
                    font_style="Label",
                    role="medium",
                    theme_text_color="Custom",
                    text_color=(0.1, 0.4, 0.8, 1),  # Dark blue for good contrast
                    bold=True,
                    size_hint=(None, None),
                    size=(dp(32), dp(24)),
                    halign="center"
                )
                question_header.add_widget(number_badge)
                
                # Question type and required status
                type_required_layout = MDBoxLayout(orientation='horizontal', spacing=dp(8))
                
                type_label = MDLabel(
                    text=question_type,
                    font_style="Label",
                    role="small",
                    theme_text_color="Custom",
                    text_color=(0.4, 0.4, 0.4, 1),  # Dark gray for better readability
                    size_hint_x=1
                )
                type_required_layout.add_widget(type_label)
                
                if is_required:
                    required_layout = MDBoxLayout(
                        orientation='horizontal',
                        spacing=dp(4),
                        size_hint=(None, None),
                        size=(dp(80), dp(20))
                    )
                    
                    required_icon = MDIcon(
                        icon="star",
                        size_hint=(None, None),
                        size=(dp(14), dp(14)),
                        theme_icon_color="Custom",
                        icon_color=(0.8, 0.2, 0.2, 1)
                    )
                    required_layout.add_widget(required_icon)
                    
                    required_label = MDLabel(
                        text="Required",
                        font_style="Label",
                        role="small",
                        theme_text_color="Custom",
                        text_color=(0.8, 0.2, 0.2, 1),
                        size_hint_x=1
                    )
                    required_layout.add_widget(required_label)
                    type_required_layout.add_widget(required_layout)
                
                question_header.add_widget(type_required_layout)
                question_card.add_widget(question_header)
                
                # Question text
                question_label = MDLabel(
                    text=question_text if question_text else "[No question text]",
                    font_style="Body",
                    role="medium",
                    theme_text_color="Custom",
                    text_color=(0.1, 0.1, 0.1, 1) if question_text else (0.5, 0.5, 0.5, 1),  # Dark text for readability
                    text_size=(None, None),
                    size_hint_y=None,
                    height=dp(20),
                    italic=not bool(question_text)
                )
                question_card.add_widget(question_label)
                
                # Options (if any)
                if 'options' in q and q['options']:
                    options_text = ', '.join(q['options'][:3])
                    if len(q['options']) > 3:
                        options_text += f" (+{len(q['options']) - 3} more)"
                    
                    options_label = MDLabel(
                        text=f"Options: {options_text}",
                        font_style="Body",
                        role="small",
                        theme_text_color="Custom",
                        text_color=(0.3, 0.3, 0.3, 1),  # Medium gray for options
                        text_size=(None, None),
                        size_hint_y=None,
                        height=dp(16)
                    )
                    question_card.add_widget(options_label)
                
                # Scale info (if any)
                if 'scale_info' in q:
                    scale_label = MDLabel(
                        text=q['scale_info'],
                        font_style="Body",
                        role="small",
                        theme_text_color="Custom",
                        text_color=(0.3, 0.3, 0.3, 1),  # Medium gray for scale info
                        text_size=(None, None),
                        size_hint_y=None,
                        height=dp(16)
                    )
                    question_card.add_widget(scale_label)
                
                questions_layout.add_widget(question_card)
                total_height += question_card.height + dp(12)
            
            # Set the calculated height
            questions_layout.height = total_height
            scroll.add_widget(questions_layout)
            content_container.add_widget(scroll)
            
            main_container.add_widget(content_container)
            
            # Footer with action buttons
            footer = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(12),
                size_hint_y=None,
                height=dp(60),
                padding=[dp(16), dp(8), dp(16), dp(16)]
            )
            
            # Add spacer
            footer.add_widget(MDBoxLayout(size_hint_x=1))
            
            # Close button with icon
            close_btn = MDButton(
                style="filled",
                size_hint=(None, None),
                size=(dp(100), dp(40)),
                md_bg_color=(0.1, 0.4, 0.8, 1)  # Same as header for consistency
            )
            close_btn.add_widget(MDButtonIcon(icon="close", icon_color=(1, 1, 1, 1)))
            close_btn.add_widget(MDButtonText(text="Close", text_color=(1, 1, 1, 1)))
            footer.add_widget(close_btn)
            
            main_container.add_widget(footer)
            
            # Create popup with better styling
            popup = Popup(
                title="",
                content=main_container,
                size_hint=(0.85, 0.85),
                auto_dismiss=True,
                background_color=(0, 0, 0, 0.3),  # Semi-transparent background
                separator_color=(0, 0, 0, 0)  # Hide default separator
            )
            
            close_btn.on_release = popup.dismiss
            popup.open()
            
        except Exception as e:
            print(f"Error creating preview dialog: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to simple toast
            preview_summary = f"Form has {len(questions)} questions"
            if questions:
                preview_summary += f": {', '.join([q.get('question', f'Q{i}')[:20] + ('...' if len(q.get('question', '')) > 20 else '') for i, q in enumerate(questions[:3], 1)])}"
                if len(questions) > 3:
                    preview_summary += f" and {len(questions)-3} more"
            toast(preview_summary, duration=4)
    
    def reset_form(self):
        """Reset the form to initial state"""
        if hasattr(self.ids, 'form_canvas'):
            self.ids.form_canvas.clear_widgets()
            
            # Show empty state
            from kivy.lang import Builder
            empty_state = Builder.load_string('''
EmptyFormState:
    id: 'empty_state'
''')
            self.ids.form_canvas.add_widget(empty_state)
        
        self.project_id = None
        self.questions_data = []
    
    def _remove_empty_state(self):
        """Remove the empty state widget"""
        if hasattr(self.ids, 'form_canvas'):
            for child in list(self.ids.form_canvas.children):
                if hasattr(child, 'id') and getattr(child, 'id', None) == 'empty_state':
                    self.ids.form_canvas.remove_widget(child)
                    break
    
    def _remove_no_projects_state(self):
        """Remove the no projects state widget"""
        if hasattr(self.ids, 'form_canvas'):
            for child in list(self.ids.form_canvas.children):
                if hasattr(child, 'id') and getattr(child, 'id', None) == 'no_projects_state':
                    self.ids.form_canvas.remove_widget(child)
                    break
    
    def _load_projects_and_select(self, selected_project):
        """Load projects and auto-select a specific project"""
        try:
            # First load all projects
            self.load_projects()
            
            # Then auto-select the specific project after a delay
            Clock.schedule_once(lambda dt: self._auto_select_project(selected_project), 1.0)
        except Exception as e:
            print(f"Error in _load_projects_and_select: {e}")
    
    def _auto_select_project(self, project_data):
        """Auto-select a specific project"""
        try:
            project_name = project_data.get('name')
            if project_name and project_name in self.project_map:
                self.on_project_selected(project_name)
                toast(f"Ready to build form for '{project_name}'!")
            else:
                print(f"Project '{project_name}' not found in project map")
        except Exception as e:
            print(f"Error in _auto_select_project: {e}")
    
    def show_loading(self, show=True, message="Loading..."):
        """Show or hide loading overlay"""
        if not hasattr(self.ids, 'loading_overlay'):
            return
        
        if show:
            self.ids.loading_overlay.opacity = 1
            self.ids.loading_overlay.disabled = False  # Enable touch events when showing
            if hasattr(self.ids, 'progress_spinner'):
                self.ids.progress_spinner.active = True
            if hasattr(self.ids, 'loading_message'):
                self.ids.loading_message.text = message
        else:
            self.ids.loading_overlay.opacity = 0
            self.ids.loading_overlay.disabled = True   # Disable touch events when hiding
            if hasattr(self.ids, 'progress_spinner'):
                self.ids.progress_spinner.active = False