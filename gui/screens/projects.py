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
        self.filtered_projects_data = []  # For filtered results
        self.is_loading = False
        self.dialog = None
        self.dialog_content = None
        self.current_project_id = None
        self.current_offset = 0
        self.page_limit = 10
        
        # New attributes for tablet optimization
        self.current_filter = "all"
        self.current_sort = "name"
        self.is_grid_view = True
        self.sort_menu = None

    def on_enter(self):
        self.ids.top_bar.set_title("Projects")
        
        # Initialize responsive layout
        self.update_responsive_layout()
        
        self.check_and_sync_projects()

    def on_window_resize(self, width, height):
        """Handle window resize for responsive layout adjustments"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            
            # Determine screen size category and orientation
            category = ResponsiveHelper.get_screen_size_category()
            is_landscape = ResponsiveHelper.is_landscape()
            
            print(f"Projects: Window resized to {width}x{height} - {category} {'landscape' if is_landscape else 'portrait'}")
            
            # Update responsive properties
            self.update_responsive_layout()
            
        except Exception as e:
            print(f"Error handling window resize in projects: {e}")
    
    def update_responsive_layout(self):
        """Update layout based on current screen size"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            
            category = ResponsiveHelper.get_screen_size_category()
            is_landscape = ResponsiveHelper.is_landscape()
            
            print(f"Projects: Updating responsive layout for {category} {'landscape' if is_landscape else 'portrait'}")
            
            # Update grid columns based on screen size
            self.update_grid_columns(category, is_landscape)
            
            # Update TopBar height for tablets
            if hasattr(self.ids, 'top_bar'):
                if category in ["tablet", "large_tablet"]:
                    self.ids.top_bar.height = dp(64)
                else:
                    self.ids.top_bar.height = dp(56)
            
        except Exception as e:
            print(f"Error updating responsive layout in projects: {e}")
    
    def update_grid_columns(self, category, is_landscape):
        """Update grid column count based on screen size and orientation"""
        if not hasattr(self.ids, 'projects_grid'):
            return
            
        grid = self.ids.projects_grid
        
        # Determine optimal column count
        if category == "large_tablet":
            cols = 4 if is_landscape else 3  # 4 columns landscape, 3 portrait
        elif category == "tablet":
            cols = 3 if is_landscape else 2  # 3 columns landscape, 2 portrait
        elif category == "small_tablet":
            cols = 2 if is_landscape else 1  # 2 columns landscape, 1 portrait
        else:  # phone
            cols = 1  # Always 1 column on phones
        
        if grid.cols != cols:
            grid.cols = cols
            print(f"Projects: Updated grid to {cols} columns for {category} {'landscape' if is_landscape else 'portrait'}")
    
    def filter_projects(self, filter_type):
        """Filter projects by type"""
        self.current_filter = filter_type
        print(f"Projects: Filtering by {filter_type}")
        
        # Update button states
        self.update_filter_button_states(filter_type)
        
        # Apply filter to current projects data
        self.apply_current_filter()
        
        # Refresh UI with filtered data
        self.refresh_projects_ui()
    
    def update_filter_button_states(self, active_filter):
        """Update the visual state of filter buttons"""
        filter_buttons = {
            "all": "filter_all_btn",
            "recent": "filter_recent_btn", 
            "synced": "filter_synced_btn",
            "pending": "filter_pending_btn"
        }
        
        for filter_name, button_id in filter_buttons.items():
            if hasattr(self.ids, button_id):
                button = getattr(self.ids, button_id)
                if filter_name == active_filter:
                    # Active button styling
                    button.md_bg_color = App.get_running_app().theme_cls.primary_color
                    button.theme_text_color = "Primary"
                else:
                    # Inactive button styling
                    button.md_bg_color = [0.9, 0.9, 0.9, 1]  # Light gray
                    button.theme_text_color = "Secondary"
    
    def apply_current_filter(self):
        """Apply the current filter to projects data"""
        if self.current_filter == "all":
            self.filtered_projects_data = self.projects_data.copy()
        elif self.current_filter == "recent":
            # Filter to projects created in last 30 days
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=30)
            self.filtered_projects_data = [
                p for p in self.projects_data 
                if self.parse_project_date(p.get('created_at', '')) > cutoff_date
            ]
        elif self.current_filter == "synced":
            self.filtered_projects_data = [
                p for p in self.projects_data 
                if p.get('sync_status', '').lower() == 'synced'
            ]
        elif self.current_filter == "pending":
            self.filtered_projects_data = [
                p for p in self.projects_data 
                if p.get('sync_status', '').lower() in ['pending', 'failed']
            ]
        
        # Apply current sort
        self.apply_current_sort()
    
    def parse_project_date(self, date_str):
        """Parse project date string to datetime object"""
        try:
            if '.' in date_str:
                return datetime.fromisoformat(date_str.split('.')[0])
            else:
                return datetime.fromisoformat(date_str.replace('Z', ''))
        except (ValueError, TypeError):
            return datetime.min  # Return minimum date for invalid dates
    
    def apply_current_sort(self):
        """Apply current sort to filtered projects data"""
        if self.current_sort == "name":
            self.filtered_projects_data.sort(key=lambda p: p.get('name', '').lower())
        elif self.current_sort == "date_new":
            self.filtered_projects_data.sort(
                key=lambda p: self.parse_project_date(p.get('created_at', '')), 
                reverse=True
            )
        elif self.current_sort == "date_old":
            self.filtered_projects_data.sort(
                key=lambda p: self.parse_project_date(p.get('created_at', ''))
            )
        elif self.current_sort == "status":
            self.filtered_projects_data.sort(key=lambda p: p.get('sync_status', '').lower())
    
    def show_sort_menu(self):
        """Show sort options menu"""
        try:
            from kivymd.uix.menu import MDDropdownMenu
            
            menu_items = [
                {"text": "Name (A-Z)", "viewclass": "OneLineListItem", "on_release": lambda: self.sort_projects("name")},
                {"text": "Newest First", "viewclass": "OneLineListItem", "on_release": lambda: self.sort_projects("date_new")},
                {"text": "Oldest First", "viewclass": "OneLineListItem", "on_release": lambda: self.sort_projects("date_old")},
                {"text": "Sync Status", "viewclass": "OneLineListItem", "on_release": lambda: self.sort_projects("status")},
            ]
            
            self.sort_menu = MDDropdownMenu(
                caller=self.ids.view_toggle_btn,  # Use any button as caller
                items=menu_items,
                width_mult=4
            )
            self.sort_menu.open()
            
        except Exception as e:
            print(f"Error showing sort menu: {e}")
            toast("Sort options coming soon")
    
    def sort_projects(self, sort_type):
        """Sort projects by specified type"""
        if self.sort_menu:
            self.sort_menu.dismiss()
            
        self.current_sort = sort_type
        print(f"Projects: Sorting by {sort_type}")
        
        # Apply sort to current filtered data
        self.apply_current_sort()
        
        # Refresh UI with sorted data
        self.refresh_projects_ui()
        
        toast(f"Sorted by {sort_type.replace('_', ' ').title()}")
    
    def toggle_view_mode(self):
        """Toggle between grid and list view"""
        self.is_grid_view = not self.is_grid_view
        
        # Update button icon
        if hasattr(self.ids, 'view_toggle_btn'):
            icon = "view-grid" if self.is_grid_view else "view-list"
            self.ids.view_toggle_btn.icon = icon
        
        # For now, we'll just show a toast - grid/list styling can be enhanced later
        view_mode = "Grid" if self.is_grid_view else "List"
        toast(f"Switched to {view_mode} view")
        
        print(f"Projects: Toggled to {'grid' if self.is_grid_view else 'list'} view")
    
    def refresh_projects_ui(self):
        """Refresh the projects UI with current filtered/sorted data"""
        # Clear current grid
        self.ids.projects_grid.clear_widgets()
        
        # Remove any existing load more button
        if hasattr(self.ids, 'load_more_button') and self.ids.load_more_button.parent:
            self.ids.content_layout.remove_widget(self.ids.load_more_button)
        
        # Display filtered projects
        if not self.filtered_projects_data:
            self.show_empty_state()
        else:
            for project in self.filtered_projects_data:
                project_item = self.create_tablet_optimized_project_item(project)
                self.ids.projects_grid.add_widget(project_item)
    
    def create_tablet_optimized_project_item(self, project):
        """Create a tablet-optimized project item"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            from widgets.project_item import ProjectItem
            
            category = ResponsiveHelper.get_screen_size_category()
            
            # Create project item with responsive sizing
            project_item = ProjectItem(
                project_id=str(project.get('id', '')),
                name=project.get('name', 'No Name'),
                description=project.get('description') or 'No description',
                created_at=project.get('created_at', ''),
                sync_status=project.get('sync_status', 'unknown')
            )
            
            # Apply tablet-specific styling if needed
            if category in ["tablet", "large_tablet"]:
                # Increase padding and spacing for tablets
                project_item.padding = (dp(12), dp(12), dp(8), dp(12))
                project_item.spacing = dp(16)
                project_item.height = dp(84)  # Slightly taller for tablets
            
            # Bind events
            project_item.bind(
                on_edit=lambda instance, pid=project.get('id'): self.edit_project(pid),
                on_delete=lambda instance, pid=project.get('id'): self.delete_project(pid),
                on_build_form=lambda instance, pid=project.get('id'): self.go_to_form_builder(pid)
            )
            
            return project_item
            
        except Exception as e:
            print(f"Error creating tablet project item: {e}")
            # Fallback to original creation
            return self.create_original_project_item(project)
    
    def create_original_project_item(self, project):
        """Create original project item as fallback"""
        from widgets.project_item import ProjectItem
        
        project_item = ProjectItem(
            project_id=str(project.get('id', '')),
            name=project.get('name', 'No Name'),
            description=project.get('description') or 'No description',
            created_at=project.get('created_at', ''),
            sync_status=project.get('sync_status', 'unknown')
        )
        
        project_item.bind(
            on_edit=lambda instance, pid=project.get('id'): self.edit_project(pid),
            on_delete=lambda instance, pid=project.get('id'): self.delete_project(pid),
            on_build_form=lambda instance, pid=project.get('id'): self.go_to_form_builder(pid)
        )
        
        return project_item
    
    def show_empty_state(self):
        """Show appropriate empty state message"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            
            category = ResponsiveHelper.get_screen_size_category()
            
            # Create responsive empty state message
            if category in ["tablet", "large_tablet"]:
                height = dp(120)
                font_size = "18sp"
            else:
                height = dp(100)
                font_size = "16sp"
            
            if self.current_filter == "all":
                message = "No projects found. Create your first project to get started!"
            else:
                filter_names = {
                    "recent": "recent projects",
                    "synced": "synced projects", 
                    "pending": "pending projects"
                }
                filter_name = filter_names.get(self.current_filter, "projects")
                message = f"No {filter_name} found. Try a different filter."
            
            empty_label = MDLabel(
                text=message,
                size_hint_y=None,
                height=height,
                halign='center',
                font_size=font_size,
                theme_text_color="Secondary"
            )
            self.ids.projects_grid.add_widget(empty_label)
            
        except Exception as e:
            print(f"Error showing empty state: {e}")
            # Fallback
            empty_label = Label(
                text="No projects found.",
                size_hint_y=None,
                height=dp(100),
                halign='center'
            )
            self.ids.projects_grid.add_widget(empty_label)

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

    def create_tablet_dialog_button(self, text, on_release, is_primary=False, disabled=False, **kwargs):
        """Create a tablet-optimized dialog button"""
        try:
            from widgets.responsive_layout import ResponsiveHelper
            
            category = ResponsiveHelper.get_screen_size_category()
            
            # Responsive button sizing
            if category == "large_tablet":
                height = dp(56)
                width = dp(120)
                font_size = "16sp"
            elif category == "tablet":
                height = dp(52)
                width = dp(110)
                font_size = "15sp"
            elif category == "small_tablet":
                height = dp(48)
                width = dp(100)
                font_size = "14sp"
            else:  # phone
                height = dp(44)
                width = dp(90)
                font_size = "13sp"
            
            # Create button with responsive styling
            button = MDRaisedButton(
                text=text,
                on_release=on_release,
                size_hint_y=None,
                height=height,
                size_hint_x=None,
                width=width,
                font_size=font_size,
                disabled=disabled,
                **kwargs
            )
            
            return button
            
        except Exception as e:
            print(f"Error creating tablet dialog button: {e}")
            # Fallback to standard button
            return MDRaisedButton(
                text=text,
                on_release=on_release,
                disabled=disabled,
                **kwargs
            )

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
            
            # Create tablet-optimized dialog buttons
            save_button = self.create_tablet_dialog_button(
                text="SAVE",
                on_release=self.save_project,
                md_bg_color=App.get_running_app().theme_cls.primary_color,
                disabled=True,
                is_primary=True
            )
            cancel_button = self.create_tablet_dialog_button(
                text="CANCEL",
                on_release=lambda x: self.dialog.dismiss(),
                is_primary=False
            )
            
            # Enhanced dialog with tablet sizing
            try:
                from widgets.responsive_layout import ResponsiveHelper
                category = ResponsiveHelper.get_screen_size_category()
                
                # Set dialog size based on device category
                if category == "large_tablet":
                    dialog_width = 0.5  # 50% of screen width
                elif category == "tablet":
                    dialog_width = 0.6  # 60% of screen width
                elif category == "small_tablet":
                    dialog_width = 0.7  # 70% of screen width
                else:  # phone
                    dialog_width = 0.85  # 85% of screen width
                    
            except Exception as e:
                print(f"Error determining dialog width: {e}")
                dialog_width = 0.8  # Default width
            
            self.dialog = MDDialog(
                title="Edit Project" if is_edit else "New Project",
                type="custom",
                content_cls=content,
                buttons=[save_button, cancel_button],
                size_hint_x=dialog_width,
                auto_dismiss=False  # Prevent accidental dismissal
            )
            
            # Enhanced validation with real-time feedback
            def on_name_change(instance, value):
                is_valid = content.validate_name()
                save_button.disabled = not is_valid
                
                # Visual feedback for tablets
                try:
                    if category in ["tablet", "large_tablet"]:
                        # Add subtle visual feedback for tablet users
                        if is_valid:
                            save_button.md_bg_color = App.get_running_app().theme_cls.primary_color
                        else:
                            save_button.md_bg_color = [0.7, 0.7, 0.7, 1]  # Grayed out
                except Exception as e:
                    print(f"Error applying visual feedback: {e}")
            
            def on_desc_change(instance, value):
                content.validate_description()
            
            # Bind validation events
            content.ids.name_field.bind(text=on_name_change)
            content.ids.desc_field.bind(text=on_desc_change)
            
            # Set initial state
            initial_valid = bool(content.ids.name_field.text.strip())
            save_button.disabled = not initial_valid
            
            self.dialog.open()

        except Exception as e:
            print(f"Error opening project dialog: {str(e)}")
            err_msg = str(e)
            Clock.schedule_once(lambda dt: toast(f"Error opening dialog: {err_msg}"))

    def save_project(self, instance):
        """Save project with enhanced validation and tablet UX"""
        self.show_loader(True)
        try:
            # Get data from the dialog's content with validation
            content = self.dialog.content_cls
            project_data = content.get_data()
            
            # Enhanced validation check
            if not content.is_valid():
                Clock.schedule_once(lambda dt: toast("Please check your input and try again"))
                self.show_loader(False)
                return
            
            if not project_data.get('is_valid', False):
                Clock.schedule_once(lambda dt: toast("Project name is required"))
                self.show_loader(False)
                return

            # Clean data for API call
            api_data = {
                'name': project_data['name'],
                'description': project_data['description']
            }

            if self.current_project_id:
                self._execute_api_call(self.project_service.update_project, self.current_project_id, api_data)
                Clock.schedule_once(lambda dt: toast("Project updated successfully"))
            else:
                self._execute_api_call(self.project_service.create_project, api_data)
                Clock.schedule_once(lambda dt: toast("Project created successfully"))

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

        # Apply current filter and sort to the newly loaded projects
        self.apply_current_filter()
        
        # Use refresh_projects_ui for consistent display
        self.refresh_projects_ui()

        # Add load more button if needed (using tablet-optimized styling)
        if not is_last_page:
            try:
                from widgets.responsive_layout import ResponsiveHelper
                category = ResponsiveHelper.get_screen_size_category()
                
                # Tablet-optimized load more button
                button_height = dp(52) if category in ["tablet", "large_tablet"] else dp(48)
                button_width = dp(160) if category in ["tablet", "large_tablet"] else dp(140)
                font_size = "16sp" if category in ["tablet", "large_tablet"] else "14sp"
                
                self.ids.load_more_button = MDRaisedButton(
                    text="Load More Projects",
                    on_release=lambda x: self.load_projects(search_query=self.ids.search_field.text if hasattr(self.ids, 'search_field') else ""),
                    size_hint_y=None,
                    height=button_height,
                    size_hint_x=None,
                    width=button_width,
                    font_size=font_size,
                    pos_hint={'center_x': 0.5},
                    md_bg_color=App.get_running_app().theme_cls.primary_color
                )
                self.ids.content_layout.add_widget(self.ids.load_more_button)
                
            except Exception as e:
                print(f"Error creating tablet-optimized load more button: {e}")
                # Fallback to original button
                self.ids.load_more_button = MDRaisedButton(
                    text="Load More",
                    on_release=lambda x: self.load_projects(search_query=self.ids.search_field.text if hasattr(self.ids, 'search_field') else ""),
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
