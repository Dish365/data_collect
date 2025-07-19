from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon, MDListItemTrailingIcon
from kivymd.uix.dialog import (
    MDDialog, 
    MDDialogHeadlineText, 
    MDDialogSupportingText, 
    MDDialogButtonContainer, 
    MDDialogContentContainer
)
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.chip import MDChip
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.lang import Builder
from widgets.top_bar import TopBar
from kivymd.uix.widget import Widget
import threading
import traceback
import os

# Load the KV file using the same pattern as form_builder
Builder.load_file("kv/team_members.kv")


class AutocompleteTextField(MDTextField):
    """Custom text field with autocomplete functionality"""
    
    def __init__(self, autocomplete_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.autocomplete_callback = autocomplete_callback
        self.search_timer = None
        self.bind(text=self.on_text_change)
    
    def on_text_change(self, instance, text):
        """Handle text changes for autocomplete"""
        if self.search_timer:
            self.search_timer.cancel()
        
        if self.autocomplete_callback and len(text.strip()) >= 2:
            # Debounce the search - wait 500ms after user stops typing
            self.search_timer = Clock.schedule_once(
                lambda dt: self.autocomplete_callback(text.strip()), 0.5
            )
        elif self.autocomplete_callback and len(text.strip()) < 2:
            # Clear results if text is too short
            self.autocomplete_callback("")


class TeamMembersScreen(MDScreen):
    """Team Members Screen"""
    
    def __init__(self, dashboard_service, project_id=None, **kwargs):
        print(f"TeamMembersScreen.__init__ called with dashboard_service: {dashboard_service}")
        super().__init__(**kwargs)
        self.dashboard_service = dashboard_service
        self.project_id = project_id
        self.projects = []
        self.current_members = []
        self.selected_project = None
        self.search_results = []
        self.selected_user = None
        self.selected_role = "member"
        self.role_buttons = {}
        self.project_dropdown_menu = None
        self.add_member_dialog = None
        self.selected_role_modal = "member"
        self.selected_user_modal = None
        
        print(f"TeamMembersScreen initialized with name: {getattr(self, 'name', 'NO NAME')}")
        
        # Initialize after kv file is loaded
        Clock.schedule_once(self.setup_ui, 0.1)
    
    def on_enter(self):
        """Called when the screen is entered"""
        try:
            # Set top bar title
            if hasattr(self.ids, 'top_bar'):
                self.ids.top_bar.set_title("Team Members")
            
            print("TeamMembersScreen: on_enter called")
            
            # Load projects and team members when entering the screen
            self.load_initial_data()
            
        except Exception as e:
            print(f"Error in team members on_enter: {e}")
            import traceback
            print(traceback.format_exc())
    
    def setup_ui(self, dt):
        """Setup UI components after kv file is loaded"""
        try:
            print("Setting up Team Members UI...")
            print(f"Available IDs: {list(self.ids.keys()) if hasattr(self, 'ids') else 'No IDs'}")
            
            # Check if we have the basic IDs we need
            required_ids = ['role_layout', 'email_field', 'members_list', 'project_dropdown_text']
            missing_ids = [id_name for id_name in required_ids if not hasattr(self.ids, id_name) or getattr(self.ids, id_name) is None]
            
            if missing_ids:
                print(f"Missing required IDs: {missing_ids}")
                print("This might be because the KV file isn't loaded properly")
                # Don't retry infinitely, just skip setup
                return
            
            # Setup role buttons
            roles = ["viewer", "member", "analyst", "collaborator"]
            
            # Clear existing widgets
            self.ids.role_layout.clear_widgets()
            
            for role in roles:
                btn = MDButton(
                    text=role.title(),
                    size_hint=(None, None),
                    width=dp(80),
                    height=dp(36),
                    on_release=lambda x, r=role: self.select_role(r),
                    style="elevated",
                    md_bg_color=[0.8, 0.8, 0.8, 1]
                )
                self.role_buttons[role] = btn
                self.ids.role_layout.add_widget(btn)
            
            # Setup email field autocomplete
            if hasattr(self.ids, 'email_field') and self.ids.email_field:
                self.ids.email_field.autocomplete_callback = self.search_users
                print("Email field autocomplete setup complete")
            
            # Update role buttons appearance
            self.update_role_buttons()
            
            # Load initial data
            self.load_initial_data()
            
            print("Team Members UI setup complete")
            
        except Exception as e:
            print(f"Error in setup_ui: {e}")
            import traceback
            print(traceback.format_exc())
    
    def search_users(self, query):
        """Search for users and update autocomplete dropdown"""
        if not query:
            self.hide_dropdown()
            return
        
        def search_in_thread():
            try:
                users = self.dashboard_service.search_users(query)
                Clock.schedule_once(lambda dt: self.update_user_dropdown(users))
            except Exception as e:
                print(f"Error searching users: {e}")
                Clock.schedule_once(lambda dt: self.update_user_dropdown([]))
        
        threading.Thread(target=search_in_thread, daemon=True).start()
    
    def update_user_dropdown(self, users):
        """Update the user dropdown with search results"""
        if not hasattr(self.ids, 'user_dropdown_list') or not hasattr(self.ids, 'user_dropdown_card'):
            return
            
        self.search_results = users
        self.ids.user_dropdown_list.clear_widgets()
        
        if not users:
            self.hide_dropdown()
            return
        
        # Show dropdown
        max_height = min(len(users) * dp(48), dp(200))
        self.ids.user_dropdown_card.height = max_height
        
        for user in users:
            user_item = MDListItem(
                size_hint_y=None,
                height=dp(48),
                on_release=lambda x, u=user: self.select_user(u)
            )
            user_item.add_widget(MDListItemHeadlineText(text=user['display_text']))
            self.ids.user_dropdown_list.add_widget(user_item)
    
    def hide_dropdown(self):
        """Hide the user dropdown"""
        if hasattr(self.ids, 'user_dropdown_card') and hasattr(self.ids, 'user_dropdown_list'):
            self.ids.user_dropdown_card.height = dp(0)
            self.ids.user_dropdown_list.clear_widgets()
    
    def select_user(self, user):
        """Handle user selection from dropdown"""
        self.selected_user = user
        if hasattr(self.ids, 'email_field'):
            self.ids.email_field.text = user['email']
        if hasattr(self.ids, 'selected_user_label'):
            self.ids.selected_user_label.text = f"Selected: {user['display_text']}"
            self.ids.selected_user_label.height = dp(30)
        self.hide_dropdown()
    
    def select_role(self, role):
        """Handle role selection"""
        self.selected_role = role
        self.update_role_buttons()
    
    def update_role_buttons(self):
        """Update role button appearance"""
        for role, btn in self.role_buttons.items():
            if role == self.selected_role:
                btn.md_bg_color = [0.2, 0.6, 1, 1]  # Blue for selected
            else:
                btn.md_bg_color = [0.8, 0.8, 0.8, 1]  # Gray for unselected
    
    def load_initial_data(self):
        """Load initial data"""
        def load_in_thread():
            try:
                # Get user's manageable projects
                projects = self.dashboard_service.get_user_projects_with_members()
                Clock.schedule_once(lambda dt: self.handle_projects_loaded(projects))
            except Exception as e:
                print(f"Error loading projects: {e}")
                Clock.schedule_once(lambda dt: self.handle_projects_loaded([]))
        
        threading.Thread(target=load_in_thread, daemon=True).start()
    
    def handle_projects_loaded(self, projects):
        """Handle projects loaded"""
        try:
            print(f"Projects loaded: {len(projects) if projects else 0}")
            self.projects = projects
            
            if not projects:
                if hasattr(self.ids, 'project_dropdown_text'):
                    self.ids.project_dropdown_text.text = "No manageable projects found"
                print("No projects available")
                return
            
            # Auto-select project if provided or use first project
            if self.project_id:
                selected_project = next((p for p in projects if p['id'] == self.project_id), None)
                if selected_project:
                    self.selected_project = selected_project
                    print(f"Selected provided project: {selected_project.get('name', 'Unknown')}")
                else:
                    self.selected_project = projects[0]
                    print(f"Provided project not found, using first project: {projects[0].get('name', 'Unknown')}")
            else:
                self.selected_project = projects[0]
                print(f"Using first project: {projects[0].get('name', 'Unknown')}")
            
            # Update the dropdown text
            if hasattr(self.ids, 'project_dropdown_text'):
                self.ids.project_dropdown_text.text = self.selected_project.get('name', 'Unknown Project')
                print(f"Updated dropdown text to: {self.selected_project.get('name', 'Unknown Project')}")
            
            # Update menu items if menu exists
            if self.project_dropdown_menu:
                self.update_menu_items()
            
            # Load team members for the selected project
            print("Loading team members for selected project...")
            self.load_project_members()
            
        except Exception as e:
            print(f"Error handling projects loaded: {e}")
            import traceback
            print(traceback.format_exc())
    
    def load_project_members(self):
        """Load current project members"""
        try:
            if not self.selected_project:
                print("No project selected, cannot load members")
                return
            
            print(f"Loading members for project: {self.selected_project.get('name', 'Unknown')} (ID: {self.selected_project.get('id', 'Unknown')})")
            
            def load_in_thread():
                try:
                    members = self.dashboard_service.get_project_members(self.selected_project['id'])
                    print(f"Loaded {len(members) if members else 0} team members")
                    Clock.schedule_once(lambda dt: self.update_members_list(members))
                except Exception as e:
                    print(f"Error loading project members: {e}")
                    import traceback
                    print(traceback.format_exc())
                    Clock.schedule_once(lambda dt: self.update_members_list([]))
            
            threading.Thread(target=load_in_thread, daemon=True).start()
            
        except Exception as e:
            print(f"Error in load_project_members: {e}")
            import traceback
            print(traceback.format_exc())
    
    def update_members_list(self, members):
        """Update the members list display"""
        try:
            if not hasattr(self.ids, 'members_list'):
                print("Members list widget not found")
                return
                
            print(f"Updating members list with {len(members) if members else 0} members")
            self.current_members = members
            self.ids.members_list.clear_widgets()
            
            if not members:
                print("No members to display, showing empty state")
                empty_item = MDListItem(
                    size_hint_y=None,
                    height=dp(48)
                )
                empty_item.add_widget(MDListItemHeadlineText(text="No team members yet"))
                self.ids.members_list.add_widget(empty_item)
                return
            
            print(f"Adding {len(members)} member items to the list")
            for member in members:
                try:
                    member_item = self.create_member_item(member)
                    self.ids.members_list.add_widget(member_item)
                except Exception as e:
                    print(f"Error creating member item: {e}")
                    import traceback
                    print(traceback.format_exc())
            
            print("Members list updated successfully")
            
        except Exception as e:
            print(f"Error updating members list: {e}")
            import traceback
            print(traceback.format_exc())
    
    def create_member_item(self, member):
        """Create a list item for a team member"""
        try:
            username = member.get('username', 'Unknown')
            email = member.get('email', 'No email')
            role = member.get('role', 'member').title()
            is_creator = member.get('is_creator', False)
            
            item_text = f"{username} ({email}) - {role}"
            if is_creator:
                item_text += " [Owner]"
            
            # Create list item
            item = MDListItem(
                size_hint_y=None,
                height=dp(48)
            )
            
            # Add user icon
            item.add_widget(MDListItemLeadingIcon(icon="account"))
            
            # Add headline text
            item.add_widget(MDListItemHeadlineText(text=item_text))
            
            # Add remove button (only if not creator)
            if not is_creator:
                remove_btn = MDListItemTrailingIcon(
                    icon="delete",
                    on_release=lambda x, m=member: self.show_remove_confirmation(m)
                )
                item.add_widget(remove_btn)
            
            return item
            
        except Exception as e:
            print(f"Error creating member item widget: {e}")
            # Return a simple fallback item
            fallback_item = MDListItem(
                size_hint_y=None,
                height=dp(48)
            )
            fallback_item.add_widget(MDListItemHeadlineText(text="Error loading member"))
            return fallback_item
    
    def add_member(self, *args):
        """Add a new team member"""
        if not self.selected_project:
            self.show_message("No project selected")
            return
        
        # Use selected user's email if available, otherwise use typed text
        email = ""
        if self.selected_user:
            email = self.selected_user['email']
        elif hasattr(self.ids, 'email_field') and self.ids.email_field.text.strip():
            email = self.ids.email_field.text.strip()
        
        if not email:
            self.show_message("Please search and select a user")
            return
        
        def invite_in_thread():
            try:
                success, message = self.dashboard_service.invite_team_member(
                    self.selected_project['id'],
                    email,
                    self.selected_role
                )
                Clock.schedule_once(lambda dt: self.handle_invite_result(success, message))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.handle_invite_result(False, str(e)))
        
        threading.Thread(target=invite_in_thread, daemon=True).start()
    
    def handle_invite_result(self, success, message):
        """Handle team member invite result"""
        self.show_message(message)
        if success:
            if hasattr(self.ids, 'email_field'):
                self.ids.email_field.text = ""
            self.selected_user = None
            if hasattr(self.ids, 'selected_user_label'):
                self.ids.selected_user_label.text = ""
                self.ids.selected_user_label.height = dp(0)
            self.hide_dropdown()
            self.load_project_members()  # Refresh the list
    
    def show_remove_confirmation(self, member):
        """Show confirmation dialog before removing team member"""
        try:
            username = member.get('username', 'Unknown')
            email = member.get('email', 'No email')
            
            # Create confirmation dialog content
            content = MDDialogContentContainer(
                MDBoxLayout(
                    orientation="vertical",
                    spacing=dp(16),
                    size_hint_y=None,
                    height=dp(100),
                    padding=dp(16)
                )
            )
            
            # Add confirmation message
            content.children[0].add_widget(
                MDLabel(
                    text=f"Are you sure you want to remove this team member?",
                    theme_text_color="Primary",
                    font_style="Body",
                    size_hint_y=None,
                    height=dp(30)
                )
            )
            
            content.children[0].add_widget(
                MDLabel(
                    text=f"{username} ({email})",
                    theme_text_color="Secondary",
                    font_style="Body",
                    size_hint_y=None,
                    height=dp(30),
                    bold=True
                )
            )
            
            # Create buttons
            cancel_button = MDButton(
                style="outlined",
                on_release=lambda x: self.remove_confirmation_dialog.dismiss()
            )
            cancel_button.add_widget(MDButtonText(text="Cancel"))
            
            confirm_button = MDButton(
                style="filled",
                on_release=lambda x: self.confirm_remove_member(member)
            )
            confirm_button.add_widget(MDButtonText(text="Remove"))
            
            # Create confirmation dialog
            self.remove_confirmation_dialog = MDDialog(
                MDDialogHeadlineText(text="Remove Team Member"),
                MDDialogSupportingText(text="This action cannot be undone."),
                content,
                MDDialogButtonContainer(
                    cancel_button,
                    confirm_button,
                )
            )
            
            self.remove_confirmation_dialog.open()
            
        except Exception as e:
            print(f"Error showing remove confirmation: {e}")
            import traceback
            print(traceback.format_exc())
    
    def confirm_remove_member(self, member):
        """Confirm and execute team member removal"""
        try:
            # Close confirmation dialog
            if hasattr(self, 'remove_confirmation_dialog'):
                self.remove_confirmation_dialog.dismiss()
            
            # Proceed with removal
            self.remove_member(member)
            
        except Exception as e:
            print(f"Error confirming member removal: {e}")
            import traceback
            print(traceback.format_exc())
    
    def remove_member(self, member):
        """Remove a team member"""
        if not self.selected_project:
            return
        
        def remove_in_thread():
            try:
                success, message = self.dashboard_service.remove_team_member(
                    self.selected_project['id'],
                    member['id']
                )
                Clock.schedule_once(lambda dt: self.handle_remove_result(success, message))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.handle_remove_result(False, str(e)))
        
        threading.Thread(target=remove_in_thread, daemon=True).start()
    
    def handle_remove_result(self, success, message):
        """Handle team member removal result"""
        self.show_message(message)
        if success:
            self.load_project_members()  # Refresh the list
    
    def refresh_data(self, *args):
        """Refresh all data"""
        self.load_initial_data()
    
    def show_project_dropdown(self):
        """Show the project selection dropdown"""
        try:
            print(f"Showing project dropdown, projects count: {len(self.projects) if self.projects else 0}")
            
            if not self.projects:
                self.show_message("No projects available")
                return
            
            from kivymd.uix.menu import MDDropdownMenu
            
            # Create menu items from projects
            menu_items = []
            for i, project in enumerate(self.projects):
                def make_callback(index):
                    return lambda x: self.menu_callback(index)
                from functools import partial
                menu_items.append({
                    "text": project.get('name', 'Unknown Project'),
                    "on_release": partial(self.select_project_by_index, i),
                })
            
            print(f"Created {len(menu_items)} menu items")
            
            # Create menu only once if not exists
            if not self.project_dropdown_menu:
                print("Creating new dropdown menu")
                self.project_dropdown_menu = MDDropdownMenu(
                    caller=self.ids.project_dropdown,
                    items=menu_items,
                    position="center",
                    width_mult=3,
                )
            else:
                print("Updating existing dropdown menu")
                self.project_dropdown_menu.items = menu_items
            
            print("Opening dropdown menu")
            self.project_dropdown_menu.open()
            
        except Exception as e:
            print(f"Error showing project dropdown: {e}")
            import traceback
            print(traceback.format_exc())
            self.show_message("Error loading project dropdown")
    
    def select_project(self, project):
        """Handle project selection from dropdown"""
        try:
            self.selected_project = project
            self.project_id = project.get('id')
            
            # Update dropdown text using the MDDropDownItemText
            if hasattr(self.ids, 'project_dropdown_text'):
                self.ids.project_dropdown_text.text = project.get('name', 'Unknown Project')
            
            # Close dropdown menu
            if self.project_dropdown_menu:
                self.project_dropdown_menu.dismiss()
            
            # Load members for the selected project
            self.load_project_members()
            
            # Clear current selection
            self.selected_user = None
            if hasattr(self.ids, 'email_field'):
                self.ids.email_field.text = ""
            if hasattr(self.ids, 'selected_user_label'):
                self.ids.selected_user_label.text = ""
                self.ids.selected_user_label.height = dp(0)
                
        except Exception as e:
            print(f"Error selecting project: {e}")
            import traceback
            print(traceback.format_exc())
            self.show_message("Error selecting project")
    
    def menu_callback(self, index):
        """Handle menu item selection - just print the selected item"""
        try:
            if 0 <= index < len(self.projects):
                project = self.projects[index]
                print(f"Selected project: {project.get('name', 'Unknown Project')}")
                
                # Update the dropdown text
                if hasattr(self.ids, 'project_dropdown_text') and self.ids.project_dropdown_text:
                    self.ids.project_dropdown_text.text = project.get('name', 'Unknown Project')
                
                # Close the dropdown menu
                if self.project_dropdown_menu:
                    self.project_dropdown_menu.dismiss()
                    
            else:
                print(f"Invalid index: {index}")
                
        except Exception as e:
            print(f"Error in menu callback: {e}")
            import traceback
            print(traceback.format_exc())
    
    def select_project_by_index(self, index):
        """Handle project selection by index"""
        try:
            if 0 <= index < len(self.projects):
                project = self.projects[index]
                self.select_project(project)
        except Exception as e:
            print(f"Error selecting project by index: {e}")
            import traceback
            print(traceback.format_exc())
            self.show_message("Error selecting project")
    
    def update_menu_items(self):
        """Update the dropdown menu items with current projects"""
        try:
            if not self.project_dropdown_menu:
                return
                
            menu_items = []
            for i, project in enumerate(self.projects):
                def make_callback(index):
                    return lambda x: self.select_project_by_index(index)
                
                menu_items.append({
                    "text": project.get('name', 'Unknown Project'),
                    "on_release": make_callback(i),
                })
            
            self.project_dropdown_menu.items = menu_items
            
        except Exception as e:
            print(f"Error updating menu items: {e}")
            import traceback
            print(traceback.format_exc())
    
    def open_add_member_modal(self):
        """Open the Add Member modal dialog"""
        try:
            if not self.selected_project:
                self.show_message("Please select a project first")
                return
            
            print("Opening add member modal...")
            
            # Always create a new dialog to avoid issues
            self.create_add_member_dialog()
            
            # Reset modal state
            self.selected_user_modal = None
            self.selected_role_modal = "member"
            
            # Clear the autocomplete field
            if hasattr(self, 'modal_email_field'):
                self.modal_email_field.text = ""
            
            # Update role buttons
            if hasattr(self, 'modal_role_chips'):
                print(f"Updating modal role buttons, count: {len(self.modal_role_chips)}")
                self.update_modal_role_chips()
            else:
                print("modal_role_chips not found")
            
            if self.add_member_dialog:
                print("Opening dialog...")
                self.add_member_dialog.open()
            else:
                print("Error: add_member_dialog is None after creation")
            
        except Exception as e:
            print(f"Error opening add member modal: {e}")
            import traceback
            print(traceback.format_exc())
    
    def create_add_member_dialog(self):
        """Create the Add Member modal dialog using modern KivyMD format"""
        try:
            # Build content dynamically
            content = MDDialogContentContainer(
                MDBoxLayout(
                    orientation="vertical",
                    spacing=dp(16),
                    size_hint_y=None,
                    height=dp(240),  # Increased height to ensure role buttons are visible
                    padding=dp(16)
                )
            )
            
            # Add autocomplete field
            self.modal_email_field = AutocompleteTextField(
                hint_text="Search users by name, username, or email",
                size_hint_y=None,
                height=dp(56),
                radius=[dp(8)]
            )
            self.modal_email_field.autocomplete_callback = self.search_users_modal
            content.children[0].add_widget(self.modal_email_field)
            
            # Add dropdown for search results
            self.modal_dropdown_card = MDBoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(0),
                spacing=dp(4)
            )
            content.children[0].add_widget(self.modal_dropdown_card)
            
            # Add role selection
            role_label = MDLabel(
                text="Select Role:",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(30),
                font_style="Body",
                role="medium",
                font_size="16sp",
                bold=True
            )
            content.children[0].add_widget(role_label)
            
            # Add role chips
            self.modal_role_layout = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(8),
                size_hint_y=None,
                height=dp(40)
            )
            content.children[0].add_widget(self.modal_role_layout)
            
            # Add selected user display
            self.modal_selected_user_label = MDLabel(
                text="",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(0),
                font_style="Body",
                role="small",
                font_size="14sp"
            )
            content.children[0].add_widget(self.modal_selected_user_label)
            
            # Setup role buttons first
            print("Setting up modal role buttons...")
            self.setup_modal_role_chips()
            print(f"Modal role buttons setup complete, layout children: {len(self.modal_role_layout.children)}")
            print(f"Modal role layout size: {self.modal_role_layout.size}")
            print(f"Modal role layout pos: {self.modal_role_layout.pos}")
            
            # Create modern dialog with proper structure
            # Create buttons first
            cancel_button = MDButton(
                style="outlined",
                on_release=lambda x: self.add_member_dialog.dismiss()
            )
            cancel_button.add_widget(MDButtonText(text="Cancel"))
            
            add_button = MDButton(
                style="filled",
                on_release=self.handle_add_member_from_modal
            )
            add_button.add_widget(MDButtonText(text="Add"))
            
            self.add_member_dialog = MDDialog(
                MDDialogHeadlineText(text="Add New Member"),
                MDDialogSupportingText(text="Search user, assign role and project."),
                content,
                MDDialogButtonContainer(
                    Widget(),
                    cancel_button,
                    add_button,
                    orientation="horizontal",
                    spacing="12dp",  # Add space between buttons
                    size_hint_y=None,
                    height=dp(48)
                )
            )
            
            print("Add member dialog created successfully")
            
        except Exception as e:
            print(f"Error creating add member dialog: {e}")
            import traceback
            print(traceback.format_exc())
    
    def setup_modal_role_chips(self):
        """Setup role selection buttons in the modal using modern MDButton format"""
        try:
            if not hasattr(self, 'modal_role_layout'):
                print("modal_role_layout not found")
                return
                
            roles = ["viewer", "member", "analyst", "collaborator"]
            self.modal_role_chips = {}
            
            # Clear existing buttons
            self.modal_role_layout.clear_widgets()
            
            for role in roles:
                # Create modern button with proper structure
                btn = MDButton(
                    style="outlined",
                    size_hint=(None, None),
                    width=dp(80),
                    height=dp(36),
                    on_release=lambda x, r=role: self.select_role_modal(r)
                )
                btn.add_widget(MDButtonText(text=role.title()))
                self.modal_role_chips[role] = btn
                self.modal_role_layout.add_widget(btn)
            
            # Set default selection
            self.update_modal_role_chips()
            print(f"Modal role buttons setup complete with {len(roles)} roles")
            
        except Exception as e:
            print(f"Error setting up modal role buttons: {e}")
            import traceback
            print(traceback.format_exc())
    
    def select_role_modal(self, role):
        """Handle role selection in modal"""
        try:
            self.selected_role_modal = role
            self.update_modal_role_chips()
        except Exception as e:
            print(f"Error selecting role in modal: {e}")
    
    def update_modal_role_chips(self):
        """Update role button appearance in modal"""
        try:
            if not hasattr(self, 'modal_role_chips') or not self.modal_role_chips:
                print("modal_role_chips not found or empty")
                return
                
            for role, btn in self.modal_role_chips.items():
                if btn.children:
                    text_widget = btn.children[0]
                
                if role == self.selected_role_modal:
                    btn.style = "filled"
                    text_widget.text_color = "white"  # White text for selected
                else:
                    btn.style = "outlined"
                    btn.md_bg_color = [0.8, 0.8, 0.8, 1]  # Gray for unselected
                    text_widget.text_color = "black"  # Black text for unselected
                    
            print(f"Updated modal role buttons, selected role: {self.selected_role_modal}")
            
        except Exception as e:
            print(f"Error updating modal role buttons: {e}")
            import traceback
            print(traceback.format_exc())
    
    def search_users_modal(self, query):
        """Search for users in modal"""
        if not query:
            self.hide_modal_dropdown()
            return
        
        def search_in_thread():
            try:
                users = self.dashboard_service.search_users(query)
                Clock.schedule_once(lambda dt: self.update_modal_user_dropdown(users))
            except Exception as e:
                print(f"Error searching users in modal: {e}")
                Clock.schedule_once(lambda dt: self.update_modal_user_dropdown([]))
        
        threading.Thread(target=search_in_thread, daemon=True).start()
    
    def update_modal_user_dropdown(self, users):
        """Update the user dropdown in modal"""
        try:
            # Clear existing widgets
            self.modal_dropdown_card.clear_widgets()
            
            if not users:
                self.hide_modal_dropdown()
                return
            
            # Show dropdown
            max_height = min(len(users) * dp(48), dp(200))
            self.modal_dropdown_card.height = max_height
            
            for user in users:
                user_item = MDListItem(
                    size_hint_y=None,
                    height=dp(48),
                    on_release=lambda x, u=user: self.select_user_modal(u)
                )
                user_item.add_widget(MDListItemHeadlineText(text=user['display_text']))
                self.modal_dropdown_card.add_widget(user_item)
                
        except Exception as e:
            print(f"Error updating modal user dropdown: {e}")
            import traceback
            print(traceback.format_exc())
    
    def hide_modal_dropdown(self):
        """Hide the user dropdown in modal"""
        try:
            if hasattr(self, 'modal_dropdown_card'):
                self.modal_dropdown_card.height = dp(0)
                self.modal_dropdown_card.clear_widgets()
        except Exception as e:
            print(f"Error hiding modal dropdown: {e}")
    
    def select_user_modal(self, user):
        """Handle user selection in modal"""
        try:
            self.selected_user_modal = user
            if hasattr(self, 'modal_email_field'):
                self.modal_email_field.text = user['email']
            if hasattr(self, 'modal_selected_user_label'):
                self.modal_selected_user_label.text = f"Selected: {user['display_text']}"
                self.modal_selected_user_label.height = dp(30)
            self.hide_modal_dropdown()
        except Exception as e:
            print(f"Error selecting user in modal: {e}")
    
    def handle_add_member_from_modal(self, *args):
        """Handle adding member from modal"""
        try:
            if not self.selected_project:
                self.show_message("No project selected")
                return
            
            # Get email from selected user or typed text
            email = ""
            if self.selected_user_modal:
                email = self.selected_user_modal['email']
            elif hasattr(self, 'modal_email_field') and self.modal_email_field.text.strip():
                email = self.modal_email_field.text.strip()
            
            if not email:
                self.show_message("Please search and select a user")
                return
            
            # Close modal
            if self.add_member_dialog:
                self.add_member_dialog.dismiss()
            
            # Add member using existing logic
            def invite_in_thread():
                try:
                    success, message = self.dashboard_service.invite_team_member(
                        self.selected_project['id'],
                        email,
                        self.selected_role_modal
                    )
                    Clock.schedule_once(lambda dt: self.handle_invite_result(success, message))
                except Exception as e:
                    Clock.schedule_once(lambda dt: self.handle_invite_result(False, str(e)))
            
            threading.Thread(target=invite_in_thread, daemon=True).start()
            
        except Exception as e:
            print(f"Error adding member from modal: {e}")
            import traceback
            print(traceback.format_exc())
            self.show_message("Error adding member")
    
    def show_message(self, message):
        """Show a message to the user"""
        print(f"Team Members Screen: {message}")
        # TODO: Implement proper toast/snackbar message 