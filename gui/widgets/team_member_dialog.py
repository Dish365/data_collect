from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import MDList, OneLineAvatarIconListItem, IconLeftWidget, IconRightWidget, OneLineListItem, TwoLineListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.app import App
import threading


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


class TeamMemberDialog:
    def __init__(self, dashboard_service, project_id=None, callback=None):
        self.dashboard_service = dashboard_service
        self.project_id = project_id
        self.callback = callback
        self.dialog = None
        self.projects = []
        self.current_members = []
        self.selected_project = None
        self.search_results = []
        self.selected_user = None
        
        # UI components
        self.project_label = None
        self.members_list = None
        self.email_field = None
        self.role_buttons = {}
        self.selected_role = "member"
        self.user_dropdown = None
        self.user_dropdown_list = None
        self.user_dropdown_card = None
        self.permissions_checkboxes = {}
        self.project_menu = None
        self.project_button = None

        self.create_dialog()
    
    def create_dialog(self):
        """Create the team member management dialog"""
        try:
            # Main content layout
            content = MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                size_hint_y=None,
                height=dp(500),  # Reduced height to fit screen better
                padding=dp(15)
            )
            
            # Title
            title_label = MDLabel(
                text="Manage Team Members",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(35),
                font_style="H6"
            )
            content.add_widget(title_label)
            
            # Project selector
            project_selector_layout = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(35)
            )
            project_selector_label = MDLabel(
                text="Project:",
                size_hint_x=0.3
            )
            self.project_button = MDFlatButton(
                text="Select Project",
                on_release=self.open_project_menu
            )
            project_selector_layout.add_widget(project_selector_label)
            project_selector_layout.add_widget(self.project_button)
            content.add_widget(project_selector_layout)

            # Project info
            self.project_label = MDLabel(
                text="Loading projects...",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(25)
            )
            content.add_widget(self.project_label)
            
            # Current members section
            members_section_label = MDLabel(
                text="Current Team Members",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(25),
                font_style="Subtitle1"
            )
            content.add_widget(members_section_label)
            
            # Members list in scrollable container
            members_scroll = ScrollView(
                size_hint=(1, None),
                height=dp(100)  # Further reduced height
            )
            
            self.members_list = MDList()
            members_scroll.add_widget(self.members_list)
            content.add_widget(members_scroll)
            
            # Add member section
            add_section_label = MDLabel(
                text="Invite Team Member",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(25),
                font_style="Subtitle1"
            )
            content.add_widget(add_section_label)
            
            # User search with autocomplete
            user_search_layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(5),
                size_hint_y=None,
                adaptive_height=True
            )
            
            # Autocomplete text field
            self.email_field = AutocompleteTextField(
                hint_text="Search users by name, username, or email",
                helper_text="Start typing to search existing users, or enter any email to invite new users",
                helper_text_mode="on_focus",
                size_hint_y=None,
                height=dp(56),
                autocomplete_callback=self.search_users
            )
            user_search_layout.add_widget(self.email_field)
            
            # Dropdown card for search results (initially hidden)
            self.user_dropdown_card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(0),  # Initially hidden
                elevation=3,
                radius=[5],
                md_bg_color=[1, 1, 1, 1]
            )
            
            dropdown_scroll = ScrollView(
                size_hint=(1, 1)
            )
            
            self.user_dropdown_list = MDList()
            dropdown_scroll.add_widget(self.user_dropdown_list)
            self.user_dropdown_card.add_widget(dropdown_scroll)
            
            user_search_layout.add_widget(self.user_dropdown_card)
            content.add_widget(user_search_layout)
            
            # Selected user display
            self.selected_user_label = MDLabel(
                text="",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(0),  # Initially hidden
                font_style="Body2"
            )
            content.add_widget(self.selected_user_label)
            
            # Role selection with buttons
            role_label = MDLabel(
                text="Role:",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(25)
            )
            content.add_widget(role_label)
            
            role_layout = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(5),
                size_hint_y=None,
                height=dp(40),
                adaptive_height=True
            )
            
            # Role buttons
            roles = ["viewer", "member", "analyst", "collaborator"]
            for role in roles:
                btn = MDFlatButton(
                    text=role.title(),
                    size_hint_x=None,
                    width=dp(75),  # Slightly smaller buttons
                    on_release=lambda x, r=role: self.select_role(r)
                )
                self.role_buttons[role] = btn
                role_layout.add_widget(btn)
            
            # Set default selected role
            self.update_role_buttons()
            content.add_widget(role_layout)

            # Permissions section
            permissions_label = MDLabel(
                text="Permissions:",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(25)
            )
            content.add_widget(permissions_label)

            permissions_scroll = ScrollView(
                size_hint_y=None,
                height=dp(120)  # Reduced permissions section height
            )
            permissions_layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(5),
                adaptive_height=True
            )

            available_permissions = self.dashboard_service.get_team_member_permissions()
            for perm in available_permissions:
                perm_box = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(35)  # Reduced height for permission items
                )
                checkbox = MDCheckbox(
                    size_hint_x=None,
                    width=dp(40)
                )
                label = MDLabel(text=perm['name'])
                perm_box.add_widget(checkbox)
                perm_box.add_widget(label)
                permissions_layout.add_widget(perm_box)
                self.permissions_checkboxes[perm['id']] = checkbox

            permissions_scroll.add_widget(permissions_layout)
            content.add_widget(permissions_scroll)
            
            # Action buttons
            button_layout = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(10),
                size_hint_y=None,
                height=dp(45)
            )
            
            self.add_button = MDRaisedButton(
                text="Add Member",
                size_hint_x=None,
                width=dp(120),
                on_release=self.add_member
            )
            button_layout.add_widget(self.add_button)
            
            refresh_button = MDFlatButton(
                text="Refresh",
                size_hint_x=None,
                width=dp(100),
                on_release=self.refresh_data
            )
            button_layout.add_widget(refresh_button)
            
            content.add_widget(button_layout)
            
            # Create dialog
            self.dialog = MDDialog(
                title="Team Members",
                type="custom",
                content_cls=content,
                size_hint=(0.85, 0.8),  # Reduced size to fit screen better
                buttons=[
                    MDFlatButton(
                        text="CLOSE",
                        on_release=self.close_dialog
                    )
                ]
            )
            
            # Load initial data
            self.load_initial_data()
            
        except Exception as e:
            print(f"Error creating team member dialog: {e}")
            raise e
    
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
        self.user_dropdown_list.clear_widgets()
        
        if not users:
            self.hide_dropdown()
            return
        
        # Show dropdown
        max_height = min(len(users) * dp(48), dp(200))  # Max 200dp height
        self.user_dropdown_card.height = max_height
        
        for user in users:
            user_item = OneLineListItem(
                text=user['display_text'],
                on_release=lambda x, u=user: self.select_user(u)
            )
            self.user_dropdown_list.add_widget(user_item)
    
    def hide_dropdown(self):
        """Hide the user dropdown"""
        self.user_dropdown_card.height = dp(0)
        self.user_dropdown_list.clear_widgets()
    
    def select_user(self, user):
        """Handle user selection from dropdown"""
        self.selected_user = user
        self.email_field.text = user['email']
        self.selected_user_label.text = f"Selected: {user['display_text']}"
        self.selected_user_label.height = dp(30)
        self.hide_dropdown()
    
    def select_role(self, role):
        """Handle role selection"""
        self.selected_role = role
        self.update_role_buttons()
        self.update_permissions_checkboxes()
    
    def update_role_buttons(self):
        """Update role button appearance"""
        for role, btn in self.role_buttons.items():
            if role == self.selected_role:
                btn.md_bg_color = [0.2, 0.6, 1, 1]  # Blue for selected
            else:
                btn.md_bg_color = [0.5, 0.5, 0.5, 0.3]  # Gray for unselected
    
    def update_permissions_checkboxes(self):
        """Update permissions checkboxes based on selected role"""
        defaults = self.dashboard_service.get_default_permissions_for_role(self.selected_role)
        for perm_id, checkbox in self.permissions_checkboxes.items():
            checkbox.active = perm_id in defaults

    def open_project_menu(self, *args):
        """Open project selection menu"""
        items = [
            {
                "text": p['name'],
                "viewclass": "OneLineListItem",
                "on_release": lambda x=p: self.select_project(x)
            } for p in self.projects
        ]
        self.project_menu = MDDropdownMenu(
            caller=self.project_button,
            items=items,
            width_mult=4
        )
        self.project_menu.open()

    def select_project(self, project):
        """Select a project"""
        self.selected_project = project
        self.project_button.text = project['name']
        self.project_label.text = f"Project: {project['name']}"
        self.load_project_members()
        if self.project_menu:
            self.project_menu.dismiss()
    
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
            if self.project_label:
                self.project_label.text = "No manageable projects found"
            return
        
        # Auto-select project if provided or use first project
        if self.project_id:
            selected = next((p for p in projects if p['id'] == self.project_id), None)
            if selected:
                self.selected_project = selected
            else:
                self.selected_project = projects[0]
        else:
            self.selected_project = projects[0]
        
        self.project_button.text = self.selected_project['name']
        self.project_label.text = f"Project: {self.selected_project['name']}"
        self.load_project_members()
        self.update_permissions_checkboxes()  # Initial update
    
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
        if self.members_list:
            self.members_list.clear_widgets()
        
        if not members:
            empty_label = MDLabel(
                text="No team members yet",
                theme_text_color="Hint",
                size_hint_y=None,
                height=dp(40),
                halign="center"
            )
            if self.members_list:
                self.members_list.add_widget(empty_label)
            return
        
        for member in members:
            try:
                member_item = self.create_member_item(member)
                if self.members_list:
                    self.members_list.add_widget(member_item)
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
            
            item = OneLineAvatarIconListItem(
                text=item_text,
                size_hint_y=None,
                height=dp(48)
            )
            
            # Add user icon
            item.add_widget(IconLeftWidget(
                icon="account",
                theme_icon_color="Primary"
            ))
            
            # Add remove button (only if not creator)
            if not is_creator:
                remove_btn = IconRightWidget(
                    icon="delete",
                    theme_icon_color="Error"
                )
                remove_btn.bind(on_release=lambda x, m=member: self.remove_member(m))
                item.add_widget(remove_btn)
            
            return item
            
        except Exception as e:
            print(f"Error creating member item widget: {e}")
            # Return a simple fallback item
            return OneLineAvatarIconListItem(
                text="Error loading member",
                size_hint_y=None,
                height=dp(48)
            )
    
    def add_member(self, *args):
        """Add a new team member"""
        if not self.selected_project:
            self.show_error_message("No project selected")
            return
        
        # Validate user selection
        email = ""
        username = ""
        if self.selected_user:
            email = self.selected_user['email']
            username = self.selected_user.get('username', email)
        elif self.email_field and self.email_field.text.strip():
            email = self.email_field.text.strip()
            username = email.split('@')[0] if '@' in email else email  # Use email prefix as display name
        
        if not email:
            self.show_error_message("Please enter an email address or search for an existing user")
            return
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            self.show_error_message("Please enter a valid email address")
            return
        
        # Note: Backend will check if user is already a member or has pending invitation
        
        # Collect selected permissions
        selected_permissions = [
            perm_id for perm_id, cb in self.permissions_checkboxes.items() if cb.active
        ]
        
        if not selected_permissions:
            self.show_error_message("Please select at least one permission")
            return
        
        # Disable the button to prevent double-clicks
        self.add_button.disabled = True
        self.add_button.text = "Inviting..."
        
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
    
    def is_user_already_member(self, email):
        """Check if user is already a team member"""
        for member in self.current_members:
            if member.get('email') == email:
                return True
        return False
    
    def handle_invite_result(self, success, message, response_data=None):
        """Handle team member invite result"""
        # Re-enable the add button
        self.add_button.disabled = False
        self.add_button.text = "Add Member"
        
        if success:
            # Check invitation type for different handling
            invitation_type = response_data.get('invitation_type', 'unknown') if response_data else 'unknown'
            
            if invitation_type == 'existing_user':
                self.show_success_message(message)
                self.load_project_members()  # Refresh the list immediately
            elif invitation_type == 'pending':
                self.show_pending_invitation_message(message, response_data)
            else:
                self.show_success_message(message)
                self.load_project_members()  # Refresh as fallback
            
            # Clear the form
            self.clear_form()
            
        else:
            # Handle specific error cases
            if "pending invitation has already been sent" in message.lower():
                email = self.get_current_email()
                self.show_pending_invitation_exists_dialog(message, email)
            else:
                self.show_error_message(f"Failed to invite member: {message}")
    
    def clear_form(self):
        """Clear the invitation form"""
        if self.email_field:
            self.email_field.text = ""
        self.selected_user = None
        self.selected_user_label.text = ""
        self.selected_user_label.height = dp(0)
        self.hide_dropdown()
        # Reset to default role and permissions
        self.selected_role = "member"
        self.update_role_buttons()
        self.update_permissions_checkboxes()
    
    def show_success_message(self, message):
        """Show a success message to the user"""
        print(f"SUCCESS: {message}")
        # TODO: Show a proper success toast/snackbar
        
    def show_error_message(self, message):
        """Show an error message to the user"""
        print(f"ERROR: {message}")
        # TODO: Show a proper error toast/snackbar
    
    def show_pending_invitation_message(self, message, response_data):
        """Show a message for pending invitations"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.label import MDLabel
        from kivymd.uix.boxlayout import MDBoxLayout
        
        invitation = response_data.get('invitation', {})
        email = invitation.get('email', 'Unknown')
        role = invitation.get('role', 'member').title()
        expires_at = invitation.get('expires_at', 'Unknown')
        
        # Create dialog content
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(200),
            padding=dp(16)
        )
        
        title_label = MDLabel(
            text="Invitation Details",
            font_style="H6",
            size_hint_y=None,
            height=dp(40),
            theme_text_color="Primary"
        )
        
        message_label = MDLabel(
            text=f"An invitation has been sent to:\n\n{email}\nRole: {role}\nExpires: {expires_at[:10] if expires_at != 'Unknown' else 'Unknown'}",
            size_hint_y=None,
            height=dp(120),
            theme_text_color="Secondary",
            halign="left"
        )
        
        note_label = MDLabel(
            text="The user will receive an email with instructions to create an account and join your project.",
            size_hint_y=None,
            height=dp(40),
            theme_text_color="Hint",
            halign="left",
            font_style="Caption"
        )
        
        content.add_widget(title_label)
        content.add_widget(message_label)
        content.add_widget(note_label)
        
        dialog = MDDialog(
            title="Invitation Sent",
            type="custom",
            content_cls=content,
            size_hint=(0.8, None),
            height=dp(350),
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
        
        print(f"PENDING INVITATION: {message}")
        print(f"Invitation details: {invitation}")
    
    def get_current_email(self):
        """Get the current email from form state"""
        if self.selected_user:
            return self.selected_user['email']
        elif self.email_field and self.email_field.text.strip():
            return self.email_field.text.strip()
        return "unknown user"
    
    def show_pending_invitation_exists_dialog(self, message, email):
        """Show dialog when a pending invitation already exists"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton, MDRaisedButton
        from kivymd.uix.label import MDLabel
        from kivymd.uix.boxlayout import MDBoxLayout
        
        # Create dialog content
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(15),
            size_hint_y=None,
            height=dp(180),
            padding=dp(16)
        )
        
        title_label = MDLabel(
            text="Invitation Already Sent",
            font_style="H6",
            size_hint_y=None,
            height=dp(40),
            theme_text_color="Primary"
        )
        
        message_label = MDLabel(
            text=f"A pending invitation has already been sent to {email}.\n\nThey may not have registered yet or the invitation may still be pending acceptance.",
            size_hint_y=None,
            height=dp(80),
            theme_text_color="Secondary",
            halign="left"
        )
        
        note_label = MDLabel(
            text="You can wait for them to accept the existing invitation, or contact them directly.",
            size_hint_y=None,
            height=dp(60),
            theme_text_color="Hint",
            halign="left",
            font_style="Caption"
        )
        
        content.add_widget(title_label)
        content.add_widget(message_label)
        content.add_widget(note_label)
        
        dialog = MDDialog(
            title="Duplicate Invitation",
            type="custom",
            content_cls=content,
            size_hint=(0.8, None),
            height=dp(400),
            buttons=[
                MDFlatButton(
                    text="VIEW PENDING INVITATIONS",
                    on_release=lambda x: self.show_pending_invitations_info(dialog)
                ),
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
        
        print(f"DUPLICATE INVITATION: {email} already has a pending invitation")
    
    def show_pending_invitations_info(self, parent_dialog):
        """Show information about pending invitations for this project"""
        parent_dialog.dismiss()
        
        # For now, just show a simple message
        # In a full implementation, you'd fetch and display all pending invitations
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.label import MDLabel
        from kivymd.uix.boxlayout import MDBoxLayout
        
        content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(150),
            padding=dp(16)
        )
        
        info_label = MDLabel(
            text="Pending invitations are automatically managed by the system.\n\nInvitations expire after 7 days if not accepted.\n\nYou can contact users directly if they haven't received their invitation email.",
            size_hint_y=None,
            height=dp(150),
            theme_text_color="Secondary",
            halign="left"
        )
        
        content.add_widget(info_label)
        
        info_dialog = MDDialog(
            title="Pending Invitations Info",
            type="custom",
            content_cls=content,
            size_hint=(0.8, None),
            height=dp(300),
            buttons=[
                MDFlatButton(
                    text="CLOSE",
                    on_release=lambda x: info_dialog.dismiss()
                )
            ]
        )
        info_dialog.open()
    
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
        print(f"Team Member Dialog: {message}")
    
    def open(self):
        """Open the dialog"""
        try:
            if self.dialog:
                self.dialog.open()
        except Exception as e:
            print(f"Error opening dialog: {e}")
    
    def close_dialog(self, *args):
        """Close the dialog"""
        try:
            if self.dialog:
                self.dialog.dismiss()
            
            # Call callback if provided
            if self.callback:
                self.callback()
        except Exception as e:
            print(f"Error closing dialog: {e}") 