from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from utils.cross_platform_toast import toast
from kivy.app import App
import threading

from widgets.sync_item import SyncItem

Builder.load_file("kv/sync.kv")

class SyncScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pending_items = []
        self.sync_items_widgets = []
        self.is_syncing = False
        
    def on_enter(self):
        """Called when the screen is entered"""
        self.ids.top_bar.set_title("Sync")
        self.load_pending_items()
        
    def load_pending_items(self):
        """Load pending sync items from the database"""
        try:
            app = App.get_running_app()
            if not app or not hasattr(app, 'db_service'):
                toast("Database service not available")
                return
                
            conn = app.db_service.get_db_connection()
            cursor = conn.cursor()
            
            # Get all pending sync items
            cursor.execute('''
                SELECT * FROM sync_queue 
                WHERE status = 'pending' 
                ORDER BY created_at ASC
            ''')
            
            items = cursor.fetchall()
            self.pending_items = [dict(item) for item in items]
            
            # Update UI
            self.update_ui()
            
        except Exception as e:
            toast(f"Error loading sync items: {str(e)}")
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    def update_ui(self):
        """Update the UI with current pending items"""
        # Update total items count
        self.ids.total_items_label.text = f"Total Items: {len(self.pending_items)}"
        
        # Clear existing sync item widgets
        for widget in self.sync_items_widgets:
            self.ids.pending_items_layout.remove_widget(widget)
        self.sync_items_widgets.clear()
        
        # Add sync item widgets
        for item in self.pending_items:
            sync_item = SyncItem(item, on_sync_pressed=self.sync_single_item)
            self.ids.pending_items_layout.add_widget(sync_item)
            self.sync_items_widgets.append(sync_item)
    
    def sync_single_item(self, sync_data):
        """Sync a single item"""
        if self.is_syncing:
            return
            
        self.is_syncing = True
        self.ids.sync_status_label.text = "Status: Syncing..."
        
        # Run sync in background thread
        threading.Thread(target=self._sync_single_item_thread, args=(sync_data,)).start()
    
    def _sync_single_item_thread(self, sync_data):
        """Sync a single item in background thread"""
        try:
            app = App.get_running_app()
            if not app or not hasattr(app, 'sync_service') or not hasattr(app, 'db_service'):
                raise Exception("Services not available")
            
            # Process the sync item
            app.sync_service._process_sync_item(sync_data, app.db_service.get_db_connection())
            
            # Update UI on main thread
            Clock.schedule_once(lambda dt: self._on_single_sync_complete(sync_data), 0)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._on_sync_error(str(e)), 0)
        finally:
            Clock.schedule_once(lambda dt: self._on_sync_finished(), 0)
    
    def _on_single_sync_complete(self, sync_data):
        """Called when single item sync completes"""
        # Remove the item from the list
        self.pending_items = [item for item in self.pending_items if item['id'] != sync_data['id']]
        self.update_ui()
        toast("Item synced successfully!")
    
    def sync_all_items(self):
        """Sync all pending items"""
        if self.is_syncing or not self.pending_items:
            return
            
        self.is_syncing = True
        self.ids.sync_status_label.text = "Status: Syncing All..."
        self.ids.sync_all_button.disabled = True
        
        # Run sync in background thread
        threading.Thread(target=self._sync_all_items_thread).start()
    
    def _sync_all_items_thread(self):
        """Sync all items in background thread"""
        try:
            app = App.get_running_app()
            if not app or not hasattr(app, 'sync_service') or not hasattr(app, 'db_service'):
                raise Exception("Services not available")
                
            total_items = len(self.pending_items)
            
            for i, item in enumerate(self.pending_items):
                # Update progress
                progress = (i / total_items) * 100
                Clock.schedule_once(lambda dt, p=progress: self._update_progress(p), 0)
                
                # Process the sync item
                app.sync_service._process_sync_item(item, app.db_service.get_db_connection())
            
            # Complete
            Clock.schedule_once(lambda dt: self._on_all_sync_complete(), 0)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._on_sync_error(str(e)), 0)
        finally:
            Clock.schedule_once(lambda dt: self._on_sync_finished(), 0)
    
    def _update_progress(self, progress):
        """Update the progress bar"""
        self.ids.sync_progress.value = progress
    
    def _on_all_sync_complete(self):
        """Called when all items sync completes"""
        self.pending_items.clear()
        self.update_ui()
        self.ids.sync_progress.value = 100
        toast("All items synced successfully!")
    
    def _on_sync_error(self, error_message):
        """Called when sync encounters an error"""
        toast(f"Sync error: {error_message}")
    
    def _on_sync_finished(self):
        """Called when sync process finishes"""
        self.is_syncing = False
        self.ids.sync_status_label.text = "Status: Ready"
        self.ids.sync_all_button.disabled = False
        self.ids.sync_progress.value = 0

        # Refresh dashboard stats
        try:
            dashboard_screen = self.manager.get_screen('dashboard')
            dashboard_screen.update_stats()
        except Exception as e:
            print(f"Could not refresh dashboard: {e}") 