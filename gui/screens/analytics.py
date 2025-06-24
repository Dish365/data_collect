from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivymd.toast import toast
from kivy.app import App
from services.analytics_service import AnalyticsService

Builder.load_file('kv/analytics.kv')

class AnalyticsScreen(Screen):
    analytics_service = ObjectProperty(None)
    current_project = None
    current_questions = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Service will be set in on_enter (after db_service is available)

    def on_enter(self):
        app = App.get_running_app()
        if not self.analytics_service:
            self.analytics_service = AnalyticsService(app.db_service)
        self.load_summary_dashboard()
        self.load_projects()

    def load_summary_dashboard(self):
        stats = self.analytics_service.get_summary_stats()
        self.ids.summary_cards.clear_widgets()
        for label, value in [
            ("Total Responses", stats['total_responses']),
            ("Total Projects", stats['total_projects']),
            ("Total Questions", stats['total_questions'])
        ]:
            from kivymd.uix.boxlayout import MDBoxLayout
            from kivymd.uix.label import MDLabel
            card = MDBoxLayout(orientation='vertical', padding=8, size_hint_x=None, width=180, size_hint_y=None, height=70, spacing=2)
            card.add_widget(MDLabel(text=str(value), font_style='H5', halign='center'))
            card.add_widget(MDLabel(text=label, font_style='Caption', halign='center'))
            self.ids.summary_cards.add_widget(card)

    def load_projects(self):
        app = App.get_running_app()
        conn = app.db_service.get_db_connection()
        if conn is None:
            toast("Database not initialized. Please restart the app.")
            return
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM projects ORDER BY name')
        projects = cursor.fetchall()
        self.ids.project_spinner.values = ['Select Project'] + [p['name'] for p in projects]
        self.ids.project_spinner.text = 'Select Project'

    def on_project_selected(self, spinner, text):
        if text == 'Select Project':
            self.current_project = None
            self.ids.question_spinner.values = ['Select Question']
            self.ids.question_spinner.text = 'Select Question'
            self.ids.chart_container.clear_widgets()
            return
        app = App.get_running_app()
        conn = app.db_service.get_db_connection()
        if conn is None:
            toast("Database not initialized. Please restart the app.")
            return
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM projects WHERE name = ?', (text,))
        project = cursor.fetchone()
        if project:
            self.current_project = project['id']
            self.load_questions()

    def load_questions(self):
        if not self.current_project:
            return
        app = App.get_running_app()
        conn = app.db_service.get_db_connection()
        if conn is None:
            toast("Database not initialized. Please restart the app.")
            return
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, question_text, question_type 
            FROM questions 
            WHERE project_id = ? 
            ORDER BY order_index
        ''', (self.current_project,))
        questions = cursor.fetchall()
        self.ids.question_spinner.values = ['Select Question'] + [
            f"{q['question_text']} ({q['question_type']})" for q in questions
        ]
        self.ids.question_spinner.text = 'Select Question'
        self.current_questions = questions

    def on_question_selected(self, spinner, text):
        if text == 'Select Question':
            self.ids.chart_container.clear_widgets()
            return
        question_index = self.ids.question_spinner.values.index(text) - 1
        question = self.current_questions[question_index]
        breakdown = self.analytics_service.get_response_breakdown(question['id'])
        self.ids.chart_container.clear_widgets()
        from kivymd.uix.label import MDLabel
        self.ids.chart_container.add_widget(MDLabel(text=str(breakdown), halign='center'))

    # --- Descriptive Analytics ---
    def load_descriptive_analytics(self):
        pass

    # --- Inferential Analytics ---
    def load_inferential_analytics(self):
        pass

    # --- Qualitative Analytics ---
    def load_qualitative_analytics(self):
        pass

    # --- Export/Reporting ---
    def export_report(self, export_type):
        toast(f"Exporting report as {export_type.upper()} (not yet implemented)")

    # --- Actionable Insights ---
    def load_actionable_insights(self):
        pass

    # --- Collaboration ---
    def load_collaboration(self):
        pass 