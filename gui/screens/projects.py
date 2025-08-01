from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.app import App
import threading
import uuid
import json
from datetime import datetime

# KivyMD 2.0 imports
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import (
    MDDialog, 
    MDDialogHeadlineText, 
    MDDialogSupportingText,
    MDDialogButtonContainer
)
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.widget import Widget

# Import with fallbacks for better compatibility
try:
    from utils.cross_platform_toast import toast
except ImportError:
    def toast(message):
        print(f"Toast: {message}")

try:
    from widgets.project_item import ProjectItem
except ImportError:
    print("Warning: ProjectItem widget not found")
    ProjectItem = None

try:
    from widgets.project_dialog import ProjectDialog
except ImportError:
    print("Warning: ProjectDialog widget not found")
    ProjectDialog = None

try:
    from widgets.loading_overlay import LoadingOverlay
except ImportError:
    print("Warning: LoadingOverlay widget not found")
    LoadingOverlay = None

try:
    from services.project_service import ProjectService
except ImportError:
    print("Warning: ProjectService not found")
    ProjectService = None

# KV file loaded by main app after theme initialization

class ProjectsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        
        # Initialize services with fallbacks
        self.auth_service = getattr(app, 'auth_service', None)
        if ProjectService and hasattr(app, 'auth_service') and hasattr(app, 'db_service') and hasattr(app, 'sync_service'):
            self.project_service = ProjectService(app.auth_service, app.db_service, app.sync_service)
        else:
            print("Warning: ProjectService not available")
            self.project_service = None
            
        self.sync_service = getattr(app, 'sync_service', None)
        
        # Data management
        self.projects_data = []
        self.filtered_projects_data = []
        self.is_loading = False
        self.dialog = None
        self.dialog_content = None
        self.current_project_id = None
        self.current_offset = 0
        self.page_limit = 10
        
        # UI state
        self.current_filter = "all"
        self.current_sort = "name"
        self.is_grid_view = True
        self.sort_menu = None
        
        # Initialize loading overlay
        if LoadingOverlay:
            self.loading_overlay = LoadingOverlay()
        else:
            self.loading_overlay = None

    def on_enter(self):
        """Called when the screen is entered"""
        if hasattr(self.ids, 'top_bar') and self.ids.top_bar:
            self.ids.top_bar.set_title("Projects")
            self.ids.top_bar.set_current_screen("projects")
        
        # Update responsive layout
        self.update_responsive_layout()
        
        self.check_and_sync_projects()

    def on_window_resize(self, width, height):
        """Handle window resize for responsive layout adjustments"""
        try:
            self.update_responsive_layout()
        except Exception as e:
            pass
    
    def update_responsive_layout(self):
        """Update layout based on current screen size using KivyMD 2.0 responsive patterns"""
        try:
            from kivy.core.window import Window
            
            window_width = Window.width
            window_height = Window.height
            
            # Determine screen category based on density-independent pixels
            if window_width < dp(600):
                category = "phone"
                cols = 1
            elif window_width < dp(840):
                category = "small_tablet"
                cols = 2
            elif window_width < dp(1200):
                category = "tablet"
                cols = 3
            else:
                category = "large_tablet"
                cols = 4
            
            is_landscape = window_width > window_height
            

            
            # Update grid columns
            if hasattr(self.ids, 'projects_grid'):
                self.ids.projects_grid.cols = cols
            
            # Update TopBar height based on screen size
            if hasattr(self.ids, 'top_bar'):
                if category in ["tablet", "large_tablet"]:
                    self.ids.top_bar.height = dp(72)
                else:
                    self.ids.top_bar.height = dp(64)
            
            # Adjust card spacing based on screen size
            if hasattr(self.ids, 'projects_grid'):
                if category == "phone":
                    self.ids.projects_grid.spacing = dp(12)
                elif category == "small_tablet":
                    self.ids.projects_grid.spacing = dp(16)
                else:
                    self.ids.projects_grid.spacing = dp(20)
                        
        except Exception as e:
            # Fallback to single column
            if hasattr(self.ids, 'projects_grid'):
                self.ids.projects_grid.cols = 1
    

    
    def filter_projects(self, filter_type):
        """Filter projects by type"""
        self.current_filter = filter_type
        
        # Update button states
        self.update_filter_button_states(filter_type)
        
        # Apply filter to current projects data
        self.apply_current_filter()
        
        # Refresh UI with filtered data
        self.refresh_projects_ui()
    
    def update_filter_button_states(self, active_filter):
        """Update the visual state of filter buttons using KivyMD 2.0 styling"""
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
                    button.style = "filled"
                    button.md_bg_color = self.theme_cls.primaryColor
                    button.elevation = 3
                else:
                    # Inactive button styling
                    button.style = "outlined"
                    button.line_color = self.theme_cls.outlineColor
                    button.elevation = 1
    
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
            return datetime.min
    
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
            menu_items = [
                {
                    "text": "Name (A-Z)",
                    "leading_icon": "sort-alphabetical-ascending",
                    "on_release": lambda: self.sort_projects("name")
                },
                {
                    "text": "Newest First", 
                    "leading_icon": "sort-calendar-descending",
                    "on_release": lambda: self.sort_projects("date_new")
                },
                {
                    "text": "Oldest First", 
                    "leading_icon": "sort-calendar-ascending",
                    "on_release": lambda: self.sort_projects("date_old")
                },
                {
                    "text": "Sync Status", 
                    "leading_icon": "sync",
                    "on_release": lambda: self.sort_projects("status")
                },
            ]
            
            self.sort_menu = MDDropdownMenu(
                caller=self.ids.sort_btn if hasattr(self.ids, 'sort_btn') else self.ids.view_toggle_btn,
                items=menu_items,
                width=dp(200),
                position="bottom"
            )
            self.sort_menu.open()
            
        except Exception as e:
            print(f"Error showing sort menu: {e}")
            toast("Sort options unavailable")
    
    def sort_projects(self, sort_type):
        """Sort projects by specified type"""
        if self.sort_menu:
            self.sort_menu.dismiss()
            
        self.current_sort = sort_type
        
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
        
        view_mode = "Grid" if self.is_grid_view else "List"
        toast(f"Switched to {view_mode} view")
    
    def refresh_projects_ui(self):
        """Refresh the projects UI with current filtered/sorted data"""        
        if not hasattr(self.ids, 'projects_grid'):
            return
            
        # Clear current grid
        self.ids.projects_grid.clear_widgets()
        
        # Remove any existing load more button
        if hasattr(self.ids, 'load_more_button') and hasattr(self.ids.load_more_button, 'parent') and self.ids.load_more_button.parent:
            try:
                self.ids.content_layout.remove_widget(self.ids.load_more_button)
            except:
                pass
        
        # Display filtered projects
        if not self.filtered_projects_data:
            self.show_empty_state()
        else:
            for project in self.filtered_projects_data:
                project_item = self.create_modern_project_item(project)
                if project_item:
                    self.ids.projects_grid.add_widget(project_item)
    
    def create_modern_project_item(self, project):
        """Create a modern project item"""
        try:
            if not ProjectItem:
                return None
            
            project_item = ProjectItem(
                project_id=str(project.get('id', '')),
                name=project.get('name', 'No Name'),
                description=project.get('description') or 'No description',
                created_at=project.get('created_at', ''),
                sync_status=project.get('sync_status', 'unknown')
            )
            
            # Bind events
            project_item.bind(
                on_edit=lambda instance, pid=project.get('id'): self.edit_project(pid),
                on_delete=lambda instance, pid=project.get('id'): self.delete_project(pid),
                on_build_form=lambda instance, pid=project.get('id'): self.go_to_form_builder(pid)
            )
            
            return project_item
            
        except Exception as e:
            print(f"Error creating project item: {e}")
            return None
    
    def show_empty_state(self):
        """Show appropriate empty state message with modern styling"""
        try:
            if self.current_filter == "all":
                title = "No Projects Yet"
                message = "Create your first project to get started!"
                icon = "plus-circle-outline"
            else:
                filter_names = {
                    "recent": "recent projects",
                    "synced": "synced projects", 
                    "pending": "pending projects"
                }
                filter_name = filter_names.get(self.current_filter, "projects")
                title = f"No {filter_name.title()} Found"
                message = "Try a different filter or create a new project."
                icon = "filter-variant-remove"
            
            # Create modern empty state card
            from kivymd.uix.card import MDCard
            from kivymd.uix.boxlayout import MDBoxLayout
            from kivymd.uix.label import MDLabel
            from kivymd.uix.button import MDButton, MDButtonText
            from kivymd.uix.button import MDIconButton
            
            empty_card = MDCard(
                orientation="vertical",
                size_hint=(None, None),
                size=(dp(300), dp(200)),
                pos_hint={'center_x': 0.5},
                padding=dp(24),
                spacing=dp(16),
                elevation=0,
                style="outlined"
            )
            
            # Icon
            icon_widget = MDIconButton(
                icon=icon,
                theme_icon_color="Secondary",
                size_hint=(None, None),
                size=(dp(48), dp(48)),
                pos_hint={'center_x': 0.5}
            )
            
            # Title
            title_label = MDLabel(
                text=title,
                font_style="Headline",
                role="small",
                theme_text_color="Primary",
                halign="center",
                size_hint_y=None,
                height=dp(32)
            )
            
            # Message
            message_label = MDLabel(
                text=message,
                font_style="Body",
                role="medium",
                theme_text_color="Secondary",
                halign="center",
                size_hint_y=None,
                height=dp(48),
                text_size=(dp(250), None)
            )
            
            empty_card.add_widget(icon_widget)
            empty_card.add_widget(title_label)
            empty_card.add_widget(message_label)
            
            # Add action button for "all" filter
            if self.current_filter == "all":
                create_button = MDButton(
                    MDButtonText(text="Create Project"),
                    style="filled",
                    size_hint=(None, None),
                    size=(dp(140), dp(40)),
                    pos_hint={'center_x': 0.5},
                    on_release=lambda x: self.navigate_to_project_creation()
                )
                empty_card.add_widget(create_button)
            
            self.ids.projects_grid.add_widget(empty_card)
            
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
        """Check for network and sync projects if online"""
        self.show_loader(True, "Syncing projects...")
        
        def _check_network_and_sync():
            try:
                if self.auth_service:
                    is_online = self.auth_service._check_network_connectivity()
                    if is_online:
                        Clock.schedule_once(lambda dt: toast("Network online. Syncing..."))
                        if self.sync_service:
                            self.sync_service.sync()
                        Clock.schedule_once(lambda dt: self.load_projects(clear_existing=True), 2)
                    else:
                        Clock.schedule_once(lambda dt: toast("Network offline. Loading local data."))
                        self.load_projects(clear_existing=True)
                else:
                    Clock.schedule_once(lambda dt: toast("Authentication service not available"))
                    self.load_projects(clear_existing=True)
            except Exception as e:
                print(f"Error in network check: {e}")
                Clock.schedule_once(lambda dt: self.load_projects(clear_existing=True))

        threading.Thread(target=_check_network_and_sync, daemon=True).start()

    def show_loader(self, show=True, message="Loading..."):
        """Show/hide loading overlay with progress indicator"""
        if self.loading_overlay:
            if show:
                self.loading_overlay.show(message)
            else:
                self.loading_overlay.hide()
        elif show:
            # Simple toast feedback if no loading overlay available
            toast(message)

    def open_project_dialog(self, is_edit=False, existing_data=None):
        """Open project dialog with streamlined responsive layout"""
        try:
            if not ProjectDialog:
                toast("Project dialog not available")
                return
                
            # Store dialog content reference
            self.dialog_content = ProjectDialog()
            self.dialog_content.projects_screen = self
            
            if is_edit and existing_data:
                self.dialog_content.set_data(**existing_data)
                self.current_project_id = existing_data.get('id')
            else:
                self.current_project_id = None
            
            # Use responsive helper for clean dialog sizing
            from widgets.responsive_layout import ResponsiveHelper
            
            # Get optimal dialog dimensions
            dialog_width, dialog_height = ResponsiveHelper.get_dialog_size()
            
            # Create dialog with simple, consistent properties
            self.dialog = MDDialog(
                size_hint=(None, None),
                size=(dialog_width, dialog_height),
                auto_dismiss=False,
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                radius=[dp(16)],
                elevation=4
            )
            
            # Add content to dialog
            self.dialog.add_widget(self.dialog_content)
            
            # Set dialog reference in content for button handling
            self.dialog_content.set_dialog_reference(self.dialog)
            
            # Open dialog and focus first field
            self.dialog.open()
            Clock.schedule_once(lambda dt: self.dialog_content.focus_first_field(), 0.2)

        except Exception as e:
            print(f"Error opening project dialog: {str(e)}")
            toast(f"Error opening dialog")

    def save_project(self, instance):
        """Save project with enhanced validation"""
        if not self.project_service or not self.dialog_content:
            toast("Project service not available")
            return
            
        self.show_loader(True, "Saving project...")
        
        try:
            # Get data from the dialog content
            project_data = self.dialog_content.get_data()
            
            # Enhanced validation check
            if not self.dialog_content.is_valid():
                toast("Please check your input and try again")
                self.show_loader(False)
                return
            
            if not project_data.get('is_valid', False):
                toast("Project name is required")
                self.show_loader(False)
                return

            # Clean data for API call
            api_data = {
                'name': project_data['name'],
                'description': project_data['description']
            }

            if self.current_project_id:
                self._execute_api_call(self.project_service.update_project, self.current_project_id, api_data)
            else:
                self._execute_api_call(self.project_service.create_project, api_data)

            self.close_dialog()

        except Exception as e:
            print(f"Error in save_project: {str(e)}")
            toast(f"Error saving project: {str(e)}")
            self.show_loader(False)

    def _execute_api_call(self, api_func, *args):
        """Execute API call in background thread"""
        def run_in_thread():
            result = {}
            try:
                result = api_func(*args)
            except Exception as e:
                print(f"Error during API call: {str(e)}")
                result = {'message': f"An error occurred: {str(e)}"}
            finally:
                Clock.schedule_once(lambda dt: self._process_api_result(result))

        threading.Thread(target=run_in_thread, daemon=True).start()
    
    def close_dialog(self, *args):
        """Close the current dialog"""
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
            self.dialog_content = None
    
    def _update_save_button_state(self):
        """Update save button state based on dialog content validation"""
        try:
            if self.dialog_content:
                # The dialog content now handles its own save button state
                self.dialog_content._update_save_button()
        except Exception as e:
            print(f"Error updating save button state: {e}")

    def _process_api_result(self, result):
        """Process API call result"""
        self.show_loader(False)
        if result.get('message'):
            toast(result['message'])
        else:
            # Default success messages
            if self.current_project_id:
                toast("Project updated successfully")
            else:
                toast("Project created successfully")
        if result.get('reload', True):  # Default to True for refresh
            self.load_projects(clear_existing=True)

    def search_projects(self, query):
        """Search projects"""
        self.load_projects(search_query=query, clear_existing=True)

    def load_projects(self, search_query=None, clear_existing=False):
        """Load projects from service"""
        if self.is_loading:
            return
            
        if not self.project_service:
            self.show_empty_state()
            return
            
        self.is_loading = True
        self.show_loader(True, "Loading projects...")

        if clear_existing:
            self.current_offset = 0
            self.projects_data = []
            if hasattr(self.ids, 'projects_grid'):
                self.ids.projects_grid.clear_widgets()
            if hasattr(self.ids, 'load_more_button') and hasattr(self.ids, 'content_layout'):
                try:
                    self.ids.content_layout.remove_widget(self.ids.load_more_button)
                except:
                    pass

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
                print(f"Error loading projects: {str(e)}")
                toast(f"Error loading projects: {str(e)}")
            finally:
                self.is_loading = False
                Clock.schedule_once(lambda dt: self.show_loader(False))

        threading.Thread(target=_load_in_thread, daemon=True).start()

    def _update_ui_with_projects(self, new_projects, is_last_page):
        """Update UI with loaded projects"""
        if hasattr(self.ids, 'load_more_button') and self.ids.load_more_button.parent:
             self.ids.content_layout.remove_widget(self.ids.load_more_button)

        # Apply current filter and sort to the newly loaded projects
        self.apply_current_filter()
        
        # Use refresh_projects_ui for consistent display
        self.refresh_projects_ui()

        # Add load more button if needed
        if not is_last_page:
            try:
                load_more_button = MDButton(
                    MDButtonText(text="Load More Projects"),
                    style="outlined",
                    size_hint=(None, None),
                    size=(dp(200), dp(48)),
                    pos_hint={'center_x': 0.5},
                    on_release=lambda x: self.load_projects(
                        search_query=self.ids.search_field.text if hasattr(self.ids, 'search_field') else ""
                    )
                )
                
                self.ids.load_more_button = load_more_button
                self.ids.content_layout.add_widget(load_more_button)
                
            except Exception as e:
                print(f"Error creating load more button: {e}")

    def edit_project(self, project_id):
        """Edit existing project"""
        project_data = next((p for p in self.projects_data if str(p.get('id')) == str(project_id)), None)
        if project_data:
            self.open_project_dialog(is_edit=True, existing_data=project_data)

    def delete_project(self, project_id):
        """Delete project with confirmation"""
        if not self.project_service:
            toast("Project service not available")
            return
            
        project_name = "Unknown"
        project_data = next((p for p in self.projects_data if str(p.get('id')) == str(project_id)), None)
        if project_data:
            project_name = project_data.get('name', 'Unknown')
        
        def confirm_delete(instance):
            self.show_loader(True, "Deleting project...")
            self._execute_api_call(self.project_service.delete_project, project_id)
            delete_dialog.dismiss()

        delete_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Delete Project?"
            ),
            MDDialogSupportingText(
                text=f"Are you sure you want to delete '{project_name}'? This action cannot be undone and all project data will be permanently deleted."
            ),
            MDDialogButtonContainer(
                Widget(),  # Spacer
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="outlined",
                    on_release=lambda x: delete_dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Delete"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color=(0.8, 0.2, 0.2, 1),  # Red background
                    on_release=confirm_delete
                ),
                spacing="8dp",
            ),
        )
        delete_dialog.open()

    def go_to_form_builder(self, project_id):
        """Navigate to form builder"""
        if self.manager:
            self.manager.current = 'form_builder'
            form_builder_screen = self.manager.get_screen('form_builder')
            form_builder_screen.project_id = project_id

    def create_new_project(self, instance):
        """Create new project"""
        self.navigate_to_project_creation()
    
    def navigate_to_project_creation(self):
        """Navigate to project creation screen"""
        try:
            app = App.get_running_app()
            if hasattr(app.root, 'current'):
                app.root.current = 'project_creation'
        except Exception as e:
            print(f"Error navigating to project creation: {e}")
            toast("Error opening project creation screen")
    
