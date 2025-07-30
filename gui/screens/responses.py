from kivy.lang import Builder
from kivy.clock import Clock
from kivy.app import App
from kivy.metrics import dp
from utils.cross_platform_toast import toast
from kivymd.uix.screen import MDScreen
from kivymd.uix.responsivelayout import MDResponsiveLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox

import threading
from datetime import datetime

Builder.load_file("kv/responses.kv")


class ResponseDetailDialog(MDDialog):
    """Dialog for showing detailed responses"""
    def __init__(self, respondent_data, **kwargs):
        self.respondent_data = respondent_data
        super().__init__(
            title=f"Responses from {respondent_data.get('display_name', 'Unknown')}",
            type="custom",
            content_cls=self.create_content(),
            size_hint=(0.9, 0.8)
        )
    
    def create_content(self):
        """Create dialog content using KV-defined component"""
        from kivy.lang import Builder
        content = Builder.load_string('ResponseDetailContent:')
        content.update_content(self.respondent_data)
        return content

class ResponseDetailContent(MDCard):
    """Content for response detail dialog"""
    def update_content(self, respondent_data):
        """Update content with respondent data"""
        self.ids.project_info_label.text = f"Project: {respondent_data.get('project_name', 'Unknown')}"
        
        responses = respondent_data.get('responses', [])
        if not responses:
            self.ids.responses_layout.clear_widgets()
            no_responses = Builder.load_string('NoResponsesLabel:')
            self.ids.responses_layout.add_widget(no_responses)
        else:
            for i, response in enumerate(responses):
                response_card = Builder.load_string('ResponseCard:')
                response_card.ids.question_label.text = f"Q{i+1}: {response.get('question_text', 'Unknown Question')}"
                response_card.ids.answer_label.text = f"Answer: {response.get('response_value', 'No answer')}"
                response_card.ids.time_label.text = f"Collected: {response.get('collected_at_formatted', 'Unknown time')}"
                self.ids.responses_layout.add_widget(response_card)


class ResponseItem(MDCard):
    """Widget for displaying a single respondent row in the table"""
    def __init__(self, respondent_data, on_view_responses=None, on_edit_respondent=None, on_delete_respondent=None, on_selection_changed=None, **kwargs):
        super().__init__(**kwargs)
        self.respondent_data = respondent_data
        self.on_view_responses = on_view_responses
        self.on_edit_respondent = on_edit_respondent
        self.on_delete_respondent = on_delete_respondent
        self.on_selection_changed = on_selection_changed
        self.is_selected = False
        
        # Update the UI with respondent data
        self.update_content()
    
    def update_content(self):
        """Update the item content with respondent data"""
        # Safe value extraction with defaults
        respondent_id = self.respondent_data.get('respondent_id') or 'Unknown'
        display_name = self.respondent_data.get('display_name') or 'Anonymous'
        project_name = self.respondent_data.get('project_name') or 'Unknown Project'
        
        # Update labels
        if hasattr(self.ids, 'respondent_id_label'):
            respondent_id_text = respondent_id[-12:] if len(respondent_id) > 12 else respondent_id
            self.ids.respondent_id_label.text = respondent_id_text
        
        if hasattr(self.ids, 'name_label'):
            self.ids.name_label.text = display_name
        
        if hasattr(self.ids, 'project_label'):
            self.ids.project_label.text = project_name
    
    def on_checkbox_active(self, checkbox, value):
        """Handle selection checkbox change"""
        self.is_selected = value
        if self.on_selection_changed:
            self.on_selection_changed(self.respondent_data, value)
    
    def set_selected(self, selected):
        """Set selection state programmatically"""
        self.is_selected = selected
        if hasattr(self.ids, 'selection_checkbox'):
            self.ids.selection_checkbox.active = selected
    
    def set_selected(self, selected):
        """Set selection state programmatically"""
        self.is_selected = selected
        self.selection_checkbox.active = selected
    
    def view_responses(self, instance):
        """Handle view responses button click"""
        if self.on_view_responses:
            self.on_view_responses(self.respondent_data)

    def edit_respondent(self, instance):
        """Handle edit respondent button click"""
        if self.on_edit_respondent:
            self.on_edit_respondent(self.respondent_data)

    def delete_respondent(self, instance):
        """Handle delete respondent button click"""
        if self.on_delete_respondent:
            self.on_delete_respondent(self.respondent_data)


class ResponsesScreen(MDScreen, MDResponsiveLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.configure_responsive_layout()
        
        app = App.get_running_app()
        self.auth_service = app.auth_service
        self.db_service = app.db_service
        from services.responses_service import ResponsesService
        self.responses_service = ResponsesService(
            app.auth_service, 
            app.db_service, 
            app.data_collection_service
        )
        self.respondents_data = []
        self.is_loading = False
        self.current_offset = 0
        self.page_limit = 20
        self.detail_dialog = None
        self.selected_respondents = set()
        self.current_detail_respondent = None
    
    def configure_responsive_layout(self):
        """Configure responsive layout breakpoints"""
        self.adaptive_size = True
        self.adaptive_height = True
        self.adaptive_width = True
        self.mobile_view = True
        self.tablet_view = False
        self.desktop_view = False
    
    def update_responsive_layout(self):
        """Update responsive layout - alias for configure_responsive_layout"""
        self.configure_responsive_layout()

    def on_enter(self):
        """Called when screen is entered"""
        self.ids.top_bar.set_title("Responses")
        self.ids.top_bar.set_current_screen("responses")
        
        # Initialize responsive layout
        self.update_responsive_layout()
        
        self.load_respondents()

    def on_resize(self, *args):
        """Handle window resize for responsive layout"""
        width = self.width
        height = self.height
        
        # Update view based on screen size
        if width >= 1200:  # Desktop breakpoint
            self.mobile_view = False
            self.tablet_view = False
            self.desktop_view = True
        elif width >= 800:  # Tablet breakpoint
            self.mobile_view = False
            self.tablet_view = True
            self.desktop_view = False
        else:  # Mobile
            self.mobile_view = True
            self.tablet_view = False
            self.desktop_view = False
    
    def on_select_all(self, active):
        """Handle select all checkbox"""
        for child in self.ids.responses_grid.children:
            if isinstance(child, ResponseItem):
                child.set_selected(active)
        
        # Update selected set
        if active:
            self.selected_respondents = {item.respondent_data['id'] for item in self.ids.responses_grid.children if isinstance(item, ResponseItem)}
        else:
            self.selected_respondents.clear()
        
        self.update_selection_ui()
    
    def on_item_selection_changed(self, respondent_data, selected):
        """Handle individual item selection change"""
        respondent_id = respondent_data.get('id')
        
        if selected:
            self.selected_respondents.add(respondent_id)
        else:
            self.selected_respondents.discard(respondent_id)
        
        self.update_selection_ui()
        
        # Update select all checkbox
        total_items = len([child for child in self.ids.responses_grid.children if isinstance(child, ResponseItem)])
        if hasattr(self.ids, 'select_all_checkbox'):
            if len(self.selected_respondents) == total_items and total_items > 0:
                self.ids.select_all_checkbox.active = True
            else:
                self.ids.select_all_checkbox.active = False
    
    def update_selection_ui(self):
        """Update selection-related UI elements"""
        count = len(self.selected_respondents)
        
        # Update selection count label
        if hasattr(self.ids, 'selection_count_label'):
            self.ids.selection_count_label.text = f"{count} selected"
        
        # Enable/disable bulk action buttons
        has_selection = count > 0
        
        # Enable bulk action buttons based on selection
        if hasattr(self.ids, 'bulk_actions_toolbar'):
            for child in self.ids.bulk_actions_toolbar.children:
                if isinstance(child, MDButton):
                    child.disabled = not has_selection

    def show_loader(self, show=True):
        """Show/hide loading spinner"""
        if hasattr(self.ids, 'spinner'):
            self.ids.spinner.active = show
        if hasattr(self.ids, 'content_layout'):
            self.ids.content_layout.opacity = 0.3 if show else 1
            self.ids.content_layout.disabled = show



    def search_respondents(self, query):
        """Search respondents by query"""
        self.current_offset = 0
        self.respondents_data = []
        self.ids.responses_grid.clear_widgets()
        self.load_respondents(search_query=query)

    def load_respondents(self, search_query=None, load_more=False):
        """Load respondents data"""
        if self.is_loading:
            return
        
        self.is_loading = True
        if not load_more:
            self.show_loader(True)
            
        def _load_in_thread():
            try:
                respondents, error = self.responses_service.get_all_respondents_with_responses(
                    search_query=search_query,
                    limit=self.page_limit,
                    offset=self.current_offset
                )
                
                if error:
                    raise Exception(error)
                
                if not load_more:
                    self.respondents_data = respondents
                else:
                    self.respondents_data.extend(respondents)
                    
                self.current_offset += len(respondents)
                
                Clock.schedule_once(lambda dt: self._update_respondents_ui(respondents, len(respondents) < self.page_limit))
                
            except Exception as e:
                print(f"Error loading respondents: {e}")
                Clock.schedule_once(lambda dt: toast(f"Error loading data: {str(e)}"))
            finally:
                self.is_loading = False
                Clock.schedule_once(lambda dt: self.show_loader(False))
        
        threading.Thread(target=_load_in_thread, daemon=True).start()

    def _update_respondents_ui(self, new_respondents, is_last_page):
        """Update the UI with respondents data"""
        try:
            # Remove existing load more button if present
            if hasattr(self.ids, 'load_more_button') and self.ids.load_more_button.parent:
                self.ids.content_layout.remove_widget(self.ids.load_more_button)
            
            # Clear grid if this is a fresh load
            if self.current_offset <= len(new_respondents):
                self.ids.responses_grid.clear_widgets()
                self.selected_respondents.clear()  # Clear selections on fresh load
                self.update_selection_ui()
            
            # Add new respondent items with tablet optimization
            for respondent in new_respondents:
                item = ResponseItem(
                    respondent_data=respondent,
                    on_view_responses=self.view_respondent_responses,
                    on_edit_respondent=self.edit_respondent,
                    on_delete_respondent=self.delete_respondent,
                    on_selection_changed=self.on_item_selection_changed  # New callback
                )
                self.ids.responses_grid.add_widget(item)
            
            # Add load more button if not last page - tablet optimized
            if not is_last_page and len(new_respondents) >= self.page_limit:
                load_more_btn = self.create_tablet_optimized_load_more_button()
                load_more_btn.id = 'load_more_button'
                self.ids.load_more_button = load_more_btn
                # Find the master panel and add to it instead of content_layout
                if hasattr(self.ids, 'master_panel'):
                    self.ids.master_panel.add_widget(load_more_btn)
                else:
                    self.ids.content_layout.add_widget(load_more_btn)
            
            # Show no data message if empty
            if not self.respondents_data:
                no_data_label = self.create_tablet_optimized_no_data_label()
                self.ids.responses_grid.add_widget(no_data_label)
                
        except Exception as e:
            print(f"Error updating UI: {e}")
    
    def create_tablet_optimized_load_more_button(self):
        """Create a load more button using KV-defined component"""
        from kivy.lang import Builder
        
        button = Builder.load_string('LoadMoreButton:')
        button.load_more = lambda: self.load_respondents(load_more=True)
        
        return button
    
    def create_tablet_optimized_no_data_label(self):
        """Create a no data label using KV-defined component"""
        from kivy.lang import Builder
        
        return Builder.load_string('NoDataLabel:')
    
    def view_respondent_responses(self, respondent_data):
        """Show detailed responses for a respondent based on screen size"""
        if self.tablet_view or self.desktop_view:
            self.show_detail_in_side_panel(respondent_data)
        else:
            self.show_detail_in_dialog(respondent_data)
    
    def show_detail_in_side_panel(self, respondent_data):
        """Show respondent details in the side panel (tablet mode)"""
        self.current_detail_respondent = respondent_data
        self.show_loader(True)
        
        def _load_details():
            try:
                detailed_data, error = self.responses_service.get_respondent_detail_with_responses(
                    respondent_data['respondent_id']
                )
                
                if error:
                    raise Exception(error)
                
                Clock.schedule_once(lambda dt: self._update_detail_panel(detailed_data))
                
            except Exception as e:
                print(f"Error loading respondent details: {e}")
                Clock.schedule_once(lambda dt: toast(f"Error loading details: {str(e)}"))
            finally:
                Clock.schedule_once(lambda dt: self.show_loader(False))
        
        threading.Thread(target=_load_details, daemon=True).start()
    
    def show_detail_in_dialog(self, respondent_data):
        """Show respondent details in a dialog (mobile mode)"""
        self.show_loader(True)
        
        def _load_details():
            try:
                detailed_data, error = self.responses_service.get_respondent_detail_with_responses(
                    respondent_data['respondent_id']
                )
                
                if error:
                    raise Exception(error)
                
                Clock.schedule_once(lambda dt: self._show_response_dialog(detailed_data))
                
            except Exception as e:
                print(f"Error loading respondent details: {e}")
                Clock.schedule_once(lambda dt: toast(f"Error loading details: {str(e)}"))
            finally:
                Clock.schedule_once(lambda dt: self.show_loader(False))
        
        threading.Thread(target=_load_details, daemon=True).start()
    
    def _update_detail_panel(self, respondent_data):
        """Update the detail panel with respondent data"""
        try:
            if not hasattr(self.ids, 'detail_content'):
                return
                
            content = self.ids.detail_content
            content.clear_widgets()
            
            # Header with respondent info
            header_card = MDCard(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(8),
                size_hint_y=None,
                height=dp(100),
                elevation=1
            )
            
            name_label = MDLabel(
                text=f"Respondent: {respondent_data.get('display_name', 'Unknown')}",
                font_style="H6",
                font_size="18sp",
                size_hint_y=None,
                height=dp(30)
            )
            
            project_label = MDLabel(
                text=f"Project: {respondent_data.get('project_name', 'Unknown')}",
                font_style="Subtitle1",
                font_size="16sp",
                size_hint_y=None,
                height=dp(25)
            )
            
            id_label = MDLabel(
                text=f"ID: {respondent_data.get('respondent_id', 'Unknown')}",
                font_style="Body2",
                font_size="14sp",
                size_hint_y=None,
                height=dp(25)
            )
            
            header_card.add_widget(name_label)
            header_card.add_widget(project_label)
            header_card.add_widget(id_label)
            content.add_widget(header_card)
            
            # Responses
            responses = respondent_data.get('responses', [])
            if not responses:
                no_responses = MDLabel(
                    text="No responses found for this respondent",
                    halign="center",
                    font_size="16sp",
                    size_hint_y=None,
                    height=dp(40)
                )
                content.add_widget(no_responses)
            else:
                for i, response in enumerate(responses):
                    response_card = self.create_response_card(response, i+1)
                    content.add_widget(response_card)
                    
        except Exception as e:
            print(f"Error updating detail panel: {e}")
    
    def create_response_card(self, response, question_number):
        """Create response card using KV-defined component"""
        from kivy.lang import Builder
        
        card = Builder.load_string('ResponseCard:')
        
        # Set the data
        card.ids.question_label.text = f"Q{question_number}: {response.get('question_text', 'Unknown Question')}"
        card.ids.answer_label.text = f"Answer: {response.get('response_value', 'No answer')}"
        card.ids.time_label.text = f"Collected: {response.get('collected_at_formatted', 'Unknown time')}"
        
        return card

    def _show_response_dialog(self, respondent_data):
        """Show the response detail dialog"""
        try:
            content = ResponseDetailDialog(respondent_data)
            
            # Create dialog using KV-defined component
            from kivy.lang import Builder
            
            self.detail_dialog = Builder.load_string('ResponseDetailDialog:')
            self.detail_dialog.content_cls = content
            self.detail_dialog.open()
            
        except Exception as e:
            print(f"Error showing dialog: {e}")
            toast("Error displaying response details")

    def refresh_data(self):
        """Refresh all data"""
        self.current_offset = 0
        self.respondents_data = []
        self.ids.responses_grid.clear_widgets()
        self.load_summary_stats()
        self.load_respondents()

    def go_back_to_dashboard(self):
        """Navigate back to dashboard"""
        self.manager.transition.direction = "right"
        self.manager.current = "dashboard"

    def edit_respondent(self, respondent_data):
        """Show edit dialog for respondent"""
        try:
            # Create edit dialog using KV-defined component
            from kivy.lang import Builder
            
            self.edit_dialog = Builder.load_string('EditRespondentDialog:')
            
            # Set initial values
            self.edit_dialog.ids.title_label.text = f"Edit Respondent: {respondent_data.get('respondent_id', 'Unknown')}"
            self.edit_dialog.ids.name_field.text = respondent_data.get('name', '')
            self.edit_dialog.ids.email_field.text = respondent_data.get('email', '')
            self.edit_dialog.ids.phone_field.text = respondent_data.get('phone', '')
            self.edit_dialog.ids.anonymous_checkbox.active = respondent_data.get('is_anonymous', True)
            
            # Set save callback
            def save_changes():
                updated_data = {
                    'name': self.edit_dialog.ids.name_field.text.strip() if self.edit_dialog.ids.name_field.text.strip() else None,
                    'email': self.edit_dialog.ids.email_field.text.strip() if self.edit_dialog.ids.email_field.text.strip() else None,
                    'phone': self.edit_dialog.ids.phone_field.text.strip() if self.edit_dialog.ids.phone_field.text.strip() else None,
                    'is_anonymous': self.edit_dialog.ids.anonymous_checkbox.active
                }
                self._update_respondent(respondent_data['id'], updated_data)
                self.edit_dialog.dismiss()
            
            self.edit_dialog.save_changes = save_changes
            self.edit_dialog.open()
            
        except Exception as e:
            print(f"Error showing edit dialog: {e}")
            toast("Error opening edit dialog")

    def delete_respondent(self, respondent_data):
        """Show delete confirmation dialog"""
        try:
            # Create delete dialog using KV-defined component
            from kivy.lang import Builder
            
            self.delete_dialog = Builder.load_string('DeleteConfirmDialog:')
            
            # Set confirmation text
            self.delete_dialog.ids.confirm_text.text = f"Are you sure you want to delete respondent '{respondent_data.get('display_name', 'Unknown')}'?\n\nThis will also delete all their responses and cannot be undone."
            
            # Set confirm callback
            def confirm_delete():
                self._delete_respondent(respondent_data['id'])
                self.delete_dialog.dismiss()
            
            self.delete_dialog.confirm_delete = confirm_delete
            self.delete_dialog.open()
            
        except Exception as e:
            print(f"Error showing delete dialog: {e}")
            toast("Error opening delete dialog")

    def _update_respondent(self, respondent_id, updated_data):
        """Update respondent via API"""
        self.show_loader(True)
        
        def _update_in_thread():
            try:
                result, error = self.responses_service.update_respondent(respondent_id, updated_data)
                
                if error:
                    Clock.schedule_once(lambda dt: toast(f"Update failed: {error}"))
                else:
                    Clock.schedule_once(lambda dt: toast("Respondent updated successfully"))
                    Clock.schedule_once(lambda dt: self.refresh_data())
                    
            except Exception as e:
                print(f"Error updating respondent: {e}")
                Clock.schedule_once(lambda dt: toast(f"Update error: {str(e)}"))
            finally:
                Clock.schedule_once(lambda dt: self.show_loader(False))
        
        threading.Thread(target=_update_in_thread, daemon=True).start()

    def _delete_respondent(self, respondent_id):
        """Delete respondent via API"""
        self.show_loader(True)
        
        def _delete_in_thread():
            try:
                success, error = self.responses_service.delete_respondent(respondent_id)
                
                if error:
                    Clock.schedule_once(lambda dt: toast(f"Delete failed: {error}"))
                else:
                    Clock.schedule_once(lambda dt: toast("Respondent deleted successfully"))
                    Clock.schedule_once(lambda dt: self.refresh_data())
                    
            except Exception as e:
                print(f"Error deleting respondent: {e}")
                Clock.schedule_once(lambda dt: toast(f"Delete error: {str(e)}"))
            finally:
                Clock.schedule_once(lambda dt: self.show_loader(False))
        
        threading.Thread(target=_delete_in_thread, daemon=True).start() 
        threading.Thread(target=_delete_in_thread, daemon=True).start() 