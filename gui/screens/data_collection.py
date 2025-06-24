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

import json

Builder.load_file("kv/collect_data.kv")

class DataCollectionScreen(Screen):
    project_id = StringProperty(None, allownone=True)
    project_list = ListProperty([])
    project_map = {}
    project_menu = None
    questions_data = []
    response_widgets = []

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
                Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'projects'), 1)
                return
            self.project_list = [p['name'] for p in projects]
            self.project_map = {p['name']: p['id'] for p in projects}
            self.project_id = None
            self.ids.project_spinner.text = 'Select Project'
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
        self.load_form()

    def load_form(self):
        self.ids.form_canvas.clear_widgets()
        self.response_widgets = []
        app = App.get_running_app()
        questions, error = app.form_service.load_questions(self.project_id)
        if error:
            toast(f"Error loading form: {error}")
            return
        self.questions_data = questions
        for q in questions:
            widget = self.create_question_widget(q)
            self.ids.form_canvas.add_widget(widget)
            self.response_widgets.append((q, widget))

    def create_question_widget(self, q):
        q_type = q.get('question_type', 'text')
        q_text = q.get('question_text', '')
        options = q.get('options') or []
        if isinstance(options, str):
            try:
                options = json.loads(options)
            except Exception:
                options = []
        allow_multiple = bool(q.get('allow_multiple', False))
        box = MDBoxLayout(orientation='vertical', spacing=dp(6), padding=[0, dp(4)], adaptive_height=True)
        box.add_widget(MDLabel(text=q_text, font_style="Subtitle1", size_hint_y=None, height=dp(28)))

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
                input_filter='int' if q_type == 'numeric' else None
            )
            box.add_widget(field)
            box.response_field = field

        elif q_type == 'choice':
            checks = []
            for opt in options:
                row = MDBoxLayout(
                    orientation='horizontal',
                    spacing=dp(10),
                    size_hint_y=None,
                    height=dp(40),
                    padding=[dp(8), dp(4), 0, dp(4)],
                )

                cb = MDCheckbox(
                    group=q_text if not allow_multiple else None,
                    size_hint=(None, None),
                    size=(dp(36), dp(36))
                )

                label = MDLabel(
                    text=opt,
                    halign='left',
                    valign='middle',
                    size_hint_x=1
                )
                label.bind(size=label.setter('text_size'))

                row.add_widget(cb)
                row.add_widget(label)
                box.add_widget(row)
                checks.append((cb, opt))
            box.response_field = checks

        elif q_type == 'scale':
            slider = MDSlider(min=1, max=5, value=3, step=1)
            box.add_widget(slider)
            box.response_field = slider

        elif q_type == 'photo':
            field = MDLabel(text="[Photo upload not implemented]", font_style="Caption")
            box.add_widget(field)
            box.response_field = None

        else:
            field = MDTextField(hint_text="Your answer", mode="rectangle")
            box.add_widget(field)
            box.response_field = field

        return box

    def submit_response(self):
        responses = []
        app = App.get_running_app()
        user_id = app.auth_service.get_user_data().get('id', 'anonymous')
        for q, widget in self.response_widgets:
            q_type = q.get('question_type', 'text')
            answer = None
            if q_type in ('text', 'long_text', 'numeric', 'date', 'location'):
                answer = widget.response_field.text if widget.response_field else None
            elif q_type == 'choice':
                if bool(q.get('allow_multiple', False)):
                    answer = [opt for cb, opt in widget.response_field if cb.active]
                else:
                    for cb, opt in widget.response_field:
                        if cb.active:
                            answer = opt
                            break
            elif q_type == 'scale':
                answer = int(widget.response_field.value) if widget.response_field else None
            elif q_type == 'photo':
                answer = None

            responses.append({
                'project': self.project_id,
                'question': q.get('id'),
                'respondent_id': user_id,
                'response_value': answer,
                'metadata': {},
                'sync_status': 'pending',
                'user_id': user_id
            })

        for resp in responses:
            if app.auth_service.is_authenticated():
                result = app.auth_service.make_authenticated_request(
                    'api/v1/responses/', method='POST', data=resp
                )
                if 'error' in result:
                    app.sync_service.queue_sync('responses', resp['question'], 'create', resp)
            else:
                app.sync_service.queue_sync('responses', resp['question'], 'create', resp)

        toast("Responses saved! (Will sync when online)")
        self.ids.form_canvas.clear_widgets()
        self.response_widgets = []
