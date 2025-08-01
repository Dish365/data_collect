from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from utils.cross_platform_toast import toast
from kivy.app import App
import threading
from typing import Dict, Any

from widgets.sync_item import SyncItem

# KV file loaded by main app after theme initialization


class SyncScreen(Screen):
    """Sync screen handling only UI logic, delegating data operations to SyncService"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pending_items = []
        self.sync_items_widgets = []
        self.sync_service = None
        self.sort_ascending = True
        
    def on_enter(self):
        """Called when the screen is entered"""
        self._setup_screen()
        self._register_sync_callbacks()
        self.refresh_pending_items()
        
    def on_leave(self):
        """Called when leaving the screen"""
        self._unregister_sync_callbacks()
        
    def _setup_screen(self):
        """Setup screen UI"""
        self.ids.top_bar.set_title("Sync")
        self.ids.top_bar.set_current_screen("sync")
        
        # Get sync service
        app = App.get_running_app()
        if app and hasattr(app, 'sync_service'):
            self.sync_service = app.sync_service
        else:
            toast("Sync service not available")
            return
    
    def _register_sync_callbacks(self):
        """Register callbacks with sync service"""
        if self.sync_service:
            self.sync_service.add_sync_callback(self._on_sync_callback)
    
    def _unregister_sync_callbacks(self):
        """Unregister callbacks from sync service"""
        if self.sync_service:
            self.sync_service.remove_sync_callback(self._on_sync_callback)
    
    def _on_sync_callback(self, success: bool, results: Dict[str, Any]):
        """Callback from sync service"""
        Clock.schedule_once(lambda dt: self._handle_sync_results(success, results), 0)
    
    def _handle_sync_results(self, success: bool, results: Dict[str, Any]):
        """Handle sync results on main thread"""
        if success:
            message = results.get('message', f"Synced {results.get('success_count', 0)} items")
            toast(message)
        else:
            errors = results.get('errors', [])
            error_msg = errors[0] if errors else "Sync failed"
            toast(f"Sync error: {error_msg}")
        
        # Refresh UI
        self.refresh_pending_items()
        self._update_dashboard_stats()
    
    def on_refresh(self, *args):
        """Handle pull-to-refresh"""
        self.refresh_pending_items()
        # Stop refresh animation after a short delay
        def stop_refresh(dt):
            if hasattr(self.ids, 'refresh_layout'):
                self.ids.refresh_layout.refreshing = False
        Clock.schedule_once(stop_refresh, 1)
    
    def refresh_pending_items(self):
        """Refresh pending items from sync service"""
        if not self.sync_service:
            return
            
        # Get data from service
        self.pending_items = self.sync_service.get_pending_items()
        stats = self.sync_service.get_sync_stats()
        
        # Update UI
        self._update_ui(stats)
    
    def _update_ui(self, stats: Dict[str, int]):
        """Update the UI with current data"""
        pending_count = stats.get('pending', 0)
        
        # Update stats
        self.ids.total_items_label.text = f"{pending_count} pending items"
        self._update_status_display(stats)
        
        # Show/hide empty state
        self._toggle_empty_state(pending_count == 0)
        
        # Update items list
        self._update_items_list()
        
        # Update buttons state
        has_pending = pending_count > 0
        self.ids.sync_all_button.disabled = not has_pending or self.sync_service.is_syncing
    
    def _update_status_display(self, stats: Dict[str, int]):
        """Update status display"""
        if self.sync_service.is_syncing:
            self.ids.sync_status_label.text = "Synchronizing..."
            self.ids.status_icon.icon = "sync"
            self._show_progress_card()
        else:
            pending = stats.get('pending', 0)
            failed = stats.get('failed', 0)
            
            if failed > 0:
                self.ids.sync_status_label.text = f"{failed} failed items"
                self.ids.status_icon.icon = "alert-circle"
            elif pending > 0:
                self.ids.sync_status_label.text = "Ready to sync"
                self.ids.status_icon.icon = "check-circle"
            else:
                self.ids.sync_status_label.text = "All synchronized"
                self.ids.status_icon.icon = "check-all"
            
            self._hide_progress_card()
    
    def _show_progress_card(self):
        """Show progress card with animation"""
        if self.ids.progress_card.opacity == 0:
            Animation(opacity=1, duration=0.3).start(self.ids.progress_card)
    
    def _hide_progress_card(self):
        """Hide progress card with animation"""
        if self.ids.progress_card.opacity == 1:
            Animation(opacity=0, duration=0.3).start(self.ids.progress_card)
    
    def _toggle_empty_state(self, show_empty: bool):
        """Show or hide empty state"""
        target_opacity = 1 if show_empty else 0
        if hasattr(self.ids, 'empty_state_card') and self.ids.empty_state_card.opacity != target_opacity:
            Animation(opacity=target_opacity, duration=0.3).start(self.ids.empty_state_card)
    
    def _update_items_list(self):
        """Update the items list"""
        # Clear existing widgets
        for widget in self.sync_items_widgets:
            self.ids.pending_items_layout.remove_widget(widget)
        self.sync_items_widgets.clear()
        
        # Add new widgets
        for item in self.pending_items:
            sync_item = SyncItem(item, on_sync_pressed=self.sync_single_item)
            self.ids.pending_items_layout.add_widget(sync_item)
            self.sync_items_widgets.append(sync_item)
    
    def sync_single_item(self, item_data: Dict[str, Any]):
        """Sync a single item via service"""
        if not self.sync_service or self.sync_service.is_syncing:
            return
        
        # Use threading to avoid blocking UI
        threading.Thread(
            target=self._sync_single_item_thread, 
            args=(item_data,),
            daemon=True
        ).start()
    
    def _sync_single_item_thread(self, item_data: Dict[str, Any]):
        """Sync single item in background thread"""
        success = self.sync_service.sync_single_item(item_data)
        
        # Update UI on main thread
        Clock.schedule_once(
            lambda dt: self._on_single_item_sync_complete(item_data, success), 
            0
        )
    
    def _on_single_item_sync_complete(self, item_data: Dict[str, Any], success: bool):
        """Handle single item sync completion"""
        if success:
            toast("Item synced successfully!")
            # Remove from local list
            self.pending_items = [item for item in self.pending_items if item['id'] != item_data['id']]
            self._update_ui(self.sync_service.get_sync_stats())
        else:
            toast("Failed to sync item")
    
    def sync_all_items(self):
        """Sync all pending items via service"""
        if not self.sync_service or self.sync_service.is_syncing or not self.pending_items:
            return
        
        # Show loading state
        self._show_loading_overlay()
        
        # Start sync in background
        threading.Thread(target=self._sync_all_items_thread, daemon=True).start()
    
    def _sync_all_items_thread(self):
        """Sync all items in background thread"""
        self.sync_service.sync_all()
        # Hide loading overlay
        Clock.schedule_once(lambda dt: self._hide_loading_overlay(), 0)
    
    def _show_loading_overlay(self):
        """Show loading overlay"""
        self.ids.spinner.active = True
        Animation(opacity=1, duration=0.3).start(self.ids.loading_overlay)
    
    def _hide_loading_overlay(self):
        """Hide loading overlay"""
        self.ids.spinner.active = False
        Animation(opacity=0, duration=0.3).start(self.ids.loading_overlay)
    
    def toggle_sort(self):
        """Toggle sort order"""
        self.sort_ascending = not self.sort_ascending
        
        # Update sort icon
        icon = "sort-ascending" if self.sort_ascending else "sort-descending"
        self.ids.sort_button.icon = icon
        
        # Sort items
        self.pending_items.sort(
            key=lambda x: x.get('created_at', ''),
            reverse=not self.sort_ascending
        )
        
        # Update UI
        self._update_items_list()
    
    def _update_dashboard_stats(self):
        """Update dashboard stats after sync"""
        try:
            dashboard_screen = self.manager.get_screen('dashboard')
            if hasattr(dashboard_screen, 'update_stats'):
                dashboard_screen.update_stats()
        except Exception as e:
            print(f"Could not refresh dashboard: {e}")
    
    def clear_completed_items(self):
        """Clear completed sync items"""
        if not self.sync_service:
            return
            
        count = self.sync_service.clear_completed_items()
        if count > 0:
            toast(f"Cleared {count} completed items")
        else:
            toast("No completed items to clear")
    
    def retry_failed_items(self):
        """Retry all failed items"""
        if not self.sync_service:
            return
            
        count = self.sync_service.retry_failed_items()
        if count > 0:
            toast(f"Retrying {count} failed items")
            self.refresh_pending_items()
        else:
            toast("No failed items to retry") 