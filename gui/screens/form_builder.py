from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from widgets.form_fields import ShortTextField, MultipleChoiceField ,LongTextField,LocationPickerField , PhotoUploadField, RatingScaleField
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
    
    def on_enter(self):
        self.load_projects()

    def load_projects(self):
        """Loads all projects from the local DB and populates the spinner."""
        app = App.get_running_app()
        conn = app.db_service.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM projects ORDER BY name")
            projects = cursor.fetchall()
            if not projects:
                toast("No projects found. Redirecting to Projects page.")
                Clock.schedule_once(lambda dt: self.manager.change_screen('projects', 'right'), 1)
                return
            self.project_list = [p['name'] for p in projects]
            self.project_map = {p['name']: p['id'] for p in projects}
            self.ids.project_spinner.values = self.project_list
            self.ids.project_spinner.text = 'Select Project'
            self.project_id = None
            self.ids.form_canvas.clear_widgets()
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
            self.ids.project_spinner.text = 'Select Project'
            self.ids.form_canvas.clear_widgets()
            return
        self.project_id = self.project_map[text]
        self.ids.project_spinner.text = text
        self.ids.top_bar.set_title(f"Form for {text}")
        self.load_form()

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
                Clock.schedule_once(lambda dt: toast(f"Error: {e}"))
            finally:
                Clock.schedule_once(lambda dt: self.show_loader(False))

        threading.Thread(target=_load_in_thread).start()

    def _update_ui_with_questions(self):
        """Populates the UI with question widgets."""
        for q_data in self.questions_data:
            # Map backend/local fields to QuestionBlock fields
            answer_type = self._map_type_to_block(q_data.get('question_type', 'text'))
            block = QuestionBlock()
            block.question_input.text = q_data.get('question_text', '')
            block.set_answer_type(answer_type)
            if answer_type == "Multiple Choice":
                # Remove default options and add from data
                block.answer_area.clear_widgets()
                block.set_answer_type("Multiple Choice")
                block.options_box.clear_widgets()
                block.options_widgets = []
                options = q_data.get('options') or []
                if isinstance(options, str):
                    try:
                        options = json.loads(options)
                    except Exception:
                        options = []
                for opt in options:
                    block.add_option()
                    block.options_widgets[-1].text = opt
                val = q_data.get('allow_multiple', False)
                if isinstance(val, str):
                    val = val.lower() in ('true', '1')
                block.toggle_switch.active = bool(val)
            block.bind(minimum_height=block.setter("height"))
            self.ids.form_canvas.add_widget(block)

    def add_question(self, question_type):
        """Adds a new question widget to the form canvas."""
        if not self.project_id:
            toast("Select a project first.")
            return
        block = QuestionBlock()
        block.set_answer_type(self._map_type_to_block(question_type))
        block.bind(minimum_height=block.setter("height"))
        self.ids.form_canvas.add_widget(block)
        toast(f"Added {question_type} question")

    def remove_question_widget(self, widget_instance):
        """Removes a question widget from the UI."""
        self.ids.form_canvas.remove_widget(widget_instance)

    def save_form(self):
        """Collects data from all question widgets and saves the form."""
        if not self.project_id:
            toast("Select a project first.")
            return
        self.show_loader(True)
        
        questions_to_save = []
        for widget in self.ids.form_canvas.children:
            if isinstance(widget, QuestionBlock):
                q = widget.to_dict()
                # Map QuestionBlock fields to backend/local fields
                questions_to_save.append({
                    'question_text': q.get('question', ''),
                    'question_type': self._map_type_to_backend(q.get('type', 'Short Answer')),
                    'options': q.get('options', []),
                    'allow_multiple': bool(q.get('allow_multiple', False))
                })
        
        # The widgets are added in reverse order, so we reverse the list back
        questions_to_save.reverse()

        def _save_in_thread():
            try:
                result = self.form_service.save_questions(self.project_id, questions_to_save)
                Clock.schedule_once(lambda dt: toast(result.get('message', 'Form saved.')))
            except Exception as e:
                Clock.schedule_once(lambda dt: toast(f"Error saving: {e}"))
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
            if isinstance(widget, QuestionBlock):
                q = widget.to_dict()
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
                if q_type == "Multiple Choice" and options:
                    for opt in options:
                        preview_layout.add_widget(MDLabel(text=f"- {opt}", font_style="Body2"))
                    if allow_multiple:
                        preview_layout.add_widget(MDLabel(text="(Multiple answers allowed)", font_style="Caption"))
                elif q_type == "Long Answer":
                    preview_layout.add_widget(MDLabel(text="[Long answer field]", font_style="Body2"))
                elif q_type == "Short Answer":
                    preview_layout.add_widget(MDLabel(text="[Short answer field]", font_style="Body2"))
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

    def add_question_block(self):
        block = QuestionBlock()
        self.ids.question_blocks_container.add_widget(block)

    def load_questions(self):
        if not self.current_project:
            return
        
        # Clear existing questions
        self.questions_layout.clear_widgets()
        self.current_questions = []
        
        # Get app instance
        app = self.manager.get_screen('form_builder').parent
        
        # Load questions from database
        cursor = app.db_service.conn.cursor()
        cursor.execute('''
            SELECT * FROM questions 
            WHERE project_id = ? 
            ORDER BY order_index
        ''', (self.current_project,))
        questions = cursor.fetchall()
        
        # Add question items
        for question in questions:
            self.add_question_item(question)
    
    def add_question_item(self, question):
        # Create question item
        item = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            padding=dp(10)
        )
        
        # Question info
        info = BoxLayout(orientation='vertical')
        info.add_widget(Label(
            text=question['question_text'],
            size_hint_y=None,
            height=dp(30)
        ))
        info.add_widget(Label(
            text=f"Type: {question['question_type']}",
            size_hint_y=None,
            height=dp(20)
        ))
        item.add_widget(info)
        
        # Delete button
        delete_btn = Button(
            text='Delete',
            size_hint_x=None,
            width=dp(100),
            on_press=lambda x: self.delete_question(question['id'])
        )
        item.add_widget(delete_btn)
        
        self.questions_layout.add_widget(item)
        self.current_questions.append(item)
    
    def delete_question(self, question_id):
        # Get app instance
        app = self.manager.get_screen('form_builder').parent
        
        # Delete from database
        cursor = app.db_service.conn.cursor()
        cursor.execute('DELETE FROM questions WHERE id = ?', (question_id,))
        app.db_service.conn.commit()
        
        # Queue for sync
        app.sync_service.queue_sync(
            'questions',
            question_id,
            'delete',
            None
        )
        
        # Reload questions
        self.load_questions() 

    def _map_type_to_block(self, question_type):
        # Map backend/local type to QuestionBlock type
        if question_type == 'text':
            return "Short Answer"
        elif question_type == 'long_text':
            return "Long Answer"
        elif question_type == 'choice':
            return "Multiple Choice"
        elif question_type == 'numeric':
            return "Short Answer"  # Could be improved
        else:
            return "Short Answer"

    def _map_type_to_backend(self, block_type):
        # Map QuestionBlock type to backend/local type
        if block_type == "Short Answer":
            return 'text'
        elif block_type == "Long Answer":
            return 'long_text'
        elif block_type == "Multiple Choice":
            return 'choice'
        else:
            return 'text' 