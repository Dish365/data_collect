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
import uuid

Builder.load_file("kv/collect_data.kv")

class DataCollectionScreen(Screen):
    project_id = StringProperty(None, allownone=True)
    project_list = ListProperty([])
    project_map = {}
    project_menu = None
    questions_data = []
    response_widgets = []
    current_respondent_id = StringProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Tablet optimization attributes
        self.answered_questions = set()
        self.total_questions = 0
        self.progress_value = 0.0

    def on_enter(self):
        # Set top bar title for consistency
        if hasattr(self.ids, 'top_bar'):
            self.ids.top_bar.set_title("Collect Data")
        
        Clock.schedule_once(self._delayed_load, 0)
        # Apply responsive layout
        self.update_responsive_layout()

    def on_window_resize(self, width, height):
        """Handle window resize for responsive layout adjustments"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            
            category = ResponsiveHelper.get_screen_size_category()
            is_landscape = ResponsiveHelper.is_landscape()
            
            print(f"DataCollection: Window resized to {width}x{height} - {category} {'landscape' if is_landscape else 'portrait'}")
            
            # Update responsive layout
            self.update_responsive_layout()
            
        except Exception as e:
            print(f"Error handling window resize in data collection: {e}")

    def update_responsive_layout(self):
        """Update layout based on current screen size"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            
            category = ResponsiveHelper.get_screen_size_category()
            is_landscape = ResponsiveHelper.is_landscape()
            
            print(f"DataCollection: Updating responsive layout for {category} {'landscape' if is_landscape else 'portrait'}")
            
            # Adjust form container orientation
            self.update_form_layout(category, is_landscape)
            
        except Exception as e:
            print(f"Error updating responsive layout in data collection: {e}")

    def update_form_layout(self, category, is_landscape):
        """Update form layout based on screen size and orientation"""
        if not hasattr(self.ids, 'form_container'):
            return
            
        container = self.ids.form_container
        side_panel = self.ids.side_panel
        form_canvas = self.ids.form_canvas
        
        # Determine layout mode
        use_side_by_side = False
        
        if category == "large_tablet":
            use_side_by_side = True  # Always side-by-side on large tablets
            canvas_width = 0.7
            panel_width = 0.3
        elif category == "tablet":
            use_side_by_side = is_landscape  # Side-by-side only in landscape
            canvas_width = 0.65 if is_landscape else 1.0
            panel_width = 0.35 if is_landscape else 0.0
        elif category == "small_tablet":
            use_side_by_side = is_landscape  # Side-by-side only in landscape
            canvas_width = 0.75 if is_landscape else 1.0
            panel_width = 0.25 if is_landscape else 0.0
        else:  # phone
            use_side_by_side = False  # Always stacked on phones
            canvas_width = 1.0
            panel_width = 0.0
        
        # Apply layout changes
        if use_side_by_side:
            container.orientation = 'horizontal'
            form_canvas.size_hint_x = canvas_width
            side_panel.size_hint_x = panel_width
            side_panel.opacity = 1
        else:
            container.orientation = 'vertical'
            form_canvas.size_hint_x = 1.0
            side_panel.size_hint_x = 0.0
            side_panel.opacity = 0
        
        print(f"DataCollection: Set layout to {'side-by-side' if use_side_by_side else 'stacked'} for {category}")

    def _delayed_load(self, dt):
        self.load_projects()

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
            toast("No projects found. Create a project first to collect data.")
            self.project_list = []
            self.project_map = {}
            self.project_id = None
            self.current_respondent_id = None
            self.ids.project_spinner.text = 'No Projects Available'
            self._show_empty_state("No projects found", "Go to the Projects page to create a new project first.")
            self._update_submit_button()
            return
            
        self.project_list = [p['name'] for p in projects]
        self.project_map = {p['name']: p['id'] for p in projects}
        self.project_id = None
        self.current_respondent_id = None
        self.ids.project_spinner.text = 'Select Project'
        self.ids.form_canvas.clear_widgets()
        self._update_submit_button()
        
        print(f"Loaded {len(projects)} projects for user {user_id}")

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
        """Handle project selection with comprehensive error handling"""
        try:
            print(f"Project selected: {text}")
            
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
            
            print(f"Loading form for project ID: {self.project_id}")
            self.load_form()
            self._update_submit_button()
            
        except Exception as e:
            print(f"Error in on_project_selected: {e}")
            import traceback
            traceback.print_exc()
            toast(f"Error selecting project: {str(e)}")
            # Reset to safe state
            self.project_id = None
            self.current_respondent_id = None
            self.ids.project_spinner.text = 'Select Project'
            self.ids.form_canvas.clear_widgets()
            self._update_submit_button()

    def load_form(self):
        """Load the form questions for the selected project with tablet optimizations"""
        try:
            print(f"Starting to load form for project: {self.project_id}")
            
            self.ids.form_canvas.clear_widgets()
            self.response_widgets = []
            self.answered_questions = set()
            
            # Hide empty state if it exists and is still alive
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
            
            # Create tablet-optimized question widgets
            for i, q in enumerate(questions):
                try:
                    widget = self.create_tablet_question_widget(q, i)
                    self.ids.form_canvas.add_widget(widget)
                    self.response_widgets.append((q, widget))
                    self.track_answer_progress(q.get('id', ''))
                except Exception as e:
                    print(f"Error creating widget for question {i}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Show progress section and side panel
            self.show_form_controls()
            
            # Update progress tracking
            self.update_progress()
            
            # Populate side panel with question overview
            self.populate_question_overview()
            
            print("Form loading completed successfully")
            
        except Exception as e:
            print(f"Error in load_form: {e}")
            import traceback
            traceback.print_exc()
            toast(f"Error loading form: {str(e)}")
            self._show_empty_state("Error loading form", str(e))

    def create_tablet_question_widget(self, q, index):
        """Create tablet-optimized UI widget for a question"""
        try:
            print(f"Creating widget for question {index}: {q.get('question_text', 'No text')}")
            
            from widgets.responsive_layout import ResponsiveHelper
            
            category = ResponsiveHelper.get_screen_size_category()
            
            # Get responsive sizes
            if category == "large_tablet":
                container_padding = dp(24)
                container_spacing = dp(16)
                header_height = dp(40)
                font_sizes = {"title": "20sp", "text": "16sp", "hint": "14sp"}
                touch_targets = {"button": dp(48), "checkbox": dp(36)}
            elif category == "tablet":
                container_padding = dp(20)
                container_spacing = dp(14)
                header_height = dp(36)
                font_sizes = {"title": "18sp", "text": "15sp", "hint": "13sp"}
                touch_targets = {"button": dp(44), "checkbox": dp(32)}
            elif category == "small_tablet":
                container_padding = dp(18)
                container_spacing = dp(12)
                header_height = dp(34)
                font_sizes = {"title": "16sp", "text": "14sp", "hint": "12sp"}
                touch_targets = {"button": dp(42), "checkbox": dp(30)}
            else:  # phone
                container_padding = dp(16)
                container_spacing = dp(12)
                header_height = dp(32)
                font_sizes = {"title": "14sp", "text": "13sp", "hint": "11sp"}
                touch_targets = {"button": dp(40), "checkbox": dp(28)}
                
        except Exception as e:
            print(f"Error getting responsive sizes: {e}")
            # Fallback to tablet sizes
            container_padding = dp(20)
            container_spacing = dp(14)
            header_height = dp(36)
            font_sizes = {"title": "18sp", "text": "15sp", "hint": "13sp"}
            touch_targets = {"button": dp(44), "checkbox": dp(32)}

        try:
            q_type = q.get('question_type', 'text')
            q_text = q.get('question_text', '')
            q_id = q.get('id', '')
            options = q.get('options') or []
            
            if isinstance(options, str):
                try:
                    options = json.loads(options)
                except Exception as e:
                    print(f"Error parsing options JSON: {e}")
                    options = []
                    
            allow_multiple = bool(q.get('allow_multiple', False))
            
            print(f"Question type: {q_type}, Options: {options}")
            
            # Create enhanced question container
            container = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height=dp(120),  # Will be adjusted based on content
                padding=container_padding,
                spacing=container_spacing,
                elevation=2,  # Higher elevation for tablets
                radius=[dp(8)],  # Rounded corners
                md_bg_color=[1, 1, 1, 1]
            )
            container.question_id = q_id

            # Enhanced question header
            header = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=header_height,
                spacing=dp(16)
            )

            # Enhanced question number circle with answer status
            number_card = MDCard(
                size_hint=(None, None),
                size=(header_height, header_height),
                radius=[header_height/2],
                md_bg_color=App.get_running_app().theme_cls.primary_color,
                elevation=1
            )
            
            number_label = MDLabel(
                text=str(index + 1),
                halign='center',
                valign='center',
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                bold=True,
                font_size=font_sizes["text"]
            )
            number_card.add_widget(number_label)
            
            # Add answer status indicator
            status_indicator = MDCard(
                size_hint=(None, None),
                size=(dp(12), dp(12)),
                radius=[dp(6)],
                md_bg_color=[0.8, 0.8, 0.8, 1],  # Gray for unanswered
                elevation=0,
                pos_hint={'center_y': 0.5}
            )
            container.answer_status = status_indicator  # Store reference for updates

            # Enhanced question text with better typography
            question_label = MDLabel(
                text=q_text,
                font_style="Subtitle1",
                theme_text_color="Primary",
                size_hint_y=None,
                height=header_height,
                font_size=font_sizes["title"],
                text_size=(None, None),
                valign='center'
            )

            header.add_widget(number_card)
            header.add_widget(status_indicator)
            header.add_widget(question_label)
            container.add_widget(header)

            # Enhanced answer section
            answer_box = MDCard(
                orientation='vertical',
                spacing=dp(12),
                padding=dp(16),
                size_hint_y=None,
                md_bg_color=[0.97, 0.97, 0.97, 1],
                radius=[dp(6)],
                elevation=0
            )

            # Create appropriate input widget based on question type
            if q_type in ['text', 'long_text', 'numeric', 'date', 'location']:
                field = self.create_tablet_text_field(q_type, font_sizes, touch_targets)
                def on_answer_change(instance, value, q_id=q_id):
                    print(f"[DEBUG] Main on_answer_change fired for field id={id(instance)} value={value}")
                    self.track_answer_progress(q_id)
                field.bind(text=on_answer_change)
                answer_box.add_widget(field)
                answer_box.height = field.height + dp(32)
                container.response_field = field
            elif q_type in ['choice', 'choice_single', 'choice_multiple']:
                choice_widget, choice_height = self.create_tablet_choice_field(
                    options, allow_multiple, q_text, font_sizes, touch_targets
                )
                # choice_widget is a tuple of (widget, list_of_checkboxes)
                if isinstance(choice_widget, tuple):
                    widget_to_add, checkbox_list = choice_widget
                    answer_box.add_widget(widget_to_add)
                    container.response_field = checkbox_list
                else:
                    answer_box.add_widget(choice_widget)
                    container.response_field = choice_widget
                answer_box.height = choice_height + dp(32)
            elif q_type == 'scale':
                from widgets.form_fields import RatingScaleField
                scale_widget = RatingScaleField(question_text=q_text)
                answer_box.add_widget(scale_widget)
                answer_box.height = scale_widget.height + dp(32)
                container.response_field = scale_widget
            elif q_type in ['image', 'photo']:
                photo_widget, photo_height = self.create_tablet_photo_field(font_sizes, touch_targets)
                if photo_widget:
                    answer_box.add_widget(photo_widget)
                    answer_box.height = photo_height + dp(32)
                    container.response_field = photo_widget
            elif q_type == 'file':
                from widgets.form_fields import FileUploadField
                file_widget = FileUploadField(question_text=q_text)
                answer_box.add_widget(file_widget)
                answer_box.height = file_widget.height + dp(32)
                container.response_field = file_widget
            elif q_type == 'date':
                from widgets.form_fields import DateField
                date_widget = DateField(question_text=q_text)
                answer_box.add_widget(date_widget)
                answer_box.height = date_widget.height + dp(32)
                container.response_field = date_widget
            else:
                # Default to text field for unknown types
                field = self.create_tablet_text_field('text', font_sizes, touch_targets)
                def on_answer_change(instance, value, q_id=q_id):
                    print(f"[DEBUG] Main on_answer_change fired for field id={id(instance)} value={value}")
                    self.track_answer_progress(q_id)
                field.bind(text=on_answer_change)
                answer_box.add_widget(field)
                answer_box.height = field.height + dp(32)
                container.response_field = field
            container.add_widget(answer_box)
            # Bind answer events for progress tracking (only for non-text fields now)
            if q_type not in ['text', 'long_text', 'numeric', 'date', 'location']:
                self.bind_answer_events(container, q_type, q_id)

            # Calculate total height
            total_height = header_height + answer_box.height + container_padding * 2 + container_spacing
            container.height = total_height

            print(f"Successfully created widget for question {index}")
            return container
            
        except Exception as e:
            print(f"Error creating question widget: {e}")
            import traceback
            traceback.print_exc()
            
            # Return a simple error widget
            error_container = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height=dp(80),
                padding=dp(16),
                md_bg_color=[1, 0.8, 0.8, 1]  # Light red background
            )
            
            error_label = MDLabel(
                text=f"Error loading question {index + 1}",
                theme_text_color="Error",
                font_size="14sp"
            )
            error_container.add_widget(error_label)
            
            return error_container

    def create_tablet_text_field(self, q_type, font_sizes, touch_targets):
        """Create tablet-optimized text input field"""
        hint = {
            'text': "Enter your answer",
            'long_text': "Enter your detailed answer",
            'numeric': "Enter a number",
            'date': "YYYY-MM-DD",
            'location': "Location (latitude, longitude)"
        }.get(q_type, "Enter your answer")

        field = MDTextField(
            hint_text=hint,
            mode="rectangle",
            multiline=q_type == 'long_text',
            input_filter='int' if q_type == 'numeric' else None,
            size_hint_y=None,
            height=touch_targets["button"] * 2 if q_type == 'long_text' else touch_targets["button"],
            font_size=font_sizes["text"],
            line_color_focus=App.get_running_app().theme_cls.primary_color,
            line_color_normal=[0.7, 0.7, 0.7, 1]
        )
        
        # Add visual feedback for content
        def on_text_change(instance, value):
            if value and value.strip():
                # Field has content - show filled state
                instance.line_color_normal = [0.2, 0.8, 0.2, 1]  # Green border
                instance.hint_text_color = [0.2, 0.8, 0.2, 1]  # Green hint
            else:
                # Field is empty - show normal state
                instance.line_color_normal = [0.7, 0.7, 0.7, 1]  # Gray border
                instance.hint_text_color = [0.5, 0.5, 0.5, 1]  # Gray hint
        
        field.bind(text=on_text_change)
        print(f"[DEBUG] Created MDTextField with id={id(field)}")
        return field

    def create_tablet_choice_field(self, options, allow_multiple, question_text, font_sizes, touch_targets):
        """Create tablet-optimized choice field"""
        try:
            print(f"Creating choice field with {len(options)} options, allow_multiple: {allow_multiple}")
            
            options_box = MDBoxLayout(
                orientation='vertical',
                spacing=dp(8),
                size_hint_y=None
            )
            
            checks = []
            option_height = touch_targets["button"]
            
            # Ensure options is a list
            if not isinstance(options, list):
                print(f"Options is not a list: {type(options)}, converting to empty list")
                options = []
            
            # If no options, provide defaults
            if not options:
                print("No options provided, using defaults")
                options = ["Option 1", "Option 2"]
            
            for i, opt in enumerate(options):
                try:
                    # Ensure option is a string
                    opt_text = str(opt) if opt is not None else f"Option {i+1}"
                    
                    row = MDBoxLayout(
                        orientation='horizontal',
                        spacing=dp(16),
                        size_hint_y=None,
                        height=option_height,
                        padding=[dp(8), 0]
                    )

                    cb = MDCheckbox(
                        group=question_text if not allow_multiple else None,
                        size_hint=(None, None),
                        size=(touch_targets["checkbox"], touch_targets["checkbox"]),
                        pos_hint={'center_y': 0.5}
                    )

                    label = MDLabel(
                        text=opt_text,
                        theme_text_color="Primary",
                        size_hint_x=1,
                        pos_hint={'center_y': 0.5},
                        font_size=font_sizes["text"]
                    )

                    row.add_widget(cb)
                    row.add_widget(label)
                    options_box.add_widget(row)
                    checks.append((cb, opt_text))
                    
                except Exception as e:
                    print(f"Error creating option {i}: {e}")
                    continue
            
            total_height = len(checks) * (option_height + dp(8))
            options_box.height = total_height
            
            print(f"Successfully created choice field with {len(checks)} options")
            # Return tuple of (widget, checkbox_list) for proper handling
            return (options_box, checks), total_height
            
        except Exception as e:
            print(f"Error creating choice field: {e}")
            import traceback
            traceback.print_exc()
            
            # Return a simple error widget
            error_box = MDBoxLayout(
                orientation='vertical',
                spacing=dp(8),
                size_hint_y=None,
                height=dp(60)
            )
            
            error_label = MDLabel(
                text="Error creating choice field",
                theme_text_color="Error",
                font_size="14sp"
            )
            error_box.add_widget(error_label)
            
            return (error_box, []), dp(60)

    def create_tablet_scale_field(self, font_sizes, touch_targets):
        """Create tablet-optimized scale field"""
        scale_box = MDBoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(80)
        )
        
        # Scale labels
        labels_box = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(20)
        )
        
        for i in range(1, 6):
            label = MDLabel(
                text=str(i),
                halign='center',
                theme_text_color="Secondary",
                font_size=font_sizes["hint"]
            )
            labels_box.add_widget(label)
        
        slider = MDSlider(
            min=1,
            max=5,
            value=3,
            step=1,
            size_hint_y=None,
            height=touch_targets["button"],
            hint=False,
            color=App.get_running_app().theme_cls.primary_color
        )
        
        value_label = MDLabel(
            text="3",
            halign='center',
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(20),
            font_size=font_sizes["text"],
            bold=True
        )
        
        def update_value(instance, value):
            value_label.text = str(int(value))
        
        slider.bind(value=update_value)
        
        scale_box.add_widget(labels_box)
        scale_box.add_widget(slider)
        scale_box.add_widget(value_label)
        
        return slider, dp(80)

    def create_tablet_photo_field(self, font_sizes, touch_targets):
        """Create tablet-optimized photo field placeholder"""
        photo_box = MDBoxLayout(
            orientation='vertical',
            spacing=dp(12),
            size_hint_y=None,
            height=dp(100)
        )
        
        placeholder_button = MDRaisedButton(
            text="📷 Photo Upload (Coming Soon)",
            size_hint_y=None,
            height=touch_targets["button"],
            font_size=font_sizes["text"],
            disabled=True,
            md_bg_color=[0.8, 0.8, 0.8, 1]
        )
        
        note_label = MDLabel(
            text="Photo upload functionality will be available in future updates",
            font_style="Caption",
            theme_text_color="Secondary",
            halign='center',
            font_size=font_sizes["hint"]
        )
        
        photo_box.add_widget(placeholder_button)
        photo_box.add_widget(note_label)
        
        return None, dp(100)

    def bind_answer_events(self, container, q_type, q_id):
        """Bind events to track answer changes for progress updates"""
        try:
            def on_answer_change(instance, value):
                print(f"[DEBUG] Main on_answer_change fired for field id={id(instance)} value={value}")
                try:
                    self.track_answer_progress(q_id)
                except Exception as e:
                    print(f"Error in answer change callback: {e}")
            print(f"[DEBUG] Binding main answer event for field id={id(container.response_field)} q_id={q_id}, q_type={q_type}, has response_field: {hasattr(container, 'response_field')}")
            # Only bind for non-text fields now
            if q_type in ['choice', 'choice_single', 'choice_multiple']:
                if hasattr(container, 'response_field') and container.response_field:
                    for cb, opt in container.response_field:
                        cb.bind(active=on_answer_change)
            elif q_type == 'scale':
                if hasattr(container, 'response_field') and container.response_field:
                    container.response_field.bind(value=on_answer_change)
        except Exception as e:
            print(f"Error binding answer events: {e}")
            import traceback
            traceback.print_exc()

    def track_answer_progress(self, question_id):
        """Track progress when answers change, adding or removing from answered_questions as needed."""
        try:
            print(f"[DEBUG] track_answer_progress called for question_id={question_id}")
            # Find the widget for this question_id
            widget = None
            for q, w in self.response_widgets:
                if q.get('id', '') == question_id:
                    widget = w
                    break
            if not widget:
                print(f"No widget found for question_id {question_id}")
                self.update_progress()
                return
            # Determine if the question is currently answered
            is_answered = False
            q_type = None
            for q, w in self.response_widgets:
                if q.get('id', '') == question_id:
                    q_type = q.get('question_type', 'text')
                    break
            # Expanded type check for all text/numeric input types
            if q_type in ('text', 'long_text', 'numeric', 'date', 'location', 'text_short', 'text_long', 'numeric_integer', 'numeric_decimal'):
                if hasattr(widget, 'response_field') and widget.response_field:
                    value = getattr(widget.response_field, 'text', None)
                    print(f"[DEBUG] Value in text field for question_id={question_id}: '{value}'")
                    if value is not None and str(value).strip():
                        is_answered = True
            elif q_type in ('choice', 'choice_single', 'choice_multiple'):
                if hasattr(widget, 'response_field') and widget.response_field:
                    is_answered = any(cb.active for cb, opt in widget.response_field)
            elif q_type == 'scale':
                if hasattr(widget, 'response_field') and widget.response_field:
                    # Consider scale answered if value is not None
                    is_answered = widget.response_field.value is not None
            if is_answered:
                self.answered_questions.add(question_id)
                # Update visual indicator to green (answered)
                if hasattr(widget, 'answer_status'):
                    widget.answer_status.md_bg_color = [0.2, 0.8, 0.2, 1]  # Green
            else:
                self.answered_questions.discard(question_id)
                # Update visual indicator to gray (unanswered)
                if hasattr(widget, 'answer_status'):
                    widget.answer_status.md_bg_color = [0.8, 0.8, 0.8, 1]  # Gray
            print(f"[DEBUG] Answered questions after tracking: {self.answered_questions}")
            self.update_progress()
        except Exception as e:
            print(f"Error tracking answer progress: {e}")

    def update_progress(self):
        """Update progress bar and statistics"""
        try:
            print(f"[DEBUG] update_progress: {len(self.answered_questions)}/{self.total_questions}")
            if self.total_questions > 0:
                self.progress_value = len(self.answered_questions) / self.total_questions
                # Update progress bar
                if hasattr(self.ids, 'form_progress'):
                    self.ids.form_progress.value = self.progress_value * 100
                # Update progress text
                if hasattr(self.ids, 'progress_text'):
                    self.ids.progress_text.text = f"{len(self.answered_questions)}/{self.total_questions}"
                # Update question count
                if hasattr(self.ids, 'question_count_label'):
                    self.ids.question_count_label.text = f"{self.total_questions} Questions"
                # Update completion status
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
            # Show progress section
            if hasattr(self.ids, 'progress_section'):
                self.ids.progress_section.opacity = 1
            
            # Show side panel (if layout supports it)
            if hasattr(self.ids, 'side_panel'):
                # This will be controlled by update_form_layout based on screen size
                pass
            
            # Show form action buttons
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
                    q_text = q.get('question_text', '')
                    q_type = q.get('question_type', 'text')
                    
                    # Create overview item
                    item_card = MDCard(
                        orientation='horizontal',
                        size_hint_y=None,
                        height=dp(48),
                        padding=dp(8),
                        spacing=dp(8),
                        elevation=0.5,
                        radius=[dp(4)],
                        md_bg_color=[0.98, 0.98, 0.98, 1]
                    )
                    
                    # Question number
                    num_label = MDLabel(
                        text=str(i + 1),
                        size_hint_x=None,
                        width=dp(24),
                        halign='center',
                        font_size="12sp",
                        theme_text_color="Secondary"
                    )
                    
                    # Question text (truncated)
                    text = q_text[:30] + "..." if len(q_text) > 30 else q_text
                    text_label = MDLabel(
                        text=text,
                        font_size="11sp",
                        theme_text_color="Primary"
                    )
                    
                    # Question type indicator
                    type_icon = {
                        'text': "📝",
                        'long_text': "📄",
                        'numeric': "🔢",
                        'choice': "☑️",
                        'choice_single': "☑️",
                        'choice_multiple': "☑️",
                        'scale': "📊",
                        'date': "📅",
                        'location': "📍",
                        'photo': "📷"
                    }.get(q_type, "❓")
                    
                    type_label = MDLabel(
                        text=type_icon,
                        size_hint_x=None,
                        width=dp(24),
                        halign='center',
                        font_size="12sp"
                    )
                    
                    item_card.add_widget(num_label)
                    item_card.add_widget(text_label)
                    item_card.add_widget(type_label)
                    overview_box.add_widget(item_card)
                    
                except Exception as e:
                    print(f"Error creating overview item for question {i}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error populating question overview: {e}")
            import traceback
            traceback.print_exc()

    def clear_current_form(self):
        """Clear all form responses"""
        try:
            self._clear_form()
            self.answered_questions.clear()
            self.update_progress()
            toast("Form cleared")
        except Exception as e:
            print(f"Error clearing form: {e}")
            toast("Error clearing form")

    def save_draft(self):
        """Save current form as draft (placeholder functionality)"""
        try:
            # This is a placeholder - in a full implementation, you'd save to local storage
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

    def has_text_input_data(self, widget):
        """Return True if the widget's response_field has non-empty text, False otherwise."""
        print(f"Checking widget: {widget}")
        if hasattr(widget, 'response_field'):
            print(f"  response_field: {widget.response_field} (type: {type(widget.response_field)})")
            
            # Handle different types of response_field
            if hasattr(widget.response_field, 'text'):
                # Direct text field (MDTextField)
                value = widget.response_field.text
                print(f"  response_field.text: {value} (type: {type(value)})")
                if value is not None and str(value).strip():
                    print(f"Input field has data: '{value}'")
                    return True
                else:
                    print(f"Input field is empty or only spaces: '{value}'")
                    return False
            elif isinstance(widget.response_field, list):
                # Checkbox list for choice questions
                for cb, opt in widget.response_field:
                    if cb.active:
                        print(f"Checkbox selected: '{opt}'")
                        return True
                print("No checkboxes selected")
                return False
            elif hasattr(widget.response_field, 'value'):
                # Slider or other value-based widget
                value = widget.response_field.value
                print(f"  response_field.value: {value} (type: {type(value)})")
                if value is not None and str(value).strip():
                    print(f"Value field has data: '{value}'")
                    return True
                else:
                    print(f"Value field is empty: '{value}'")
                    return False
            else:
                print(f"Unknown response_field type: {type(widget.response_field)}")
                return False
        print("Widget has no response_field or response_field is None")
        return False

    def _submit_in_thread(self):
        """Background thread for form submission with tablet optimizations"""
        try:
            app = App.get_running_app()
            
            # Collect responses from UI with enhanced handling
            responses_data = []
            has_responses = False
            
            for q, widget in self.response_widgets:
                q_type = q.get('question_type', 'text')
                q_id = q.get('id', '')
                print(f"[DEBUG] Collecting answer for question: {q.get('question_text')} (type: {q_type}, id: {q_id})")
                print(f"[DEBUG] Widget: {widget}, type: {type(widget)}")
                print(f"[DEBUG] Widget dir: {dir(widget)}")
                if hasattr(widget, 'response_field'):
                    print(f"[DEBUG] Widget.response_field: {widget.response_field}, type: {type(widget.response_field)}")
                    print(f"[DEBUG] response_field dir: {dir(widget.response_field)}")
                else:
                    print(f"[DEBUG] Widget has NO response_field!")
                answer = None
                
                # Expanded type check for all text/numeric input types
                if q_type in ('text', 'long_text', 'numeric', 'date', 'location', 'text_short', 'text_long', 'numeric_integer', 'numeric_decimal'):
                    if hasattr(widget, 'response_field') and widget.response_field:
                        raw_value = widget.response_field.text
                        print(f"[DEBUG] Before submit: Question '{q.get('question_text')}' input text: '{raw_value}'")
                        print(f"[DEBUG] Text color: {getattr(widget.response_field, 'text_color', 'N/A')}, Background color: {getattr(widget.response_field, 'background_color', 'N/A')}")
                        answer = raw_value if raw_value is not None else ''
                        answer = answer.strip()
                        print(f"Stripped value in text input for '{q.get('question_text')}': '{answer}'")
                        if not answer:
                            print(f"Skipping empty answer for '{q.get('question_text')}'")
                            continue
                        # Additional validation for tablet input
                        if q_type in ('numeric', 'numeric_integer', 'numeric_decimal') and answer:
                            try:
                                float(answer)  # Validate numeric input
                            except ValueError:
                                Clock.schedule_once(lambda dt: toast(f"Invalid number format in question {q.get('question_text', '')[:30]}..."))
                                Clock.schedule_once(lambda dt: self._reset_submit_button())
                                return
                    else:
                        print(f"Skipping empty answer for '{q.get('question_text')}'")
                        continue
                elif q_type == 'choice' or q_type in ('choice_single', 'choice_multiple'):
                    if hasattr(widget, 'response_field'):
                        print(f"Checkbox states for '{q.get('question_text')}':")
                        for cb, opt in widget.response_field:
                            print(f"  Option: '{opt}', Checkbox active: {cb.active}")
                        if bool(q.get('allow_multiple', False)) or q_type == 'choice_multiple':
                            selected_options = [opt for cb, opt in widget.response_field if cb.active]
                            print(f"Selected options for '{q.get('question_text')}': {selected_options}")
                            if not selected_options:
                                print(f"Skipping empty choice for '{q.get('question_text')}'")
                                continue
                            answer = json.dumps(selected_options)
                        else:
                            found = False
                            for cb, opt in widget.response_field:
                                if cb.active:
                                    answer = opt
                                    found = True
                                    break
                            if not found:
                                print(f"Skipping empty single choice for '{q.get('question_text')}'")
                                continue
                elif q_type == 'scale':
                    if hasattr(widget, 'response_field') and widget.response_field:
                        answer = str(int(widget.response_field.value))
                        
                elif q_type == 'photo':
                    # Photo handling placeholder
                    answer = None

                # Enhanced response tracking
                if answer is not None and str(answer).strip():
                    has_responses = True
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
            print(f"Final collected responses_data: {responses_data}")
            print(f"Project ID: {self.project_id}, Respondent ID: {self.current_respondent_id}")
            
            # Check if any questions were answered
            if not responses_data:
                # Check if there are any questions that could be answered
                total_questions = len(self.questions_data)
                if total_questions == 0:
                    Clock.schedule_once(lambda dt: toast("No questions available in this form"))
                else:
                    Clock.schedule_once(lambda dt: toast(f"Please answer at least one question before submitting. You have {total_questions} question(s) to answer."))
                Clock.schedule_once(lambda dt: self._reset_submit_button())
                return
            
            # Enhanced progress tracking
            answered_count = len(responses_data)
            total_count = len(self.questions_data)
            completion_rate = (answered_count / total_count) * 100 if total_count > 0 else 0
            
            # Create respondent if this is a new form submission
            if not self.current_respondent_id:
                respondent_data = app.data_collection_service.create_respondent(
                    project_id=self.project_id,
                    is_anonymous=True,
                    consent_given=True
                )
                self.current_respondent_id = respondent_data['respondent_id']
            
            # Submit responses with enhanced metadata
            result = app.data_collection_service.submit_form_responses(
                project_id=self.project_id,
                respondent_id=self.current_respondent_id,
                responses_data=responses_data,
                location_data=None,  # Could add GPS location here
                device_info={
                    'device_type': self.get_device_type(),
                    'screen_dimensions': self.get_screen_dimensions(),
                    'completion_rate': completion_rate,
                    'answered_questions': answered_count,
                    'total_questions': total_count
                }
            )
            print(f"Submission result: {result}")
            # Update UI on main thread with enhanced feedback
            Clock.schedule_once(lambda dt: self._handle_submission_success_tablet(result, answered_count, total_count))
            
        except Exception as e:
            error_message = str(e)
            print(f"Error submitting form: {error_message}")
            Clock.schedule_once(lambda dt: toast(f"Submission error: {error_message}"))
            Clock.schedule_once(lambda dt: self._reset_submit_button())

    def get_device_type(self):
        """Get current device type for metadata"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
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

    def _handle_submission_success_tablet(self, result, answered_count, total_count):
        """Enhanced success handling for tablet interface"""
        # Show detailed success message
        completion_rate = int((answered_count / total_count) * 100) if total_count > 0 else 0
        success_message = f"✅ Response submitted successfully!\n{answered_count}/{total_count} questions answered ({completion_rate}%)"
        toast(success_message)
        
        # Clear the form for next respondent
        self.current_respondent_id = None
        self._clear_form()
        self.answered_questions.clear()
        self.update_progress()
        self._reset_submit_button()
        
        # Hide form controls until next form load
        self.hide_form_controls()
        
        print(f"Tablet form submitted successfully: {result}")

    def hide_form_controls(self):
        """Hide form controls after submission"""
        try:
            # Hide progress section until next form
            if hasattr(self.ids, 'progress_section'):
                self.ids.progress_section.opacity = 0
            
            # Hide action buttons
            if hasattr(self.ids, 'form_actions'):
                self.ids.form_actions.opacity = 0
                
            # Hide side panel
            if hasattr(self.ids, 'side_panel'):
                self.ids.side_panel.opacity = 0
                
        except Exception as e:
            print(f"Error hiding form controls: {e}")

    def _clear_form(self):
        """Enhanced form clearing for tablet widgets"""
        for q, widget in self.response_widgets:
            q_type = q.get('question_type', 'text')
            
            try:
                if q_type in ('text', 'long_text', 'numeric', 'date', 'location'):
                    if hasattr(widget, 'response_field') and widget.response_field:
                        widget.response_field.text = ""
                        
                elif q_type == 'choice':
                    if hasattr(widget, 'response_field'):
                        for cb, opt in widget.response_field:
                            cb.active = False
                            
                elif q_type == 'scale':
                    if hasattr(widget, 'response_field') and widget.response_field:
                        widget.response_field.value = 3  # Reset to middle value
                
                # Reset visual status indicator to gray (unanswered)
                if hasattr(widget, 'answer_status'):
                    widget.answer_status.md_bg_color = [0.8, 0.8, 0.8, 1]  # Gray
                        
            except Exception as e:
                print(f"Error clearing widget for question type {q_type}: {e}")

    def _show_empty_state(self, title="No form loaded", message="Select a project above to load its data collection form"):
        """Enhanced empty state display for tablets"""
        try:
            # Clear existing widgets
            self.ids.form_canvas.clear_widgets()
            
            # Hide form controls
            self.hide_form_controls()
            
            # Create tablet-optimized empty state
            from widgets.responsive_layout import ResponsiveHelper
            category = ResponsiveHelper.get_screen_size_category()
            
            if category in ["large_tablet", "tablet"]:
                card_height = dp(350)
                icon_size = "72sp"
                title_size = "24sp"
                message_size = "18sp"
                padding = dp(40)
            elif category == "small_tablet":
                card_height = dp(300)
                icon_size = "64sp"
                title_size = "20sp" 
                message_size = "16sp"
                padding = dp(32)
            else:  # phone
                card_height = dp(250)
                icon_size = "56sp"
                title_size = "18sp"
                message_size = "14sp"
                padding = dp(24)
            
            empty_state = MDCard(
                orientation='vertical',
                spacing=dp(20),
                size_hint_y=None,
                height=card_height,
                elevation=1,
                padding=padding,
                radius=[dp(12)]
            )
            empty_state.id = 'empty_state'
            
            # Spacer
            empty_state.add_widget(Widget(size_hint_y=None, height=dp(20)))
            
            # Icon
            icon_label = MDLabel(
                text="📋",
                halign="center",
                font_size=icon_size,
                size_hint_y=None,
                height=dp(80),
                theme_text_color="Hint"
            )
            empty_state.add_widget(icon_label)
            
            # Title
            title_label = MDLabel(
                text=title,
                font_style="H5",
                theme_text_color="Hint",
                halign="center",
                font_size=title_size,
                bold=True
            )
            empty_state.add_widget(title_label)
            
            # Message
            message_label = MDLabel(
                text=message,
                font_style="Body1",
                theme_text_color="Hint",
                halign="center",
                font_size=message_size,
                text_size=(None, None)
            )
            empty_state.add_widget(message_label)
            
            # Spacer
            empty_state.add_widget(Widget(size_hint_y=None, height=dp(20)))
            
            self.ids.form_canvas.add_widget(empty_state)
            
        except Exception as e:
            print(f"Error showing enhanced empty state: {e}")
            # Fallback to basic empty state
            self.ids.form_canvas.clear_widgets()

    def _reset_submit_button(self):
        """Reset submit button to normal state"""
        self.ids.submit_button.disabled = False
        self._update_submit_button()
