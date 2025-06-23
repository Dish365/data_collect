from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivy.app import App

from widgets.project_item import ProjectItem
from widgets.project_dialog import ProjectDialog
from services.auth_service import AuthService
from services.project_service import ProjectService
from services.sync_service import SyncService

import threading
import uuid
import json
from datetime import datetime

Builder.load_file("kv/projects.kv")


class ProjectsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        self.auth_service = app.auth_service
        self.project_service = ProjectService(app.auth_service, app.db_service, app.sync_service)
        self.sync_service = app.sync_service
        self.projects_data = []
        self.is_loading = False
        self.dialog = None
        self.dialog_content = None
        self.current_project_id = None
        self.current_offset = 0
        self.page_limit = 10

    def on_enter(self):
        self.ids.top_bar.set_title("Projects")
        self.check_and_sync_projects()

    def check_and_sync_projects(self):
        """Check for network and sync projects if online."""
        self.show_loader(True)
        def _check_network_and_sync():
            is_online = self.auth_service._check_network_connectivity()
            if is_online:
                Clock.schedule_once(lambda dt: toast("Network online. Syncing..."))
                # Trigger a one-off sync
                self.sync_service.sync() 
                # After sync, reload projects to get updated statuses
                Clock.schedule_once(lambda dt: self.load_projects(clear_existing=True), 2) # Delay to allow sync to complete
            else:
                Clock.schedule_once(lambda dt: toast("Network offline. Loading local data."))
                self.load_projects(clear_existing=True)

        threading.Thread(target=_check_network_and_sync).start()

    def show_loader(self, show=True):
        if self.ids.spinner:
            self.ids.spinner.active = show
        if self.ids.content_layout:
            self.ids.content_layout.opacity = 0.3 if show else 1
            self.ids.content_layout.disabled = show

    def open_project_dialog(self, is_edit=False, existing_data=None):
        try:
            # Always create a new content widget to avoid state issues
            content = ProjectDialog()

            if is_edit and existing_data:
                content.set_data(**existing_data)
                self.current_project_id = existing_data.get('id')
            else:
                # This is a new project
                self.current_project_id = None
            
            # Create a new dialog each time to ensure it's fresh
            self.dialog = MDDialog(
                title="Edit Project" if is_edit else "New Project",
                type="custom",
                content_cls=content,
                buttons=[
                    MDRaisedButton(
                        text="SAVE",
                        on_release=self.save_project,
                        md_bg_color=App.get_running_app().theme_cls.primary_color,
                    ),
                    MDRaisedButton(
                        text="CANCEL",
                        on_release=lambda x: self.dialog.dismiss(),
                    ),
                ],
            )
            self.dialog.open()

        except Exception as e:
            print(f"Error opening project dialog: {str(e)}")
            err_msg = str(e)
            Clock.schedule_once(lambda dt: toast(f"Error opening dialog: {err_msg}"))

    def save_project(self, instance):
        self.show_loader(True)
        try:
            # Get data from the dialog's content
            project_data = self.dialog.content_cls.get_data()
            if not project_data['name'].strip():
                Clock.schedule_once(lambda dt: toast("Project name is required"))
                self.show_loader(False)
                return

            if self.current_project_id:
                self._execute_api_call(self.project_service.update_project, self.current_project_id, project_data)
            else:
                self._execute_api_call(self.project_service.create_project, project_data)

            if self.dialog:
                self.dialog.dismiss()

        except Exception as e:
            print(f"Error in save_project: {str(e)}")
            err_msg = str(e)
            Clock.schedule_once(lambda dt: toast(f"Error saving project: {err_msg}"))
            self.show_loader(False)

    def _execute_api_call(self, api_func, *args):
        def run_in_thread():
            result = {}
            try:
                result = api_func(*args)
            except Exception as e:
                print(f"Error during API call: {str(e)}")
                result = {'message': f"An error occurred: {str(e)}"}
            finally:
                Clock.schedule_once(lambda dt: self._process_api_result(result))

        threading.Thread(target=run_in_thread).start()

    def _process_api_result(self, result):
        self.show_loader(False)
        if result.get('message'):
            Clock.schedule_once(lambda dt: toast(result['message']))
        if result.get('reload', False):
            self.load_projects(clear_existing=True)

    def search_projects(self, query):
        self.load_projects(search_query=query, clear_existing=True)

    def load_projects(self, search_query=None, clear_existing=False):
        if self.is_loading:
            return
        self.is_loading = True
        self.show_loader(True)

        if clear_existing:
            self.current_offset = 0
            self.projects_data = []
            self.ids.projects_grid.clear_widgets()
            if hasattr(self.ids, 'load_more_button'):
                self.ids.content_layout.remove_widget(self.ids.load_more_button)

        def _load_in_thread():
            try:
                projects, error = self.project_service.load_projects(
                    search_query=search_query,
                    limit=self.page_limit,
                    offset=self.current_offset
                )
                if error:
                    raise Exception(error)
                
                self.projects_data.extend(projects)
                self.current_offset += len(projects)
                
                Clock.schedule_once(lambda dt: self._update_ui_with_projects(projects, len(projects) < self.page_limit))
            except Exception as e:
                print(f"Error in load_projects: {str(e)}")
                err_msg = str(e)
                Clock.schedule_once(lambda dt: toast(f"Error loading projects: {err_msg}"))
            finally:
                self.is_loading = False
                Clock.schedule_once(lambda dt: self.show_loader(False))

        threading.Thread(target=_load_in_thread).start()

    def _update_ui_with_projects(self, new_projects, is_last_page):
        if hasattr(self.ids, 'load_more_button') and self.ids.load_more_button.parent:
             self.ids.content_layout.remove_widget(self.ids.load_more_button)

        if not self.projects_data and not new_projects:
            self.ids.projects_grid.clear_widgets()
            empty_label = Label(
                text="No projects found.",
                size_hint_y=None,
                height=dp(100),
                halign='center'
            )
            self.ids.projects_grid.add_widget(empty_label)
            return

        for project in new_projects:
            project_item = ProjectItem(
                project_id=str(project.get('id', '')),
                name=project.get('name', 'No Name'),
                description=project.get('description', ''),
                created_at=project.get('created_at', ''),
                sync_status=project.get('sync_status', 'unknown')
            )
            project_item.bind(
                on_edit=lambda instance, pid=project.get('id'): self.edit_project(pid),
                on_delete=lambda instance, pid=project.get('id'): self.delete_project(pid),
                on_build_form=lambda instance, pid=project.get('id'): self.go_to_form_builder(pid)
            )
            self.ids.projects_grid.add_widget(project_item)

        if not is_last_page:
            self.ids.load_more_button = MDRaisedButton(
                text="Load More",
                on_release=lambda x: self.load_projects(search_query=self.ids.search_field.text),
                size_hint_y=None,
                height=dp(48),
                pos_hint={'center_x': 0.5},
            )
            self.ids.content_layout.add_widget(self.ids.load_more_button)

    def edit_project(self, project_id):
        project_data = next((p for p in self.projects_data if str(p.get('id')) == str(project_id)), None)
        if project_data:
            self.open_project_dialog(is_edit=True, existing_data=project_data)

    def delete_project(self, project_id):
        def confirm_delete(instance):
            self.show_loader(True)
            self._execute_api_call(self.project_service.delete_project, project_id)
            delete_dialog.dismiss()

        delete_dialog = MDDialog(
            title="Delete Project?",
            text="This action cannot be undone.",
            buttons=[
                MDRaisedButton(
                    text="CANCEL",
                    on_release=lambda x: delete_dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="DELETE",
                    md_bg_color=(1, 0, 0, 1),
                    on_release=confirm_delete,
                ),
            ],
        )
        delete_dialog.open()

    def go_to_form_builder(self, project_id):
        self.manager.current = 'form_builder'
        form_builder_screen = self.manager.get_screen('form_builder')
        form_builder_screen.project_id = project_id

    def create_new_project(self, instance):
        self.open_project_dialog()
