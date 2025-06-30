from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp

from kivymd.toast import toast
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.slider import MDSlider
from kivymd.uix.widget import Widget
from kivymd.uix.card import MDCard

import json
import threading

Builder.load_file("kv/collect_data.kv")

class DataCollectionScreen(Screen):
    project_id = StringProperty(None, allownone=True)
    project_list = ListProperty([])
    project_map = {}
    project_menu = None
    questions_data = []
    response_widgets = []
    current_respondent_id = StringProperty(None, allownone=True)

    def on_enter(self):
        Clock.schedule_once(self._delayed_load, 0)

    def _delayed_load(self, dt):
        self.load_projects()

    def load_projects(self):
        app = App.get_running_app()
        conn = app.db_service.get_db_connection()
        try:
            cursor = conn.cursor()
            user_id = app.auth_service.get_user_data().get('id')
            if user_id:
                cursor.execute("SELECT id, name FROM projects WHERE user_id = ? ORDER BY name", (user_id,))
            else:
                cursor.execute("SELECT id, name FROM projects ORDER BY name")
            projects = cursor.fetchall()
            if not projects:
                toast("No projects found. Redirecting to Projects page.")
                try:
                    if self.manager and hasattr(self.manager, 'screen_names') and 'projects' in self.manager.screen_names:
                        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'projects'), 0.5)
                except Exception as e:
                    print(f"Screen transition error: {e}")
                return  # Prevent further code execution
            self.project_list = [p['name'] for p in projects]
            self.project_map = {p['name']: p['id'] for p in projects}
            self.project_id = None
            self.current_respondent_id = None
            self.ids.project_spinner.text = 'Select Project'
            self.ids.form_canvas.clear_widgets()
            self._update_submit_button()
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
        if self.project_menu:
            self.project_menu.dismiss()
        if text == 'Select Project' or text not in self.project_map:
            self.project_id = None
            self.current_respondent_id = None
            self.ids.project_spinner.text = 'Select Project'
            self.ids.form_canvas.clear_widgets()
            self._update_submit_button()
            return
        self.project_id = self.project_map[text]
        self.ids.project_spinner.text = text
        self.current_respondent_id = None
        self.load_form()
        self._update_submit_button()

    def load_form(self):
        """Load the form questions for the selected project"""
        self.ids.form_canvas.clear_widgets()
        self.response_widgets = []
        
        # Hide empty state if it exists
        if hasattr(self.ids.form_canvas, 'children'):
            for child in self.ids.form_canvas.children:
                if hasattr(child, 'id') and child.id == 'empty_state':
                    child.opacity = 0
        
        app = App.get_running_app()
        questions, error = app.form_service.load_questions(self.project_id)
        if error:
            toast(f"Error loading form: {error}")
            self._show_empty_state("Error loading form", error)
            return
            
        if not questions:
            self._show_empty_state("No questions found", "This form doesn't have any questions yet")
            return
            
        self.questions_data = questions
        for i, q in enumerate(questions):
            widget = self.create_question_widget(q, i)
            self.ids.form_canvas.add_widget(widget)
            self.response_widgets.append((q, widget))

    def create_question_widget(self, q, index):
        """Create UI widget for a question"""
        q_type = q.get('question_type', 'text')
        q_text = q.get('question_text', '')
        options = q.get('options') or []
        if isinstance(options, str):
            try:
                options = json.loads(options)
            except Exception:
                options = []
        allow_multiple = bool(q.get('allow_multiple', False))
        
        # Create question container with card-like styling
        container = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            padding=dp(16),
            spacing=dp(12),
            elevation=1
        )

        # Question header with number
        header = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(32),
            spacing=dp(12)
        )

        # Question number circle - simplified for KivyMD 1.2.0
        number_box = MDBoxLayout(
            size_hint=(None, None),
            size=(dp(32), dp(32)),
            padding=dp(0)
        )
        number_box.md_bg_color = App.get_running_app().theme_cls.primary_color
        
        number_label = MDLabel(
            text=str(index + 1),
            halign='center',
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            bold=True
        )
        number_box.add_widget(number_label)

        # Question text
        question_label = MDLabel(
            text=q_text,
            font_style="Subtitle1",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(32)
        )

        header.add_widget(number_box)
        header.add_widget(question_label)
        container.add_widget(header)

        # Answer section with light background
        answer_box = MDBoxLayout(
            orientation='vertical',
            spacing=dp(8),
            padding=[dp(8), dp(8), dp(8), dp(8)],
            size_hint_y=None,
            md_bg_color=[0.95, 0.95, 0.95, 1],
            radius=[dp(4)]
        )

        if q_type in ['text', 'long_text', 'numeric', 'date', 'location']:
            hint = {
                'text': "Your answer",
                'long_text': "Your answer",
                'numeric': "Enter a number",
                'date': "YYYY-MM-DD",
                'location': "Location (lat,lon)"
            }.get(q_type, "Your answer")

            field = MDTextField(
                hint_text=hint,
                mode="rectangle",
                multiline=q_type == 'long_text',
                input_filter='int' if q_type == 'numeric' else None,
                size_hint_y=None,
                height=dp(48) if not q_type == 'long_text' else dp(96),
                font_size="16sp"
            )
            answer_box.add_widget(field)
            answer_box.height = field.height + dp(16)  # Add padding
            container.response_field = field

        elif q_type == 'choice':
            options_box = MDBoxLayout(
                orientation='vertical',
                spacing=dp(4),
                size_hint_y=None,
                height=len(options) * dp(40)
            )
            checks = []
            for opt in options:
                row = MDBoxLayout(
                    orientation='horizontal',
                    spacing=dp(12),
                    size_hint_y=None,
                    height=dp(40)
                )

                cb = MDCheckbox(
                    group=q_text if not allow_multiple else None,
                    size_hint=(None, None),
                    size=(dp(32), dp(32)),
                    pos_hint={'center_y': 0.5}
                )

                label = MDLabel(
                    text=opt,
                    theme_text_color="Primary",
                    size_hint_x=1,
                    pos_hint={'center_y': 0.5}
                )

                row.add_widget(cb)
                row.add_widget(label)
                options_box.add_widget(row)
                checks.append((cb, opt))
            answer_box.add_widget(options_box)
            answer_box.height = options_box.height + dp(16)  # Add padding
            container.response_field = checks

        elif q_type == 'scale':
            scale_box = MDBoxLayout(
                orientation='vertical',
                spacing=dp(4),
                size_hint_y=None,
                height=dp(60)
            )
            
            slider = MDSlider(
                min=1,
                max=5,
                value=3,
                step=1,
                size_hint_y=None,
                height=dp(40),
                hint=False
            )
            
            value_label = MDLabel(
                text="3",
                halign='center',
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(20)
            )
            
            def update_value(instance, value):
                value_label.text = str(int(value))
            
            slider.bind(value=update_value)
            
            scale_box.add_widget(slider)
            scale_box.add_widget(value_label)
            answer_box.add_widget(scale_box)
            answer_box.height = scale_box.height + dp(16)  # Add padding
            container.response_field = slider

        elif q_type == 'photo':
            photo_box = MDBoxLayout(
                orientation='vertical',
                spacing=dp(8),
                size_hint_y=None,
                height=dp(80)
            )
            
            field = MDLabel(
                text="[Photo upload not implemented]",
                font_style="Caption",
                theme_text_color="Secondary",
                halign='center'
            )
            photo_box.add_widget(field)
            answer_box.add_widget(photo_box)
            answer_box.height = photo_box.height + dp(16)  # Add padding
            container.response_field = None

        container.add_widget(answer_box)
        container.height = header.height + answer_box.height + dp(32)  # Total height plus padding
        return container

    def _update_submit_button(self):
        """Update submit button text based on current state"""
        if self.project_id:
            if self.current_respondent_id:
                self.ids.submit_button.text = "Submit Additional Response"
            else:
                self.ids.submit_button.text = "Submit New Response"
        else:
            self.ids.submit_button.text = "Submit"

    def submit_response(self):
        """Submit the form response - creates respondent and responses"""
        if not self.project_id:
            toast("Please select a project first")
            return
        
        if not self.response_widgets:
            toast("No form questions loaded")
            return
        
        # Show loading
        self.ids.submit_button.text = "Submitting..."
        self.ids.submit_button.disabled = True
        
        # Start submission in background thread
        threading.Thread(target=self._submit_in_thread, daemon=True).start()

    def _submit_in_thread(self):
        """Background thread for form submission"""
        try:
            app = App.get_running_app()
            
            # Collect responses from UI
            responses_data = []
            has_responses = False
            
            for q, widget in self.response_widgets:
                q_type = q.get('question_type', 'text')
                answer = None
                
                if q_type in ('text', 'long_text', 'numeric', 'date', 'location'):
                    answer = widget.response_field.text if widget.response_field else None
                elif q_type == 'choice':
                    if bool(q.get('allow_multiple', False)):
                        answer = [opt for cb, opt in widget.response_field if cb.active]
                        if answer:  # Only count if there's an actual selection
                            answer = json.dumps(answer)
                    else:
                        for cb, opt in widget.response_field:
                            if cb.active:
                                answer = opt
                                break
                elif q_type == 'scale':
                    answer = int(widget.response_field.value) if widget.response_field else None
                elif q_type == 'photo':
                    answer = None

                # Only include questions that have been answered
                if answer is not None and str(answer).strip():
                    has_responses = True
                    responses_data.append({
                        'question_id': q.get('id'),
                        'response_value': str(answer),
                        'metadata': {
                            'question_type': q_type,
                            'question_text': q.get('question_text', '')
                        }
                    })
            
            if not has_responses:
                Clock.schedule_once(lambda dt: toast("Please answer at least one question"))
                Clock.schedule_once(lambda dt: self._reset_submit_button())
                return
            
            # Create respondent if this is a new form submission
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
                location_data=None,  # Could add GPS location here
                device_info=None     # Could add device info here
            )
            
            # Update UI on main thread
            Clock.schedule_once(lambda dt: self._handle_submission_success(result))
            
        except Exception as e:
            error_message = str(e)  # Capture the error message
            print(f"Error submitting form: {error_message}")
            Clock.schedule_once(lambda dt: toast(f"Error submitting form: {error_message}"))
            Clock.schedule_once(lambda dt: self._reset_submit_button())

    def _handle_submission_success(self, result):
        """Handle successful form submission"""
        toast(result['message'])
        
        # Clear the form for next respondent
        self.current_respondent_id = None
        self._clear_form()
        self._reset_submit_button()
        
        print(f"Form submitted successfully: {result}")

    def _clear_form(self):
        """Clear all form inputs"""
        for q, widget in self.response_widgets:
            q_type = q.get('question_type', 'text')
            
            if q_type in ('text', 'long_text', 'numeric', 'date', 'location'):
                if widget.response_field:
                    widget.response_field.text = ""
            elif q_type == 'choice':
                for cb, opt in widget.response_field:
                    cb.active = False
            elif q_type == 'scale':
                if widget.response_field:
                    widget.response_field.value = 3

    def _reset_submit_button(self):
        """Reset submit button to normal state"""
        self.ids.submit_button.disabled = False
        self._update_submit_button()

    def _show_empty_state(self, title="No form loaded", message="Select a project to load its form"):
        """Show empty state with custom message"""
        if hasattr(self.ids.form_canvas, 'children'):
            for child in self.ids.form_canvas.children:
                if hasattr(child, 'id') and child.id == 'empty_state':
                    # Update existing empty state
                    for widget in child.children:
                        if isinstance(widget, MDLabel):
                            if widget.font_style == "H6":
                                widget.text = title
                            elif widget.font_style == "Body2":
                                widget.text = message
                    child.opacity = 1
                    return
                    
        # Create new empty state if not found
        empty_state = MDBoxLayout(
            orientation='vertical',
            spacing=dp(16),
            size_hint_y=None,
            height=dp(200),
            opacity=1
        )
        empty_state.id = 'empty_state'
        
        empty_state.add_widget(MDBoxLayout(size_hint_y=None, height=dp(40)))
        
        # Use MDLabel for icon in KivyMD 1.2.0
        icon_label = MDLabel(
            text="📋",  # Using emoji instead of icon
            halign="center",
            font_size="48sp",
            size_hint_y=None,
            height=dp(64),
            theme_text_color="Hint"
        )
        empty_state.add_widget(icon_label)
        
        title_label = MDLabel(
            text=title,
            font_style="H6",
            theme_text_color="Hint",
            halign="center",
            font_size="18sp"
        )
        empty_state.add_widget(title_label)
        
        message_label = MDLabel(
            text=message,
            font_style="Body2",
            theme_text_color="Hint",
            halign="center",
            font_size="14sp"
        )
        empty_state.add_widget(message_label)
        
        self.ids.form_canvas.add_widget(empty_state)
