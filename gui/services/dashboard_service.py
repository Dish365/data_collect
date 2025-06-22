import concurrent.futures
from datetime import datetime
import humanize

class DashboardService:
    def __init__(self, auth_service, db_service):
        self.auth_service = auth_service
        self.db_service = db_service

    def get_dashboard_stats(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit all tasks to the executor
            future_api_stats = executor.submit(self._fetch_api_stats)
            future_db_stats = executor.submit(self._fetch_db_stats)
            future_activity = executor.submit(self._fetch_activity_feed)

            # Get results
            api_stats = future_api_stats.result()
            db_stats = future_db_stats.result()
            activity_feed = future_activity.result()

            # Merge results
            stats = {**api_stats, **db_stats, "activity_feed": activity_feed}
            return stats

    def _fetch_api_stats(self):
        """Fetches stats from the backend API."""
        response = self.auth_service.make_authenticated_request('api/v1/dashboard-stats/')
        if 'error' in response:
            return {
                "total_responses": "No data available",
                "team_members": "No data available"
            }
        return {
            "total_responses": str(response.get("total_responses", "N/A")),
            "team_members": str(response.get("team_members", "N/A"))
        }

    def _fetch_activity_feed(self):
        """Fetches recent activity from the backend."""
        response = self.auth_service.make_authenticated_request('api/v1/activity-stream/')
        if 'error' in response or not isinstance(response, list):
            return []
        
        # Process activities
        processed_feed = []
        for item in response:
            try:
                # Example: "2 hours ago"
                timestamp = datetime.fromisoformat(item.get('timestamp').replace('Z', ''))
                time_ago = humanize.naturaltime(datetime.now() - timestamp)

                processed_feed.append({
                    "text": item.get('text', 'No activity text.'),
                    "time": time_ago,
                    "icon": self._get_icon_for_activity(item.get('verb'))
                })
            except (ValueError, TypeError):
                continue # Skip items with bad timestamps
        
        return processed_feed

    def _get_icon_for_activity(self, verb):
        verb_to_icon = {
            "created": "plus-circle",
            "updated": "pencil-circle",
            "deleted": "delete-circle",
            "submitted": "check-circle",
            "joined": "account-plus"
        }
        return verb_to_icon.get(verb, "information")

    def _fetch_db_stats(self):
        """Fetches stats from the local database."""
        conn = self.db_service.get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Active projects
            cursor.execute("SELECT COUNT(*) FROM projects WHERE sync_status != 'pending_delete'")
            active_projects = cursor.fetchone()[0]

            # Pending sync
            cursor.execute("SELECT COUNT(*) FROM sync_queue WHERE status = 'pending'")
            pending_sync = cursor.fetchone()[0]

            return {
                "active_projects": str(active_projects),
                "pending_sync": str(pending_sync)
            }
        except Exception as e:
            print(f"Error fetching DB stats: {e}")
            return {
                "active_projects": "N/A",
                "pending_sync": "N/A"
            }
        finally:
            if conn:
                conn.close() 