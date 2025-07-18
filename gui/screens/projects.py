from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from utils.toast import toast
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.app import App

from widgets.project_dialog import ProjectDialog
from widgets.loading_overlay import LoadingOverlay
from widgets.top_bar import TopBar
from widgets.responsive_layout import ResponsiveHelper
from services.project_service import ProjectService

import threading
from datetime import datetime
import traceback

# Load KV file only once to prevent duplicate rule application
try:
    Builder.load_file("kv/projects.kv")
except Exception as e:
    # If KV file is already loaded, ignore the error
    if "rule not in self.rulectx" not in str(e):
        print(f"Error loading projects.kv: {e}")


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
        
        # Initialize loading overlay
        self.loading_overlay = LoadingOverlay()
        
        # Bind window resize event
        Window.bind(on_resize=self.on_window_resize)

    def on_enter(self):
        self.ids.top_bar.set_title("Projects")
        
        # Initialize responsive layout
        self.update_responsive_layout()
        
        # Set initial filter state to "all" and update chip states
        self.current_filter = "all"
        
        # Update filter chip states using latest KivyMD approach
        try:
            self.update_filter_chip_states("all")
        except:
            pass
        Clock.schedule_once(lambda dt: self.update_filter_chip_states("all"), 0.5)
        
        # Load projects first, then apply filter
        self.check_and_sync_projects()
        
        # Add a test project item to see if widget creation works

    def on_window_resize(self, window, width, height):
        """Handle window resize for responsive layout adjustments"""
        try:
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
            
            # Update responsive spacing and padding
            self.update_responsive_spacing(category)
            
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
    
    def update_responsive_spacing(self, category):
        """Update spacing and padding based on screen size"""
        if not hasattr(self.ids, 'projects_grid'):
            return
            
        grid = self.ids.projects_grid
        
        # Update spacing based on screen size
        if category in ["tablet", "large_tablet"]:
            grid.spacing = dp(20)
            grid.padding = dp(24)
        else:
            grid.spacing = dp(16)
            grid.padding = dp(16)
    
    def filter_projects(self, filter_type):
        """Filter projects by type using latest KivyMD filter chip approach"""
        self.current_filter = filter_type
        print(f"Projects: Filtering by {filter_type}")
        
        # Update filter chip states using the new approach
        self.update_filter_chip_states(filter_type)
        
        # Apply filter to current projects data
        self.apply_current_filter()
        
        # Refresh UI with filtered data
        self.refresh_projects_ui()
    
    def update_filter_chip_states(self, active_filter):
        """Update the visual state of filter chips using latest KivyMD approach"""
        filter_chips = {
            "all": "filter_all_btn",
            "recent": "filter_recent_btn", 
            "synced": "filter_synced_btn",
            "pending": "filter_pending_btn"
        }
        
        for filter_name, chip_id in filter_chips.items():
            if hasattr(self.ids, chip_id):
                chip = getattr(self.ids, chip_id)
                is_active = (filter_name == active_filter)
                chip.active = is_active
                
                # Update colors manually for proper visual feedback
                if is_active:
                    # Active chip - blue background
                    chip.md_bg_color = (0.2, 0.6, 1.0, 1.0)  # Blue color
                    # Update text color to white for better contrast
                    if hasattr(chip, 'ids') and hasattr(chip.ids, 'chip_text'):
                        chip.ids.chip_text.text_color = (1, 1, 1, 1)
                        chip.ids.chip_text.theme_text_color = "Custom"
                else:
                    # Inactive chip - light blue background
                    chip.md_bg_color = (0.8, 0.9, 1.0, 1)  # Light blue
                    # Update text color to black
                    if hasattr(chip, 'ids') and hasattr(chip.ids, 'chip_text'):
                        chip.ids.chip_text.text_color = (0, 0, 0, 1)
                        chip.ids.chip_text.theme_text_color = "Custom"
    
    def on_filter_chip_click(self, filter_type):
        """Handle filter chip clicks - simpler approach using on_release"""
        print(f"Filter chip {filter_type} clicked!")
        print(f"Current projects data count: {len(self.projects_data)}")
        
        # If clicking the same filter, do nothing (keep it active)
        if self.current_filter == filter_type:
            print(f"Filter {filter_type} is already active, no change needed")
            return
        
        # Apply the new filter
        self.filter_projects(filter_type)
    
    def apply_current_filter(self):
        """Apply the current filter to projects data"""
        print(f"Applying filter: {self.current_filter}")
        print(f"Total projects data: {len(self.projects_data)}")
        
        # Debug: Print sample project data to understand structure
        if self.projects_data:
            sample_project = self.projects_data[0]
            print(f"Sample project data: {sample_project}")
            print(f"Sample project keys: {list(sample_project.keys())}")
        
        if self.current_filter == "all":
            self.filtered_projects_data = self.projects_data.copy()
        elif self.current_filter == "recent":
            # Filter to projects created in last 30 days
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=30)
            print(f"Recent filter cutoff date: {cutoff_date}")
            
            self.filtered_projects_data = []
            for p in self.projects_data:
                created_date = self.parse_project_date(p.get('created_at', ''))
                print(f"Project '{p.get('name', 'Unknown')}' created: {created_date}")
                if created_date > cutoff_date:
                    self.filtered_projects_data.append(p)
                    
        elif self.current_filter == "synced":
            print("Checking sync status for projects:")
            self.filtered_projects_data = []
            for p in self.projects_data:
                sync_status = p.get('sync_status', '').lower()
                print(f"Project '{p.get('name', 'Unknown')}' sync_status: '{sync_status}'")
                if sync_status == 'synced':
                    self.filtered_projects_data.append(p)
                    
        elif self.current_filter == "pending":
            print("Checking pending status for projects:")
            self.filtered_projects_data = []
            for p in self.projects_data:
                sync_status = p.get('sync_status', '').lower()
                print(f"Project '{p.get('name', 'Unknown')}' sync_status: '{sync_status}'")
                if sync_status in ['pending', 'failed']:
                    self.filtered_projects_data.append(p)
        
        print(f"Filtered projects count: {len(self.filtered_projects_data)}")
        
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
                {
                    "text": "Name (A-Z)",
                    "on_release": lambda x="name": self.sort_projects(x),
                },
                {
                    "text": "Newest First",
                    "on_release": lambda x="date_new": self.sort_projects(x),
                },
                {
                    "text": "Oldest First",
                    "on_release": lambda x="date_old": self.sort_projects(x),
                },
                {
                    "text": "Sync Status",
                    "on_release": lambda x="status": self.sort_projects(x),
                },
            ]

            self.sort_menu = MDDropdownMenu(
                caller=self.ids.sort_button,
                items=menu_items,
                width_mult=4,
                position="auto",
            )
            self.sort_menu.open()

        except Exception as e:
            print(f"Error showing sort menu: {e}")
            from kivymd.uix.snackbar import Snackbar
            Snackbar(
                text="Sort options coming soon",
                duration=3
            ).open()

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
        
        # Refresh the UI to show the new view mode
        self.refresh_projects_ui()
        
        # Show user feedback
        view_mode = "Grid" if self.is_grid_view else "List"
        toast(f"Switched to {view_mode} view")
        
        print(f"Projects: Toggled to {'grid' if self.is_grid_view else 'list'} view")
    
    def refresh_projects_ui(self):
        """Refresh the projects UI with current filtered/sorted data"""
        
        
        # Debug: Print all projects data
        for i, project in enumerate(self.projects_data):
            print(f"Project {i+1}: {project}")
        
        # Clear current grid
        print(f"Grid before clearing: {len(self.ids.projects_grid.children)} children")
        self.ids.projects_grid.clear_widgets()
        print(f"Grid cleared. Grid children count: {len(self.ids.projects_grid.children)}")
        
        # Remove any existing load more button
        if hasattr(self.ids, 'load_more_button') and self.ids.load_more_button.parent:
            self.ids.content_layout.remove_widget(self.ids.load_more_button)
        
        # Display filtered projects
        if not self.filtered_projects_data:
            print("No filtered projects, showing empty state")
            self.show_empty_state()
        else:
            print(f"Adding {len(self.filtered_projects_data)} projects to grid")
            for i, project in enumerate(self.filtered_projects_data):
                print(f"Creating project item {i+1}: {project.get('name', 'Unknown')}")
                
                try:
                    # Create actual ProjectItem widget
                    project_item = self.create_tablet_optimized_project_item(project)
                    print(f"Project item created successfully: {project_item}")
                    print(f"Project item size: {project_item.size}, pos: {project_item.pos}")
                    print(f"Project item visible: {project_item.opacity}, disabled: {project_item.disabled}")
                    
                    # Add to grid
                    self.ids.projects_grid.add_widget(project_item)
                    print(f"Project item added to grid. Grid children count: {len(self.ids.projects_grid.children)}")
                    
                    # Force layout update
                    self.ids.projects_grid.do_layout()
                    print(f"Grid layout updated. Grid size: {self.ids.projects_grid.size}")
                    
                except Exception as e:
                    print(f"Error creating project item: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    # Fallback to simple card if ProjectItem fails
                    from kivymd.uix.card import MDCard
                    from kivymd.uix.label import MDLabel
                    
                    fallback_card = MDCard(
                        style="outlined",
                        line_color=(0.8, 0.8, 0.8, 1),
                        md_bg_color=(1, 1, 1, 1),
                        size_hint=(1, None),
                        height=dp(120),
                        padding=dp(16)
                    )
                    fallback_card.add_widget(
                        MDLabel(
                            text=f"Project: {project.get('name', 'Unknown')}",
                            halign='center',
                            theme_text_color="Primary"
                        )
                    )
                    self.ids.projects_grid.add_widget(fallback_card)
                    print(f"Added fallback card. Grid children count: {len(self.ids.projects_grid.children)}")
        
        print(f"=== END REFRESH PROJECTS UI ===")
        print(f"Final grid children count: {len(self.ids.projects_grid.children)}")
    
    def create_tablet_optimized_project_item(self, project):
        """Create a tablet-optimized project item"""
        try:
            from widgets.project_item import ProjectItem
            
            category = ResponsiveHelper.get_screen_size_category()
            print(f"Creating project item for category: {category}")
            
            # Create project item with responsive sizing
            project_item = ProjectItem(
                project_id=str(project.get('id', '')),
                name=project.get('name', 'No Name'),
                description=project.get('description') or 'No description',
                created_at=project.get('created_at', ''),
                sync_status=project.get('sync_status', 'unknown')
            )
            
            print(f"Project item created with name: {project_item.name}")
            
            # Apply tablet-specific styling if needed
            if category in ["tablet", "large_tablet"]:
                # Set height to match grid row height for tablets
                project_item.height = dp(140)
                print(f"Applied tablet styling: height={project_item.height}")
            else:
                project_item.height = dp(120)  # Match grid row height for phones
                print(f"Applied phone styling: height={project_item.height}")
            
            # Bind events
            project_item.bind(
                on_edit=lambda instance, pid=project.get('id'): self.edit_project(pid),
                on_delete=lambda instance, pid=project.get('id'): self.delete_project(pid),
                on_build_form=lambda instance, pid=project.get('id'): self.go_to_form_builder(pid)
            )
            
            print(f"Project item ready: size={project_item.size}, visible={project_item.opacity}")
            return project_item
            
        except Exception as e:
            print(f"Error creating tablet project item: {e}")
            import traceback
            traceback.print_exc()
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
            
            # Use proper KivyMD font styling approach
            empty_label = MDLabel(
                text=message,
                size_hint_y=None,
                height=height,
                halign='center',
                theme_text_color="Secondary"
            )
            self.ids.projects_grid.add_widget(empty_label)
            
        except Exception as e:
            print(f"Error showing empty state: {e}")
            # Fallback with simple Label to avoid any KivyMD font issues
            empty_label = Label(
                text="No projects found.",
                size_hint_y=None,
                height=dp(100),
                halign='center',
                color=(0.5, 0.5, 0.5, 1)  # Gray color for secondary text
            )
            self.ids.projects_grid.add_widget(empty_label)

    def check_and_sync_projects(self):
        """Check for network and sync projects if online."""
        self.show_loader(True, "Syncing projects...")
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

    def show_loader(self, show=True, message="Loading..."):
        if show:
            self.loading_overlay.show(message)
        else:
            self.loading_overlay.hide()

    def create_tablet_dialog_button(self, text, on_release, is_primary=False, disabled=False, **kwargs):
        """Create a tablet-optimized dialog button"""
        try:
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
            button = MDButton(
                style="elevated",
                on_release=on_release,
                size_hint_y=None,
                height=height,
                size_hint_x=None,
                width=width,
                disabled=disabled,
                **kwargs
            )
            button.add_widget(
                MDButtonText(
                    text=text,
                    font_size=font_size
                )
            )
            
            return button
            
        except Exception as e:
            print(f"Error creating tablet dialog button: {e}")
            # Fallback to standard button
            fallback_button = MDButton(
                style="elevated",
                on_release=on_release,
                disabled=disabled,
                **kwargs
            )
            fallback_button.add_widget(
                MDButtonText(
                    text=text
                )
            )
            return fallback_button

    def open_project_dialog(self, is_edit=False, existing_data=None):
        try:
            print("Opening project dialog...")
            content = ProjectDialog()
            if is_edit and existing_data:
                content.set_data(**existing_data)
                self.current_project_id = existing_data.get('id')
            else:
                self.current_project_id = None

            # Store the content reference for later access
            self.dialog_content = content

            # Set up button callbacks
            content.set_save_callback(self.save_project)
            content.set_cancel_callback(lambda x: self.dialog.dismiss())

            # Also bind to text changes for immediate feedback
            def on_name_change(instance, value):
                # Trigger validation check
                content.validate_name()
                # Update button state
                content.on_validation_change(None, None)

            content.ids.name_field.bind(text=on_name_change)

            self.dialog = MDDialog(
                MDDialogHeadlineText(
                    text="Edit Project" if is_edit else "New Project",
                ),
                MDDialogContentContainer(
                    content
                ),
                MDDialogButtonContainer(
                    Widget(),
                    MDButton(
                        MDButtonText(text="Cancel"),
                        style="outlined",
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDButton(
                        MDButtonText(text="Save"),
                        style="filled",
                        id="save_button",
                        on_release=self.save_project
                    ),
                    spacing="8dp",
                ),
            )
            self.dialog.open()
        except Exception as e:
            print("Error opening project dialog:")
            traceback.print_exc()
            toast("Error opening project dialog")

    def save_project(self, instance):
        """Save project with enhanced validation and tablet UX"""
        try:
            # Get data from the dialog's content - access the ProjectDialog directly
            # Since we're using the ProjectDialog as the content, we can access it directly
            content = self.dialog.children[0].children[0]  # Get the ProjectDialog from the dialog structure
            
            # Alternative approach: store the content reference when creating the dialog
            if hasattr(self, 'dialog_content'):
                content = self.dialog_content
            else:
                # Fallback: try to find the ProjectDialog in the dialog structure
                for child in self.dialog.children:
                    if hasattr(child, 'children'):
                        for grandchild in child.children:
                            if hasattr(grandchild, 'get_data'):
                                content = grandchild
                                break
                        if hasattr(content, 'get_data'):
                            break
            
            if not content or not hasattr(content, 'get_data'):
                print("Error: Could not find ProjectDialog content")
                toast("Error accessing dialog content")
                return
                
            project_data = content.get_data()
            
            # Enhanced validation check with detailed feedback
            if not content.is_valid():
                # Check specific validation issues
                name_errors = []
                desc_errors = []
                
                if not content.validate_name():
                    name_errors.append("Project name validation failed")
                if not content.validate_description():
                    desc_errors.append("Description validation failed")
                
                # Show specific error messages
                error_messages = []
                if name_errors:
                    error_messages.extend(name_errors)
                if desc_errors:
                    error_messages.extend(desc_errors)
                
                if error_messages:
                    error_text = "\n".join(error_messages)
                    Clock.schedule_once(lambda dt: toast(f"Please fix the following issues:\n{error_text}"))
                else:
                    Clock.schedule_once(lambda dt: toast("Please check your input and try again"))
                return
            
            if not project_data.get('is_valid', False):
                Clock.schedule_once(lambda dt: toast("Project name is required"))
                return

            # Show loading state
            self.show_loader(True, "Saving project...")

            # Clean data for API call
            api_data = {
                'name': project_data['name'].strip(),
                'description': project_data['description'].strip()
            }

            # Validate data one more time before API call
            if not api_data['name'] or len(api_data['name']) < 2:
                Clock.schedule_once(lambda dt: toast("Project name must be at least 2 characters"))
                self.show_loader(False)
                return

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
            
            # Provide more user-friendly error messages
            if "network" in err_msg.lower() or "connection" in err_msg.lower():
                user_msg = "Network error. Please check your connection and try again."
            elif "timeout" in err_msg.lower():
                user_msg = "Request timed out. Please try again."
            elif "validation" in err_msg.lower():
                user_msg = "Please check your input and try again."
            else:
                user_msg = f"Error saving project: {err_msg}"
            
            Clock.schedule_once(lambda dt: toast(user_msg))
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
        self.show_loader(True, "Loading projects...")

        if clear_existing:
            self.current_offset = 0
            self.projects_data = []
            self.ids.projects_grid.clear_widgets()
            if hasattr(self.ids, 'load_more_button'):
                self.ids.content_layout.remove_widget(self.ids.load_more_button)

        def _load_in_thread():
            try:
                print(f"=== LOADING PROJECTS ===")
                print(f"Search query: {search_query}")
                print(f"Limit: {self.page_limit}, Offset: {self.current_offset}")
                
                projects, error = self.project_service.load_projects(
                    search_query=search_query,
                    limit=self.page_limit,
                    offset=self.current_offset
                )
                
                print(f"Projects loaded: {len(projects) if projects else 0}")
                print(f"Error: {error}")
                
                if error:
                    raise Exception(error)
                
                if projects:
                    print(f"Projects data: {projects}")
                    self.projects_data.extend(projects)
                    self.current_offset += len(projects)
                    print(f"Total projects data now: {len(self.projects_data)}")
                else:
                    print("No projects returned from service")
                
                Clock.schedule_once(lambda dt: self._update_ui_with_projects(projects, len(projects) < self.page_limit))
            except Exception as e:
                print(f"Error in load_projects: {str(e)}")
                import traceback
                traceback.print_exc()
                err_msg = str(e)
                Clock.schedule_once(lambda dt: toast(f"Error loading projects: {err_msg}"))
            finally:
                self.is_loading = False
                Clock.schedule_once(lambda dt: self.show_loader(False))
                print(f"=== END LOADING PROJECTS ===")

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
                category = ResponsiveHelper.get_screen_size_category()
                
                # Tablet-optimized load more button
                button_height = dp(52) if category in ["tablet", "large_tablet"] else dp(48)
                button_width = dp(160) if category in ["tablet", "large_tablet"] else dp(140)
                font_size = "16sp" if category in ["tablet", "large_tablet"] else "14sp"
                
                self.ids.load_more_button = MDButton(
                    style="elevated",
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
                self.ids.load_more_button = MDButton(
                    style="elevated",
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
            self.show_loader(True, "Deleting project...")
            self._execute_api_call(self.project_service.delete_project, project_id)
            delete_dialog.dismiss()
            
        def cancel_delete(instance):
            delete_dialog.dismiss()
            
        # Create dialog using latest KivyMD approach
        delete_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Delete Project?"
            ),
            MDDialogContentContainer(
                MDLabel(
                    text="This action cannot be undone.",
                    size_hint_y=None,
                    height=dp(48),
                    halign='center',
                    theme_text_color="Error"
                )
            ),
            MDDialogButtonContainer(
                Widget(),
                
                MDButton(
                    MDButtonText(text="Cancel"),
                    style="outlined",
                    on_release=cancel_delete
                ),
                MDButton(
                    MDButtonText(text="Delete"),
                    style="filled",
                    on_release=confirm_delete,
                    md_bg_color=(0.8, 0.2, 0.2, 1)  # Red color for delete
                ),
                spacing="8dp",
                size_hint_y=None,
                height=dp(48)
            )
        )
        delete_dialog.open()

    def go_to_form_builder(self, project_id):
        self.manager.current = 'form_builder'
        form_builder_screen = self.manager.get_screen('form_builder')
        form_builder_screen.project_id = project_id

    
    def create_new_project(self, instance=None):
        print("Creating new project...")
        try:
            self.open_project_dialog()
        except Exception as e:
            print(f"Error creating new project: {e}")
            toast("Error opening project dialog")
