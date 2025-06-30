from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from widgets.form_fields import (
    ShortTextField, LongTextField, NumericIntegerField, NumericDecimalField,
    SingleChoiceField, MultipleChoiceField, RatingScaleField, DateField, 
    DateTimeField, LocationPickerField, PhotoUploadField, AudioRecordingField, 
    BarcodeField, create_form_field
)
from widgets.questionBlock import QuestionBlock
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty
from kivy.app import App
from kivymd.toast import toast
import threading
from kivymd.uix.menu import MDDropdownMenu

from kivy.lang import Builder

import uuid
import json

from services.form_service import FormService

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
            'image': 'Photo/Image',
            'audio': 'Audio Recording',
            'barcode': 'Barcode/QR Code',
        }
    
    def on_enter(self):
        """Called when the screen is entered."""
        try:
            # Set the title
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
        except Exception as e:
            print(f"Error in form builder on_enter: {e}")
            toast(f"Error initializing Form Builder: {str(e)}")
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'dashboard'), 1)

    def load_projects(self):
        """Loads all projects from the local DB and populates the spinner."""
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
        
        conn = app.db_service.get_db_connection()
        try:
            cursor = conn.cursor()
            user_id = user_data.get('id')
            cursor.execute("SELECT id, name FROM projects WHERE user_id = ? ORDER BY name", (user_id,))
            projects = cursor.fetchall()
            
            if not projects:
                # Instead of redirecting, show a helpful message and allow user to create projects
                toast("No projects found. Create a project first to build forms.")
                self.project_list = []
                self.project_map = {}
                if hasattr(self.ids, 'project_spinner'):
                    self.ids.project_spinner.text = 'No Projects Available'
                self.project_id = None
                self.ids.form_canvas.clear_widgets()
                
                # Add a helpful widget to the form canvas
                help_layout = MDBoxLayout(
                    orientation='vertical',
                    spacing=dp(16),
                    adaptive_height=True,
                    size_hint_y=None,
                    height=dp(200)
                )
                
                help_label = MDLabel(
                    text="No projects found!\n\nTo create forms, you need to have at least one project.\nGo to the Projects page to create a new project first.",
                    halign="center",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=dp(120)
                )
                
                go_to_projects_btn = MDRaisedButton(
                    text="Go to Projects",
                    size_hint=(None, None),
                    size=(dp(150), dp(40)),
                    pos_hint={'center_x': 0.5},
                    on_release=lambda x: setattr(self.manager, 'current', 'projects')
                )
                
                help_layout.add_widget(help_label)
                help_layout.add_widget(go_to_projects_btn)
                self.ids.form_canvas.add_widget(help_layout)
                
                print(f"No projects found for user {user_id}")
                return
                
            self.project_list = [p['name'] for p in projects]
            self.project_map = {p['name']: p['id'] for p in projects}
            if hasattr(self.ids, 'project_spinner'):
                self.ids.project_spinner.text = 'Select Project'
            self.project_id = None
            self.ids.form_canvas.clear_widgets()
            
            print(f"Loaded {len(projects)} projects for user {user_id}")
            
        except Exception as e:
            print(f"Error loading projects: {e}")
            toast(f"Error loading projects: {str(e)}")
        finally:
            conn.close()

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
                return
            
            self.project_id = self.project_map[text]
            if hasattr(self.ids, 'project_spinner'):
                self.ids.project_spinner.text = text
            
            if hasattr(self.ids, 'top_bar'):
                self.ids.top_bar.set_title(f"Form for {text}")
            
            self.load_form()
        except Exception as e:
            print(f"Error selecting project: {e}")
            toast(f"Error selecting project: {str(e)}")

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
                Clock.schedule_once(lambda dt: self.show_loader(False))

        threading.Thread(target=_load_in_thread).start()

    def _update_ui_with_questions(self):
        """Populates the UI with question widgets using the new form fields."""
        for q_data in self.questions_data:
            # Get response type from the data
            response_type = q_data.get('question_type', 'text_short')
            question_text = q_data.get('question_text', '')
            options = q_data.get('options') or []
            
            # Parse options if they're stored as JSON string
            if isinstance(options, str):
                try:
                    options = json.loads(options)
                except:
                    options = []
            
            # Create the appropriate form field
            try:
                field = create_form_field(
                    response_type=response_type,
                    question_text=question_text,
                    options=options
                )
                
                # Set additional properties for choice fields
                if hasattr(field, 'selected_option') and response_type == 'choice_single':
                    # For single choice, we might want to set a default if available
                    pass
                elif hasattr(field, 'selected_options') and response_type == 'choice_multiple':
                    # For multiple choice, we might want to set defaults if available
                    pass
                
                self.ids.form_canvas.add_widget(field)
                
            except Exception as e:
                print(f"Error creating form field for question {question_text}: {e}")
                # Fallback to basic text field
                field = create_form_field(
                    response_type='text_short',
                    question_text=question_text
                )
                self.ids.form_canvas.add_widget(field)

    def add_question(self, response_type):
        """Adds a new question widget to the form canvas."""
        if not self.project_id:
            toast("Select a project first.")
            return
        
        try:
            # Create a new form field based on response type
            display_name = self.response_type_display.get(response_type, response_type)
            field = create_form_field(
                response_type=response_type,
                question_text=f"New {display_name} Question",
                options=['Option 1', 'Option 2'] if 'choice' in response_type else None
            )
            
            self.ids.form_canvas.add_widget(field)
            toast(f"Added {display_name} question")
            
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
        
        for i, widget in enumerate(self.ids.form_canvas.children):
            # Check if widget is one of our form fields
            if hasattr(widget, 'response_type') and hasattr(widget, 'get_value'):
                question_text = widget.question_text.strip()
                response_type = widget.response_type
                
                # Validate question text
                if not question_text or question_text.startswith("New "):
                    validation_errors.append(f"Question {len(questions_to_save) + 1}: Please enter a proper question text")
                    continue
                
                # Get the value/options for choice fields
                options = []
                allow_multiple = False
                
                if hasattr(widget, 'options') and widget.options:
                    options = widget.options
                    if len(options) < 2 and 'choice' in response_type:
                        validation_errors.append(f"Question {len(questions_to_save) + 1}: Choice questions need at least 2 options")
                        continue
                
                if hasattr(widget, 'selected_options'):
                    allow_multiple = True
                
                # Validate field-specific requirements
                is_valid, field_errors = widget.validate()
                if not is_valid:
                    validation_errors.extend([f"Question {len(questions_to_save) + 1}: {error}" for error in field_errors])
                    continue
                
                # Map to backend format
                questions_to_save.append({
                    'question_text': question_text,
                    'response_type': response_type,  # Using the new response type format
                    'options': options,
                    'allow_multiple': allow_multiple,
                    'order_index': len(questions_to_save)
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
        
        # The widgets are added in reverse order, so we reverse the list back
        questions_to_save.reverse()

        def _save_in_thread():
            try:
                result = self.form_service.save_questions(self.project_id, questions_to_save)
                Clock.schedule_once(lambda dt: toast(result.get('message', 'Form saved.')))
            except Exception as e:
                error_message = str(e)  # Capture the error message
                Clock.schedule_once(lambda dt: toast(f"Error saving: {error_message}"))
            finally:
                Clock.schedule_once(lambda dt: self.show_loader(False))

        threading.Thread(target=_save_in_thread).start()

    def show_loader(self, show=True):
        self.ids.spinner.active = show
        self.ids.form_canvas.disabled = show

    def preview_questions(self):
        """Show a dialog previewing the current form questions."""
        questions = []
        for widget in self.ids.form_canvas.children:
            if hasattr(widget, 'response_type') and hasattr(widget, 'get_value'):
                response_type = widget.response_type
                question_text = widget.question_text
                display_name = self.response_type_display.get(response_type, response_type)
                
                q = {
                    'question': question_text,
                    'type': display_name
                }
                
                # Add options for choice fields
                if hasattr(widget, 'options') and widget.options:
                    q['options'] = widget.options
                    q['allow_multiple'] = hasattr(widget, 'selected_options')
                
                questions.append(q)
                
        questions.reverse()  # To match display order

        preview_layout = MDBoxLayout(orientation="vertical", spacing=dp(12), padding=dp(16), adaptive_height=True)
        if not questions:
            preview_layout.add_widget(MDLabel(text="No questions to preview.", font_style="Subtitle1"))
        else:
            for idx, q in enumerate(questions, 1):
                q_text = q.get('question', '')
                q_type = q.get('type', '')
                options = q.get('options', [])
                allow_multiple = q.get('allow_multiple', False)
                
                label = f"{idx}. {q_text}"
                preview_layout.add_widget(MDLabel(text=label, font_style="Subtitle1"))
                preview_layout.add_widget(MDLabel(text=f"Type: {q_type}", font_style="Caption"))
                
                if options:
                    for opt in options:
                        preview_layout.add_widget(MDLabel(text=f"- {opt}", font_style="Body2"))
                    if allow_multiple:
                        preview_layout.add_widget(MDLabel(text="(Multiple answers allowed)", font_style="Caption"))
                elif q_type in ["GPS Location", "Photo/Image", "Audio Recording", "Barcode/QR Code"]:
                    preview_layout.add_widget(MDLabel(text=f"[{q_type} input field]", font_style="Body2"))
                elif "Number" in q_type:
                    preview_layout.add_widget(MDLabel(text=f"[{q_type} input field]", font_style="Body2"))
                elif "Date" in q_type:
                    preview_layout.add_widget(MDLabel(text=f"[{q_type} picker]", font_style="Body2"))
                elif "Rating" in q_type:
                    preview_layout.add_widget(MDLabel(text="[Rating scale 1-5]", font_style="Body2"))
                else:
                    preview_layout.add_widget(MDLabel(text="[Text input field]", font_style="Body2"))
                    
                preview_layout.add_widget(MDLabel(text="", font_style="Body2"))  # Spacer

        dialog = MDDialog(
            title="Preview Questions",
            type="custom",
            content_cls=preview_layout,
            buttons=[
                MDRaisedButton(text="Close", on_release=lambda x: dialog.dismiss())
            ],
            auto_dismiss=True,
        )
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