from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import MDGridLayout
from kivy.app import App

import threading
from datetime import datetime

Builder.load_file("kv/responses.kv")


class ResponseDetailDialog(MDBoxLayout):
    """Dialog content for showing detailed responses"""
    def __init__(self, respondent_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(400)
        
        # Respondent info header
        header = MDLabel(
            text=f"Responses from {respondent_data.get('display_name', 'Unknown')}",
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
        )
        self.add_widget(header)
        
        # Project info
        project_info = MDLabel(
            text=f"Project: {respondent_data.get('project_name', 'Unknown')}",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(30)
        )
        self.add_widget(project_info)
        
        # Responses list
        from kivymd.uix.scrollview import MDScrollView
        scroll = MDScrollView()
        responses_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            adaptive_height=True,
            padding=dp(10)
        )
        
        responses = respondent_data.get('responses', [])
        if not responses:
            no_responses = MDLabel(
                text="No responses found for this respondent",
                halign="center",
                size_hint_y=None,
                height=dp(40)
            )
            responses_layout.add_widget(no_responses)
        else:
            for i, response in enumerate(responses):
                response_card = MDCard(
                    orientation="vertical",
                    padding=dp(10),
                    spacing=dp(5),
                    size_hint_y=None,
                    height=dp(80),
                    elevation=2
                )
                
                question_label = MDLabel(
                    text=f"Q{i+1}: {response.get('question_text', 'Unknown Question')}",
                    font_style="Subtitle2",
                    size_hint_y=None,
                    height=dp(25)
                )
                
                answer_label = MDLabel(
                    text=f"Answer: {response.get('response_value', 'No answer')}",
                    font_style="Body1",
                    size_hint_y=None,
                    height=dp(25)
                )
                
                time_label = MDLabel(
                    text=f"Collected: {response.get('collected_at_formatted', 'Unknown time')}",
                    font_style="Caption",
                    size_hint_y=None,
                    height=dp(20)
                )
                
                response_card.add_widget(question_label)
                response_card.add_widget(answer_label)
                response_card.add_widget(time_label)
                responses_layout.add_widget(response_card)
        
        scroll.add_widget(responses_layout)
        self.add_widget(scroll)


class ResponseItem(MDCard):
    """Widget for displaying a single respondent row in the table"""
    def __init__(self, respondent_data, on_view_responses=None, on_edit_respondent=None, on_delete_respondent=None, **kwargs):
        super().__init__(**kwargs)
        self.respondent_data = respondent_data
        self.on_view_responses = on_view_responses
        self.on_edit_respondent = on_edit_respondent
        self.on_delete_respondent = on_delete_respondent
        self.orientation = "horizontal"
        self.padding = dp(10)
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(60)
        self.elevation = 1
        
        # Safe value extraction with defaults
        respondent_id = respondent_data.get('respondent_id') or 'Unknown'
        display_name = respondent_data.get('display_name') or 'Anonymous'
        project_name = respondent_data.get('project_name') or 'Unknown Project'
        response_count = respondent_data.get('response_count') or 0
        last_response = respondent_data.get('last_response_formatted') or 'No responses'
        
        # Respondent ID
        respondent_id_text = respondent_id[-12:] if len(respondent_id) > 12 else respondent_id
        respondent_id_label = MDLabel(
            text=respondent_id_text,
            size_hint_x = 0.2,
            font_style="Body2",
            halign="left"
        )
        respondent_id_label.bind(size=respondent_id_label.setter('text_size'))
        
        # Display Name
        name_label = MDLabel(
            text=display_name,
            size_hint_x = 0.2,
            font_style="Body2",
            halign="left"
        )
        name_label.bind(size=name_label.setter('text_size'))
        
        # Project Name
        project_label = MDLabel(
            text=project_name,
            size_hint_x = 0.2,
            font_style="Body2",
            halign="left"
        )
        project_label.bind(size=project_label.setter('text_size'))
        
        # Response Count
        count_label = MDLabel(
            text=str(response_count),
            size_hint_x = 0.1,
            font_style="Body2",
            halign="center"
        )
        
        # Last Response Date
        date_label = MDLabel(
            text=last_response,
            size_hint_x = 0.15,
            font_style="Body2",
            halign="center"
        )
        date_label.bind(size=date_label.setter('text_size'))
        
        # Actions (View, Edit, Delete)
        actions_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_x=0.15,
            spacing=dp(2)
        )
        
        # View Button
        view_button = MDFlatButton(
            text="View",
            size_hint_x=None,
            width=dp(50),
            on_release=self.view_responses
        )
        
        # Edit Button
        edit_button = MDFlatButton(
            text="Edit",
            size_hint_x=None,
            width=dp(50),
            on_release=self.edit_respondent
        )
        
        # Delete Button
        delete_button = MDFlatButton(
            text="Del",
            size_hint_x=None,
            width=dp(40),
            theme_text_color="Error",
            on_release=self.delete_respondent
        )
        
        actions_layout.add_widget(view_button)
        actions_layout.add_widget(edit_button)
        actions_layout.add_widget(delete_button)
        
        self.add_widget(respondent_id_label)
        self.add_widget(name_label)
        self.add_widget(project_label)
        self.add_widget(count_label)
        self.add_widget(date_label)
        self.add_widget(actions_layout)
    
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


class ResponsesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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

    def on_enter(self):
        """Called when screen is entered"""
        self.ids.top_bar.set_title("Responses")
        self.load_summary_stats()
        self.load_respondents()

    def show_loader(self, show=True):
        """Show/hide loading spinner"""
        if hasattr(self.ids, 'spinner'):
            self.ids.spinner.active = show
        if hasattr(self.ids, 'content_layout'):
            self.ids.content_layout.opacity = 0.3 if show else 1
            self.ids.content_layout.disabled = show

    def load_summary_stats(self):
        """Load summary statistics for the header"""
        def _load_stats():
            try:
                summary, error = self.responses_service.get_respondents_summary()
                if error:
                    print(f"Error loading summary: {error}")
                    return
                Clock.schedule_once(lambda dt: self._update_summary_ui(summary))
            except Exception as e:
                print(f"Exception loading summary: {e}")
        
        threading.Thread(target=_load_stats, daemon=True).start()

    def _update_summary_ui(self, summary):
        """Update the summary statistics in the UI"""
        try:
            # Safely extract values with defaults
            total_respondents = summary.get('total_respondents', 0) if summary else 0
            total_responses = summary.get('total_responses', 0) if summary else 0
            avg_responses = summary.get('avg_responses_per_respondent', 0.0) if summary else 0.0
            
            # Update labels with safe values
            if hasattr(self.ids, 'total_respondents_label'):
                self.ids.total_respondents_label.text = f"Total Respondents: {total_respondents}"
            if hasattr(self.ids, 'total_responses_label'):
                self.ids.total_responses_label.text = f"Total Responses: {total_responses}"
            if hasattr(self.ids, 'avg_responses_label'):
                self.ids.avg_responses_label.text = f"Avg per Respondent: {avg_responses}"
        except Exception as e:
            print(f"Error updating summary UI: {e}")
            # Set fallback values on error
            try:
                if hasattr(self.ids, 'total_respondents_label'):
                    self.ids.total_respondents_label.text = "Total Respondents: 0"
                if hasattr(self.ids, 'total_responses_label'):
                    self.ids.total_responses_label.text = "Total Responses: 0"
                if hasattr(self.ids, 'avg_responses_label'):
                    self.ids.avg_responses_label.text = "Avg per Respondent: 0.0"
            except:
                pass

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
            
            # Add new respondent items
            for respondent in new_respondents:
                item = ResponseItem(
                    respondent_data=respondent,
                    on_view_responses=self.view_respondent_responses,
                    on_edit_respondent=self.edit_respondent,
                    on_delete_respondent=self.delete_respondent
                )
                self.ids.responses_grid.add_widget(item)
            
            # Add load more button if not last page
            if not is_last_page and len(new_respondents) >= self.page_limit:
                load_more_btn = MDRaisedButton(
                    text="Load More",
                    size_hint_y=None,
                    height=dp(40),
                    on_release=lambda x: self.load_respondents(load_more=True)
                )
                load_more_btn.id = 'load_more_button'
                self.ids.load_more_button = load_more_btn
                self.ids.content_layout.add_widget(load_more_btn)
            
            # Show no data message if empty
            if not self.respondents_data:
                no_data_label = MDLabel(
                    text="No responses found. Start collecting data to see respondents here.",
                    halign="center",
                    font_style="Subtitle1",
                    size_hint_y=None,
                    height=dp(60)
                )
                self.ids.responses_grid.add_widget(no_data_label)
                
        except Exception as e:
            print(f"Error updating UI: {e}")

    def view_respondent_responses(self, respondent_data):
        """Show detailed responses for a respondent"""
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

    def _show_response_dialog(self, respondent_data):
        """Show the response detail dialog"""
        try:
            content = ResponseDetailDialog(respondent_data)
            
            self.detail_dialog = MDDialog(
                title="Response Details",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(
                        text="CLOSE",
                        on_release=lambda x: self.detail_dialog.dismiss()
                    )
                ],
                size_hint=(0.9, 0.8)
            )
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
            from kivymd.uix.textfield import MDTextField
            from kivymd.uix.selectioncontrol import MDCheckbox
            
            content = MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                size_hint_y=None,
                height=dp(300)
            )
            
            # Name field
            name_field = MDTextField(
                hint_text="Name (optional)",
                text=respondent_data.get('name', ''),
                size_hint_y=None,
                height=dp(40)
            )
            
            # Email field
            email_field = MDTextField(
                hint_text="Email (optional)",
                text=respondent_data.get('email', ''),
                size_hint_y=None,
                height=dp(40)
            )
            
            # Phone field
            phone_field = MDTextField(
                hint_text="Phone (optional)",
                text=respondent_data.get('phone', ''),
                size_hint_y=None,
                height=dp(40)
            )
            
            # Anonymous checkbox
            checkbox_layout = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(40),
                spacing=dp(10)
            )
            
            anonymous_checkbox = MDCheckbox(
                active=respondent_data.get('is_anonymous', True),
                size_hint_x=None,
                width=dp(30)
            )
            
            checkbox_label = MDLabel(
                text="Anonymous respondent",
                size_hint_y=None,
                height=dp(40)
            )
            
            checkbox_layout.add_widget(anonymous_checkbox)
            checkbox_layout.add_widget(checkbox_label)
            
            content.add_widget(MDLabel(text=f"Edit Respondent: {respondent_data.get('respondent_id', 'Unknown')}", font_style="H6"))
            content.add_widget(name_field)
            content.add_widget(email_field)
            content.add_widget(phone_field)
            content.add_widget(checkbox_layout)
            
            def save_changes(instance):
                updated_data = {
                    'name': name_field.text.strip() if name_field.text.strip() else None,
                    'email': email_field.text.strip() if email_field.text.strip() else None,
                    'phone': phone_field.text.strip() if phone_field.text.strip() else None,
                    'is_anonymous': anonymous_checkbox.active
                }
                self._update_respondent(respondent_data['id'], updated_data)
                self.edit_dialog.dismiss()
            
            self.edit_dialog = MDDialog(
                title="Edit Respondent",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda x: self.edit_dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="SAVE",
                        on_release=save_changes
                    )
                ],
                size_hint=(0.8, None)
            )
            self.edit_dialog.open()
            
        except Exception as e:
            print(f"Error showing edit dialog: {e}")
            toast("Error opening edit dialog")

    def delete_respondent(self, respondent_data):
        """Show delete confirmation dialog"""
        try:
            content = MDLabel(
                text=f"Are you sure you want to delete respondent '{respondent_data.get('display_name', 'Unknown')}'?\n\nThis will also delete all their responses and cannot be undone.",
                halign="center",
                size_hint_y=None,
                height=dp(100)
            )
            
            def confirm_delete(instance):
                self._delete_respondent(respondent_data['id'])
                self.delete_dialog.dismiss()
            
            self.delete_dialog = MDDialog(
                title="Confirm Delete",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda x: self.delete_dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="DELETE",
                        theme_bg_color="Error",
                        on_release=confirm_delete
                    )
                ],
                size_hint=(0.8, None)
            )
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