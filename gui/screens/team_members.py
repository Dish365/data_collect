from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDButton
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemLeadingIcon, MDListItemTrailingIcon
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.lang import Builder
from widgets.top_bar import TopBar
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
            
        except Exception as e:
            print(f"Error in team members on_enter: {e}")
    
    def setup_ui(self, dt):
        """Setup UI components after kv file is loaded"""
        try:
            print("Setting up Team Members UI...")
            print(f"Available IDs: {list(self.ids.keys()) if hasattr(self, 'ids') else 'No IDs'}")
            
            # Check if we have the basic IDs we need
            required_ids = ['role_layout', 'email_field', 'members_list', 'project_label']
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
        self.projects = projects
        
        if not projects:
            if hasattr(self.ids, 'project_label'):
                self.ids.project_label.text = "No manageable projects found"
            return
        
        # Auto-select project if provided or use first project
        if self.project_id:
            selected_project = next((p for p in projects if p['id'] == self.project_id), None)
            if selected_project:
                self.selected_project = selected_project
            else:
                self.selected_project = projects[0]
        else:
            self.selected_project = projects[0]
        
        if hasattr(self.ids, 'project_label'):
            self.ids.project_label.text = f"Project: {self.selected_project['name']}"
        self.load_project_members()
    
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
        if not hasattr(self.ids, 'members_list'):
            return
            
        self.current_members = members
        self.ids.members_list.clear_widgets()
        
        if not members:
            empty_item = MDListItem(
                size_hint_y=None,
                height=dp(48)
            )
            empty_item.add_widget(MDListItemHeadlineText(text="No team members yet"))
            self.ids.members_list.add_widget(empty_item)
            return
        
        for member in members:
            try:
                member_item = self.create_member_item(member)
                self.ids.members_list.add_widget(member_item)
            except Exception as e:
                print(f"Error creating member item: {e}")
    
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
                    on_release=lambda x, m=member: self.remove_member(m)
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
    
    def show_message(self, message):
        """Show a message to the user"""
        print(f"Team Members Screen: {message}")
        # TODO: Implement proper toast/snackbar message 