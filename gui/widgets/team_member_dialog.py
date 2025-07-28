from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.app import App
from kivy.properties import StringProperty, DictProperty, BooleanProperty
import threading
import re

# KivyMD imports for 2.0
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import (
    MDDialog, 
    MDDialogHeadlineText, 
    MDDialogSupportingText,
    MDDialogButtonContainer
)
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemSupportingText, MDListItemLeadingIcon, MDListItemTrailingIcon
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.widget import Widget

# Load the KV file
Builder.load_file("kv/team_member_dialog.kv")

class AutocompleteTextField(MDTextField):
    """Custom text field with autocomplete functionality for KivyMD 2.0"""
    
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

class PermissionItem(MDBoxLayout):
    """Modern permission item widget"""
    permission_id = StringProperty("")
    permission_name = StringProperty("")
    permission_description = StringProperty("")
    checkbox_active = BooleanProperty(False)
    
    def on_checkbox_change(self, active):
        """Handle checkbox state change"""
        self.checkbox_active = active

class MemberListItem(MDListItem):
    """Modern member list item widget"""
    member_data = DictProperty({})
    
    def get_member_headline(self):
        """Get the headline text for the member"""
        if not self.member_data:
            return "Unknown Member"
        
        username = self.member_data.get('username', 'Unknown')
        role = self.member_data.get('role', 'member').title()
        is_creator = self.member_data.get('is_creator', False)
        
        if is_creator:
            return f"{username} (Owner)"
        return f"{username} ({role})"
    
    def get_member_supporting_text(self):
        """Get the supporting text for the member"""
        if not self.member_data:
            return "No email"
        return self.member_data.get('email', 'No email')
    
    def on_trailing_icon_press(self):
        """Handle trailing icon press (remove member)"""
        if not self.member_data.get('is_creator', False):
            # Get the parent dialog and call remove member
            parent_dialog = self.get_parent_dialog()
            if parent_dialog:
                parent_dialog.remove_member(self.member_data)
    
    def get_parent_dialog(self):
        """Get the parent team member dialog"""
        parent = self.parent
        while parent:
            if hasattr(parent, 'dashboard_service'):
                return parent
            parent = parent.parent
        return None

class TeamMemberDialogContent(MDBoxLayout):
    """Main content widget for the team member dialog"""
    
    def __init__(self, dashboard_service, project_id=None, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.dashboard_service = dashboard_service
        self.project_id = project_id
        self.callback = callback
        
        # Data
        self.projects = []
        self.current_members = []
        self.selected_project = None
        self.search_results = []
        self.selected_user = None
        self.selected_role = "member"
        self.permissions_checkboxes = {}
        
        # UI references
        self.project_menu = None
        
        # Initialize after the widget is fully loaded
        Clock.schedule_once(self.initialize_content, 0.1)
    
    def initialize_content(self, dt):
        """Initialize the content after KV is loaded"""
        try:
            # Set up autocomplete for email field
            if hasattr(self.ids, 'email_field'):
                self.ids.email_field.autocomplete_callback = self.search_users
            
            # Load initial data
            self.load_initial_data()
            
            # Set up initial role selection
            self.update_role_buttons()
            
        except Exception as e:
            print(f"Error initializing team member dialog: {e}")
    
    def open_project_menu(self):
        """Open project selection menu"""
        if not self.projects:
            self.show_toast("No projects available")
            return
            
        items = []
        for project in self.projects:
            items.append({
                "text": project['name'],
                "viewclass": "OneLineListItem",
                "on_release": lambda x=project: self.select_project(x)
            })
        
        self.project_menu = MDDropdownMenu(
            caller=self.ids.project_button,
            items=items,
            width_mult=4
        )
        self.project_menu.open()

    def select_project(self, project):
        """Select a project"""
        self.selected_project = project
        
        # Update UI
        if hasattr(self.ids, 'project_button'):
            # Update button text
            button_text = self.ids.project_button.children[0]  # MDButtonText
            button_text.text = project['name']
        
        if hasattr(self.ids, 'project_label'):
            self.ids.project_label.text = f"Project: {project['name']}"
        
        # Load project members
        self.load_project_members()
        
        # Close menu
        if self.project_menu:
            self.project_menu.dismiss()
    
    def select_role(self, role):
        """Handle role selection"""
        self.selected_role = role
        self.update_role_buttons()
        self.update_permissions_checkboxes()
    
    def update_role_buttons(self):
        """Update role button appearance based on selection"""
        roles = ["viewer", "member", "analyst", "collaborator"]
        
        for role in roles:
            btn_id = f"{role}_role_btn"
            if hasattr(self.ids, btn_id):
                btn = getattr(self.ids, btn_id)
                if role == self.selected_role:
                    btn.style = "filled"
                else:
                    btn.style = "outlined"
    
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
        self.search_results = users
        
        if not hasattr(self.ids, 'user_dropdown_list') or not hasattr(self.ids, 'user_dropdown_card'):
            return
            
        self.ids.user_dropdown_list.clear_widgets()
        
        if not users:
            self.hide_dropdown()
            return
        
        # Show dropdown
        max_height = min(len(users) * dp(48), dp(200))
        self.ids.user_dropdown_card.height = max_height
        self.ids.user_dropdown_card.opacity = 1
        
        for user in users:
            try:
                # Use modern KivyMD 2.0 list item
                user_item = MDListItem(
                    MDListItemHeadlineText(text=user['display_text']),
                    size_hint_y=None,
                    height=dp(48),
                    on_release=lambda x, u=user: self.select_user(u)
                )
                self.ids.user_dropdown_list.add_widget(user_item)
            except:
                # Fallback for compatibility
                user_item = MDListItem(
                    text=user['display_text'],
                    size_hint_y=None,
                    height=dp(48),
                    on_release=lambda x, u=user: self.select_user(u)
                )
                self.ids.user_dropdown_list.add_widget(user_item)
    
    def hide_dropdown(self):
        """Hide the user dropdown"""
        if hasattr(self.ids, 'user_dropdown_card'):
            self.ids.user_dropdown_card.height = dp(0)
            self.ids.user_dropdown_card.opacity = 0
        if hasattr(self.ids, 'user_dropdown_list'):
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
    
    def load_initial_data(self):
        """Load initial data"""
        def load_in_thread():
            try:
                projects = self.dashboard_service.get_user_projects_with_members()
                Clock.schedule_once(lambda dt: self.handle_projects_loaded(projects))
            except Exception as e:
                print(f"Error loading projects: {e}")
                Clock.schedule_once(lambda dt: self.handle_projects_loaded([]))
        
        threading.Thread(target=load_in_thread, daemon=True).start()
    
    def handle_projects_loaded(self, projects):
        """Handle projects loaded"""
        self.projects = projects
        
        if not projects:
            if hasattr(self.ids, 'project_label'):
                self.ids.project_label.text = "No manageable projects found"
            return
        
        # Auto-select project
        if self.project_id:
            selected = next((p for p in projects if p['id'] == self.project_id), None)
            if selected:
                self.selected_project = selected
            else:
                self.selected_project = projects[0]
        else:
            self.selected_project = projects[0]
        
        # Update UI
        if hasattr(self.ids, 'project_button'):
            button_text = self.ids.project_button.children[0]
            button_text.text = self.selected_project['name']
        
        if hasattr(self.ids, 'project_label'):
            self.ids.project_label.text = f"Project: {self.selected_project['name']}"
        
        self.load_project_members()
        self.load_permissions()
    
    def load_project_members(self):
        """Load current project members"""
        if not self.selected_project:
            return
        
        def load_in_thread():
            try:
                members = self.dashboard_service.get_project_members(self.selected_project['id'])
                Clock.schedule_once(lambda dt: self.update_members_list(members))
            except Exception as e:
                print(f"Error loading project members: {e}")
                Clock.schedule_once(lambda dt: self.update_members_list([]))
        
        threading.Thread(target=load_in_thread, daemon=True).start()
    
    def update_members_list(self, members):
        """Update the members list display"""
        self.current_members = members
        
        if not hasattr(self.ids, 'members_list'):
            return
            
        self.ids.members_list.clear_widgets()
        
        if not members:
            empty_label = MDLabel(
                text="No team members yet",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(40),
                halign="center"
            )
            self.ids.members_list.add_widget(empty_label)
            return
        
        for member in members:
            try:
                member_item = MemberListItem(member_data=member)
                self.ids.members_list.add_widget(member_item)
            except Exception as e:
                print(f"Error creating member item: {e}")
    
    def load_permissions(self):
        """Load available permissions"""
        try:
            if not hasattr(self.ids, 'permissions_layout'):
                return
                
            permissions_layout = self.ids.permissions_layout
            permissions_layout.clear_widgets()
            self.permissions_checkboxes = {}
            
            available_permissions = self.dashboard_service.get_team_member_permissions()
            
            for perm in available_permissions:
                perm_item = PermissionItem(
                    permission_id=perm['id'],
                    permission_name=perm['name'],
                    permission_description=perm.get('description', ''),
                )
                
                permissions_layout.add_widget(perm_item)
                self.permissions_checkboxes[perm['id']] = perm_item.ids.permission_checkbox
            
            self.update_permissions_checkboxes()
            
        except Exception as e:
            print(f"Error loading permissions: {e}")
    
    def update_permissions_checkboxes(self):
        """Update permissions checkboxes based on selected role"""
        try:
            defaults = self.dashboard_service.get_default_permissions_for_role(self.selected_role)
            for perm_id, checkbox in self.permissions_checkboxes.items():
                checkbox.active = perm_id in defaults
        except Exception as e:
            print(f"Error updating permissions: {e}")
    
    def add_member(self):
        """Add a new team member"""
        if not self.selected_project:
            self.show_toast("No project selected")
            return
        
        # Validate user selection
        email = ""
        username = ""
        if self.selected_user:
            email = self.selected_user['email']
            username = self.selected_user.get('username', email)
        elif hasattr(self.ids, 'email_field') and self.ids.email_field.text.strip():
            email = self.ids.email_field.text.strip()
            username = email.split('@')[0] if '@' in email else email
        
        if not email:
            self.show_toast("Please enter an email address or search for an existing user")
            return
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            self.show_toast("Please enter a valid email address")
            return
        
        # Collect selected permissions
        selected_permissions = [
            perm_id for perm_id, cb in self.permissions_checkboxes.items() if cb.active
        ]
        
        if not selected_permissions:
            self.show_toast("Please select at least one permission")
            return
        
        # Update UI
        if hasattr(self.ids, 'add_button'):
            self.ids.add_button.disabled = True
            button_text = self.ids.add_button.children[0]
            button_text.text = "Inviting..."
        
        def invite_in_thread():
            try:
                success, message, response_data = self.dashboard_service.invite_team_member(
                    self.selected_project['id'],
                    email,
                    self.selected_role,
                    permissions=selected_permissions
                )
                Clock.schedule_once(lambda dt: self.handle_invite_result(success, message, response_data))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.handle_invite_result(False, str(e), None))
        
        threading.Thread(target=invite_in_thread, daemon=True).start()
    
    def handle_invite_result(self, success, message, response_data=None):
        """Handle team member invite result"""
        # Re-enable the add button
        if hasattr(self.ids, 'add_button'):
            self.ids.add_button.disabled = False
            button_text = self.ids.add_button.children[0]
            button_text.text = "Add Member"
        
        if success:
            self.show_toast("Member invited successfully!")
            self.load_project_members()  # Refresh the list
            self.clear_form()
        else:
            self.show_toast(f"Failed to invite member: {message}")
    
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
        if success:
            self.show_toast("Member removed successfully!")
            self.load_project_members()  # Refresh the list
        else:
            self.show_toast(f"Failed to remove member: {message}")
    
    def clear_form(self):
        """Clear the invitation form"""
        if hasattr(self.ids, 'email_field'):
            self.ids.email_field.text = ""
        
        self.selected_user = None
        
        if hasattr(self.ids, 'selected_user_label'):
            self.ids.selected_user_label.text = ""
            self.ids.selected_user_label.height = dp(0)
        
        self.hide_dropdown()
        
        # Reset to default role and permissions
        self.selected_role = "member"
        self.update_role_buttons()
        self.update_permissions_checkboxes()
    
    def refresh_data(self):
        """Refresh all data"""
        self.load_initial_data()
    
    def close_dialog(self):
        """Close the dialog"""
        # Find the parent dialog and dismiss it
        parent = self.parent
        while parent:
            if isinstance(parent, MDDialog):
                parent.dismiss()
                break
            parent = parent.parent
        
        # Call callback if provided
        if self.callback:
            self.callback()
    
    def show_toast(self, message):
        """Show toast message with fallback"""
        try:
            from utils.cross_platform_toast import toast
            toast(message)
        except ImportError:
            try:
                from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
                
                snackbar = MDSnackbar(
                    MDSnackbarText(text=message),
                    y=dp(24),
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.8,
                )
                snackbar.open()
            except Exception:
                print(f"Toast: {message}")

class TeamMemberDialog:
    """Modern team member dialog manager"""
    
    def __init__(self, dashboard_service, project_id=None, callback=None):
        self.dashboard_service = dashboard_service
        self.project_id = project_id
        self.callback = callback
        self.dialog = None
        self.create_dialog()
    
    def create_dialog(self):
        """Create the modern team member dialog"""
        try:
            # Create content widget
            content = TeamMemberDialogContent(
                dashboard_service=self.dashboard_service,
                project_id=self.project_id,
                callback=self.callback
            )
            
            # Create dialog with KivyMD 2.0 structure
            self.dialog = MDDialog(
                MDDialogHeadlineText(
                    text="Team Management"
                ),
                MDDialogSupportingText(
                    text="Manage your project team members and permissions"
                ),
                # Use custom content for the main UI
                # The content widget handles its own close button
                size_hint=(0.9, 0.85),
            )
            
            # Add our content to the dialog
            # Note: In KivyMD 2.0, we might need to adjust this approach
            self.dialog.add_widget(content)
            
        except Exception as e:
            print(f"Error creating team member dialog: {e}")
            raise e
    
    def open(self):
        """Open the dialog"""
        try:
            if self.dialog:
                self.dialog.open()
        except Exception as e:
            print(f"Error opening dialog: {e}")
    
    def close(self):
        """Close the dialog"""
        try:
            if self.dialog:
                self.dialog.dismiss()
        except Exception as e:
            print(f"Error closing dialog: {e}")