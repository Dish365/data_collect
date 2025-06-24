# Dashboard Integration Guide

This guide explains the implementation of dashboard endpoints that interface between the Django backend and Kivy frontend for the Research Data Collection Tool.

## Overview

The dashboard system provides real-time statistics and activity feeds for authenticated users, with role-based access control and efficient data fetching strategies.

## Backend Implementation

### Endpoints

#### 1. Dashboard Stats (`/api/v1/dashboard-stats/`)
**Method:** GET  
**Authentication:** Required  
**Purpose:** Get comprehensive dashboard statistics

**Response:**
```json
{
  "total_responses": 1250,
  "active_projects": 15,
  "team_members": 8,
  "pending_sync": 3,
  "failed_sync": 1,
  "recent_responses": 45,
  "completion_rate": 78.5,
  "user_permissions": {
    "can_manage_users": true,
    "can_create_projects": true,
    "can_collect_data": true
  },
  "summary": {
    "projects_with_responses": 12,
    "total_questions": 156,
    "avg_responses_per_project": 83.3
  }
}
```

#### 2. Activity Stream (`/api/v1/activity-stream/`)
**Method:** GET  
**Authentication:** Required  
**Purpose:** Get recent activity feed

**Response:**
```json
[
  {
    "text": "Response collected for \"Market Research\" by John Smith",
    "timestamp": "2024-01-15T14:30:00",
    "verb": "submitted",
    "type": "response",
    "project_name": "Market Research",
    "project_id": "uuid-here"
  },
  {
    "text": "Project \"Customer Survey\" created by Admin User",
    "timestamp": "2024-01-15T13:15:00",
    "verb": "created",
    "type": "project",
    "project_name": "Customer Survey",
    "project_id": "uuid-here"
  }
]
```

#### 3. Combined Dashboard (`/api/v1/dashboard/`) 
**Method:** GET  
**Authentication:** Required  
**Purpose:** Get both stats and activity in a single request (recommended for better performance)

**Response:**
```json
{
  "stats": {
    "total_responses": 1250,
    "active_projects": 15,
    "team_members": 8,
    "pending_sync": 3,
    "failed_sync": 1,
    "recent_responses": 45,
    "user_permissions": {
      "can_manage_users": true,
      "can_create_projects": true,
      "can_collect_data": true
    }
  },
  "activity_feed": [...],
  "timestamp": "2024-01-15T14:35:00"
}
```

### Role-Based Access Control

- **Admin Users**: See all projects and system-wide statistics
- **Researchers**: See all projects and can create new ones
- **Field Workers**: See only their own data collection activities

### Error Handling

All endpoints include comprehensive error handling:
```json
{
  "error": "Failed to calculate dashboard statistics",
  "message": "Database connection timeout"
}
```

## Frontend Implementation

### DashboardService

The `DashboardService` class handles all communication with the backend:

```python
# Usage
dashboard_service = DashboardService(auth_service, db_service)
stats = dashboard_service.get_dashboard_stats()
```

### Key Features

1. **Smart Endpoint Selection**: Automatically tries the combined endpoint first, falls back to separate endpoints
2. **Concurrent Execution**: Fetches data from multiple sources simultaneously
3. **Fallback Handling**: Graceful degradation when API is unavailable
4. **Local Database Integration**: Merges API data with local SQLite data

### Dashboard Screen

The `DashboardScreen` provides:
- Real-time statistics display
- Activity feed with timestamps
- Auto-refresh every 30 seconds
- Manual refresh button
- Role-based UI adjustments
- Error handling with user feedback

## Testing

### Running Backend Tests

```bash
cd backend
python test_dashboard_endpoints.py
```

This will:
- Create test data
- Test all dashboard endpoints
- Verify authentication
- Check role-based permissions
- Clean up test data

### Expected Test Output

```
Starting Dashboard Endpoint Tests...
==================================================
Setting up test data...
Test data setup complete!

=== Testing Dashboard Stats Endpoint ===
Status Code: 200
✓ Dashboard stats endpoint working correctly

=== Testing Activity Stream Endpoint ===
Status Code: 200
✓ Activity stream endpoint working correctly

=== Testing Combined Dashboard Endpoint ===
Status Code: 200
✓ Combined dashboard endpoint working correctly

=== Testing Permission Handling ===
✓ Permission handling working correctly

=== Testing Unauthenticated Access ===
✓ Authentication protection working correctly

==================================================
🎉 All dashboard endpoint tests passed!
🚀 Dashboard endpoints are ready for frontend integration!
```

## Usage Examples

### Frontend Integration

```python
class DashboardScreen(MDScreen):
    def update_stats(self):
        def _update_in_thread():
            stats = self.dashboard_service.get_dashboard_stats()
            Clock.schedule_once(lambda dt: self._update_ui(stats))
        
        threading.Thread(target=_update_in_thread, daemon=True).start()
```

### API Testing with curl

```bash
# Login and get token
curl -X POST http://127.0.0.1:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_email", "password": "your_password"}'

# Use token for dashboard requests
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
  http://127.0.0.1:8000/api/v1/dashboard/
```

## Performance Considerations

### Backend Optimizations

1. **Database Queries**: Uses `select_related()` and `distinct()` for efficient queries
2. **Role-Based Filtering**: Filters data at the database level
3. **Caching**: Activity data is limited to recent items only
4. **Error Logging**: Comprehensive logging for debugging

### Frontend Optimizations

1. **Combined Endpoint**: Single request instead of multiple calls
2. **Background Threading**: Non-blocking UI updates
3. **Auto-refresh**: Configurable refresh intervals
4. **Fallback Strategy**: Multiple levels of graceful degradation

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure token is valid and not expired
   - Check `Authorization: Token <token>` header format

2. **Permission Denied**
   - Verify user role and permissions
   - Check project access rights

3. **Network Issues**
   - Frontend automatically handles offline mode
   - Shows "Offline" status for unavailable data

4. **Database Errors**
   - Check Django database connections
   - Verify model relationships

### Debug Mode

Enable debug logging in Django settings:
```python
LOGGING = {
    'loggers': {
        'api.v1.views': {
            'level': 'DEBUG',
        }
    }
}
```

## Security Considerations

1. **Authentication Required**: All endpoints require valid tokens
2. **Role-Based Access**: Data filtered by user permissions
3. **Input Validation**: All user inputs are validated
4. **Error Information**: Sensitive information not exposed in errors

## Future Enhancements

Potential improvements for the dashboard system:

1. **Real-time Updates**: WebSocket integration for live updates
2. **Caching**: Redis caching for frequently accessed data
3. **Analytics**: More detailed statistics and trends
4. **Customization**: User-configurable dashboard widgets
5. **Export**: Export dashboard data to various formats

## Files Modified/Created

### Backend Files
- `backend/api/v1/views.py` - Enhanced dashboard endpoints
- `backend/api/v1/urls.py` - Added combined dashboard route
- `backend/test_dashboard_endpoints.py` - Comprehensive test suite

### Frontend Files
- `gui/services/dashboard_service.py` - Enhanced service with fallback strategies
- `gui/screens/dashboard.py` - Improved screen with auto-refresh and error handling
- `gui/kv/dashboard.kv` - Added refresh button to UI

### Documentation
- `DASHBOARD_INTEGRATION_GUIDE.md` - This integration guide

## Conclusion

The dashboard endpoint implementation provides a robust, scalable solution for displaying real-time research data with proper authentication, role-based access control, and efficient frontend-backend integration. The system is designed to handle both online and offline scenarios gracefully while providing comprehensive error handling and user feedback. 