import concurrent.futures
from datetime import datetime
import humanize

class DashboardService:
    def __init__(self, auth_service, db_service):
        self.auth_service = auth_service
        self.db_service = db_service
        self.use_combined_endpoint = True  # Flag to use combined endpoint by default

    def get_current_user_id(self):
        """Get the current user ID from auth service"""
        try:
            user_data = self.auth_service.get_user_data()
            if user_data and 'id' in user_data:
                return user_data['id']
            return None
        except Exception as e:
            print(f"Error getting user ID: {e}")
            return None

    def get_dashboard_stats(self):
        """Main method to get dashboard statistics with multiple fallback strategies"""
        # Ensure we have user context
        user_id = self.get_current_user_id()
        if not user_id:
            print("Warning: No user ID available for dashboard stats")
            # Still try to get stats, but they may not be user-specific
        
        if self.use_combined_endpoint:
            return self._get_dashboard_stats_combined()
        else:
            return self._get_dashboard_stats_separate()

    def _get_dashboard_stats_combined(self):
        """Fetch dashboard data using the combined endpoint for better performance"""
        try:
            # Try combined endpoint first
            response = self.auth_service.make_authenticated_request('api/v1/dashboard/')
            
            if 'error' in response:
                print(f"Combined endpoint error: {response.get('message', 'Unknown error')}")
                # Fallback to separate endpoints
                self.use_combined_endpoint = False
                return self._get_dashboard_stats_separate()
            
            # Extract stats and activity feed from combined response
            stats = response.get('stats', {})
            activity_feed = response.get('activity_feed', [])
            
            # Process activity feed
            processed_activity = self._process_activity_feed(activity_feed)
            
            # Use API data as the primary source - don't mix with local DB
            # Local DB data might be stale or have incorrect user associations
            combined_stats = {
                'total_respondents': str(stats.get('total_respondents', 'N/A')),
                'team_members': str(stats.get('team_members', 'N/A')),
                'active_projects': str(stats.get('active_projects', 'N/A')),  # Use API data
                'pending_sync': str(stats.get('pending_sync', 'N/A')),  # Use API data
                'failed_sync': str(stats.get('failed_sync', '0')),  # Use API data
                'recent_responses': str(stats.get('recent_responses', '0')),
                'user_permissions': stats.get('user_permissions', {}),
                'activity_feed': processed_activity,
                'last_updated': response.get('timestamp', datetime.now().isoformat())
            }
            
            print(f"Combined dashboard stats from API: {combined_stats}")
            return combined_stats
            
        except Exception as e:
            print(f"Error with combined endpoint: {e}")
            # Fallback to separate endpoints
            self.use_combined_endpoint = False
            return self._get_dashboard_stats_separate()

    def _get_dashboard_stats_separate(self):
        """Original method using separate endpoints with concurrent execution"""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit all tasks to the executor
            future_api_stats = executor.submit(self._fetch_api_stats)
            future_activity = executor.submit(self._fetch_activity_feed)
            # Don't fetch local DB stats if we have API data
            
            # Get results with timeout
            try:
                api_stats = future_api_stats.result(timeout=10)
                activity_feed = future_activity.result(timeout=10)
                
                # Only use local DB as fallback if API fails
                if 'Offline' in str(api_stats.get('active_projects', '')):
                    print("API is offline, falling back to local database")
                    future_db_stats = executor.submit(self._fetch_db_stats)
                    db_stats = future_db_stats.result(timeout=5)
                    # Merge with API data taking precedence
                    stats = {**db_stats, **api_stats, "activity_feed": activity_feed}
                else:
                    # Use API data only
                    stats = {**api_stats, "activity_feed": activity_feed}
                    
            except concurrent.futures.TimeoutError:
                print("Timeout occurred while fetching dashboard data")
                api_stats = self._get_fallback_api_stats()
                db_stats = self._get_fallback_db_stats()
                activity_feed = []
                stats = {**db_stats, **api_stats, "activity_feed": activity_feed}

            return stats

    def _fetch_api_stats(self):
        """Fetches stats from the backend API."""
        try:
            response = self.auth_service.make_authenticated_request('api/v1/dashboard-stats/')
            if 'error' in response:
                print(f"API stats error: {response.get('message', 'Unknown error')}")
                return self._get_fallback_api_stats()
                
            return {
                "total_respondents": str(response.get("total_respondents", "N/A")),
                "team_members": str(response.get("team_members", "N/A")),
                "active_projects": str(response.get("active_projects", "N/A")),  # Add this
                "pending_sync": str(response.get("pending_sync", "N/A")),  # Add this
                "failed_sync": str(response.get("failed_sync", "0")),
                "recent_responses": str(response.get("recent_responses", "0")),
                "user_permissions": response.get("user_permissions", {}),
                "completion_rate": str(response.get("completion_rate", "N/A"))
            }
        except Exception as e:
            print(f"Exception in _fetch_api_stats: {e}")
            return self._get_fallback_api_stats()

    def _fetch_activity_feed(self):
        """Fetches recent activity from the backend."""
        try:
            response = self.auth_service.make_authenticated_request('api/v1/activity-stream/')
            if 'error' in response or not isinstance(response, list):
                print(f"Activity feed error: {response.get('message', 'Invalid response format') if isinstance(response, dict) else 'Invalid response'}")
                return []
            
            return self._process_activity_feed(response)
            
        except Exception as e:
            print(f"Exception in _fetch_activity_feed: {e}")
            return []

    def _process_activity_feed(self, activity_data):
        """Process activity data from backend into frontend format"""
        processed_feed = []
        
        for item in activity_data:
            try:
                # Handle different timestamp formats
                timestamp_str = item.get('timestamp', '')
                if timestamp_str:
                    # Remove Z suffix if present and parse
                    timestamp_str = timestamp_str.replace('Z', '')
                    if '+' in timestamp_str:
                        timestamp_str = timestamp_str.split('+')[0]
                    
                    timestamp = datetime.fromisoformat(timestamp_str)
                    time_ago = humanize.naturaltime(datetime.now() - timestamp)
                else:
                    time_ago = "Unknown time"

                processed_feed.append({
                    "text": item.get('text', 'No activity text.'),
                    "time": time_ago,
                    "icon": self._get_icon_for_activity(item.get('verb')),
                    "type": item.get('type', 'unknown')
                })
            except (ValueError, TypeError) as e:
                print(f"Error processing activity item: {e}")
                continue # Skip items with bad timestamps
        
        return processed_feed

    def _get_icon_for_activity(self, verb):
        """Map activity verbs to appropriate icons"""
        verb_to_icon = {
            "created": "plus-circle",
            "updated": "pencil-circle",
            "deleted": "delete-circle",
            "submitted": "check-circle",
            "joined": "account-plus",
            "synced": "sync",
            "sync_failed": "sync-alert",
            "member_added": "account-plus",
            "member_removed": "account-minus",
            "member_updated": "account-edit"
        }
        return verb_to_icon.get(verb, "information")

    def _fetch_db_stats(self):
        """Fetches user-specific stats from the local database."""
        try:
            user_id = self.get_current_user_id()
            if not user_id:
                print("Warning: No user ID for local DB stats - using fallback")
                return self._get_fallback_db_stats()
                
            conn = self.db_service.get_db_connection()
            cursor = conn.cursor()
            
            # Active projects - user-specific
            cursor.execute(
                "SELECT COUNT(*) FROM projects WHERE user_id = ? AND sync_status != 'pending_delete'", 
                (user_id,)
            )
            active_projects = cursor.fetchone()[0]

            # Total completed forms (respondents) - user-specific
            cursor.execute(
                "SELECT COUNT(*) FROM respondents WHERE user_id = ?", 
                (user_id,)
            )
            total_respondents = cursor.fetchone()[0]

            # Pending sync - user-specific
            cursor.execute(
                "SELECT COUNT(*) FROM sync_queue WHERE user_id = ? AND status = 'pending'", 
                (user_id,)
            )
            pending_sync = cursor.fetchone()[0]

            # Failed sync - user-specific
            cursor.execute(
                "SELECT COUNT(*) FROM sync_queue WHERE user_id = ? AND status = 'failed'", 
                (user_id,)
            )
            failed_sync = cursor.fetchone()[0]

            print(f"Local DB stats for user {user_id}: Projects={active_projects}, Respondents={total_respondents}, Pending={pending_sync}, Failed={failed_sync}")
            
            return {
                "active_projects": str(active_projects),
                "total_respondents": str(total_respondents),
                "pending_sync": str(pending_sync),
                "failed_sync": str(failed_sync)
            }
        except Exception as e:
            print(f"Error fetching DB stats: {e}")
            return self._get_fallback_db_stats()
        finally:
            if conn:
                conn.close()

    def _get_fallback_api_stats(self):
        """Fallback stats when API is unavailable"""
        return {
            "total_respondents": "Offline",
            "team_members": "Offline",
            "active_projects": "Offline",
            "pending_sync": "Offline",
            "failed_sync": "0",
            "recent_responses": "0",
            "user_permissions": {},
            "completion_rate": "N/A"
        }

    def _get_fallback_db_stats(self):
        """Fallback stats when local DB is unavailable"""
        return {
            "active_projects": "N/A",
            "total_respondents": "N/A",
            "pending_sync": "N/A",
            "failed_sync": "N/A"
        }

    def refresh_stats(self):
        """Force refresh of dashboard statistics"""
        self.use_combined_endpoint = True  # Reset to try combined endpoint again
        return self.get_dashboard_stats()

    def get_user_permissions(self):
        """Get user permissions from the last fetched stats"""
        try:
            stats = self.get_dashboard_stats()
            return stats.get('user_permissions', {})
        except Exception as e:
            print(f"Error getting user permissions: {e}")
            return {}

    def initialize_for_user(self):
        """Initialize dashboard service for the current user"""
        try:
            # Step 1: Verify auth service has user data
            user_id = self.get_current_user_id()
            if not user_id:
                print("Warning: Could not initialize dashboard service - no user ID from auth service")
                return False
            
            print(f"Initializing dashboard for user: {user_id}")
            
            # Step 2: Ensure database session is set for this user
            db_user = self.db_service.get_current_user()
            if db_user != user_id:
                print(f"Database user context mismatch. Auth: {user_id}, DB: {db_user}")
                self.db_service.set_current_user(user_id)
                
                # Verify the context was set correctly
                db_user_after = self.db_service.get_current_user()
                if db_user_after != user_id:
                    print(f"Failed to set database user context. Expected: {user_id}, Got: {db_user_after}")
                    return False
                print(f"Database user context updated to: {db_user_after}")
            
            # Step 3: Test API connectivity
            try:
                test_response = self.auth_service.make_authenticated_request('api/v1/dashboard-stats/')
                if 'error' in test_response:
                    print(f"API test failed: {test_response.get('message', 'Unknown error')}")
                    print("Dashboard will use local data only")
                else:
                    print("API connectivity confirmed")
            except Exception as e:
                print(f"API test failed with exception: {e}")
                print("Dashboard will use local data only")
            
            # Step 4: Force a refresh to get user-specific data
            self.use_combined_endpoint = True
            
            print(f"Dashboard service successfully initialized for user: {user_id}")
            return True
            
        except Exception as e:
            print(f"Error initializing dashboard service: {e}")
            return False

    # Team Member Management Methods
    
    def get_available_users(self):
        """Get list of users that can be invited to projects"""
        try:
            response = self.auth_service.make_authenticated_request('api/v1/projects/available_users/')
            if 'error' in response:
                print(f"Error getting available users: {response.get('message', 'Unknown error')}")
                return []
            
            return response.get('users', [])
            
        except Exception as e:
            print(f"Exception getting available users: {e}")
            return []
    
    def search_users(self, query):
        """Search for users by username, email, or name"""
        try:
            if not query or len(query.strip()) < 2:
                return []
                
            response = self.auth_service.make_authenticated_request(f'api/v1/auth/search-users/?q={query.strip()}')
            if 'error' in response:
                print(f"Error searching users: {response.get('message', 'Unknown error')}")
                return []
            
            return response.get('users', [])
            
        except Exception as e:
            print(f"Exception searching users: {e}")
            return []
    
    def get_project_members(self, project_id):
        """Get team members for a specific project"""
        try:
            response = self.auth_service.make_authenticated_request(f'api/v1/projects/{project_id}/members/')
            if 'error' in response:
                print(f"Error getting project members: {response.get('message', 'Unknown error')}")
                return []
            
            return response.get('team_members', [])
            
        except Exception as e:
            print(f"Exception getting project members: {e}")
            return []
    
    def invite_team_member(self, project_id, user_email, role='member', permissions=None):
        """Invite a user to join a project team"""
        try:
            data = {
                'user_email': user_email,
                'role': role
            }
            
            if permissions:
                data['permissions'] = permissions
            
            response = self.auth_service.make_authenticated_request(
                f'api/v1/projects/{project_id}/invite_member/',
                method='POST',
                data=data
            )
            
            if 'error' in response:
                return False, response.get('error', 'Unknown error')
            
            return True, response.get('message', 'Team member invited successfully')
            
        except Exception as e:
            print(f"Exception inviting team member: {e}")
            return False, str(e)
    
    def remove_team_member(self, project_id, user_id):
        """Remove a team member from a project"""
        try:
            # Send user_id as query parameter for DELETE request
            response = self.auth_service.make_authenticated_request(
                f'api/v1/projects/{project_id}/remove_member/?user_id={user_id}',
                method='DELETE'
            )
            
            if 'error' in response:
                return False, response.get('error', 'Unknown error')
            
            return True, response.get('message', 'Team member removed successfully')
            
        except Exception as e:
            print(f"Exception removing team member: {e}")
            return False, str(e)
    
    def update_team_member(self, project_id, user_id, role=None, permissions=None):
        """Update a team member's role and permissions"""
        try:
            data = {'user_id': user_id}
            
            if role:
                data['role'] = role
            if permissions:
                data['permissions_list'] = permissions
            
            response = self.auth_service.make_authenticated_request(
                f'api/v1/projects/{project_id}/update_member/',
                method='PATCH',
                data=data
            )
            
            if 'error' in response:
                return False, response.get('error', 'Unknown error')
            
            return True, response.get('message', 'Team member updated successfully')
            
        except Exception as e:
            print(f"Exception updating team member: {e}")
            return False, str(e)
    
    def get_user_projects_with_members(self):
        """Get user's projects with team member information"""
        try:
            response = self.auth_service.make_authenticated_request('api/v1/projects/')
            if 'error' in response:
                print(f"Error getting projects: {response.get('message', 'Unknown error')}")
                return []
            
            projects = response.get('results', []) if 'results' in response else response
            
            # Filter projects where user can manage team members (creator)
            manageable_projects = []
            for project in projects:
                user_data = self.auth_service.get_user_data()
                if user_data and project.get('created_by') == user_data.get('id'):
                    manageable_projects.append(project)
            
            return manageable_projects
            
        except Exception as e:
            print(f"Exception getting projects with members: {e}")
            return []
    
    def get_team_member_roles(self):
        """Get available team member roles"""
        return [
            {'id': 'viewer', 'name': 'Viewer', 'description': 'Can view project and responses'},
            {'id': 'member', 'name': 'Member', 'description': 'Can view and edit responses, view analytics'},
            {'id': 'analyst', 'name': 'Analyst', 'description': 'Can run analytics and export data'},
            {'id': 'collaborator', 'name': 'Collaborator', 'description': 'Can edit project and manage questions'},
        ]
    
    def get_team_member_permissions(self):
        """Get available team member permissions"""
        return [
            {'id': 'view_project', 'name': 'View Project'},
            {'id': 'edit_project', 'name': 'Edit Project'}, 
            {'id': 'view_responses', 'name': 'View Responses'},
            {'id': 'edit_responses', 'name': 'Edit Responses'},
            {'id': 'delete_responses', 'name': 'Delete Responses'},
            {'id': 'view_analytics', 'name': 'View Analytics'},
            {'id': 'run_analytics', 'name': 'Run Analytics'},
            {'id': 'manage_questions', 'name': 'Manage Questions'},
            {'id': 'export_data', 'name': 'Export Data'},
        ]
    
    def get_default_permissions_for_role(self, role):
        """Get default permissions for a specific role"""
        role_permissions = {
            'viewer': ['view_project', 'view_responses'],
            'member': ['view_project', 'view_responses', 'edit_responses', 'view_analytics'],
            'analyst': ['view_project', 'view_responses', 'view_analytics', 'run_analytics', 'export_data'],
            'collaborator': ['view_project', 'edit_project', 'view_responses', 'edit_responses', 
                           'view_analytics', 'run_analytics', 'manage_questions', 'export_data'],
        }
        return role_permissions.get(role, ['view_project', 'view_responses'])

    def get_total_team_members_info(self):
        """Get detailed information about team members across all projects"""
        try:
            # Get all user's projects
            response = self.auth_service.make_authenticated_request('api/v1/projects/')
            if 'error' in response:
                return {'total': 0, 'details': 'Error loading projects'}
            
            projects = response.get('results', []) if 'results' in response else response
            
            if not projects:
                return {'total': 0, 'details': 'No projects created yet'}
            
            # Get team member count for each project
            total_members = set()  # Use set to avoid counting same user multiple times
            project_count = len(projects)
            
            for project in projects:
                # Add creator
                if project.get('created_by'):
                    total_members.add(project['created_by'])
                
                # Try to get team members for this project
                try:
                    members_response = self.auth_service.make_authenticated_request(f"api/v1/projects/{project['id']}/members/")
                    if 'team_members' in members_response:
                        for member in members_response['team_members']:
                            total_members.add(member.get('id'))
                except Exception as e:
                    print(f"Could not get members for project {project['id']}: {e}")
                    continue
            
            unique_count = len(total_members)
            
            # Create descriptive text
            if unique_count == 0:
                details = "No team members yet"
            elif unique_count == 1:
                details = "Only you in projects"
            elif project_count == 1:
                details = f"In {project_count} project"
            else:
                details = f"Across {project_count} projects"
            
            return {
                'total': unique_count,
                'details': details,
                'project_count': project_count
            }
            
        except Exception as e:
            print(f"Exception getting team member info: {e}")
            return {'total': 0, 'details': 'Error loading team data'} 