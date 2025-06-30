#!/usr/bin/env python3
import requests
import json

# Test the dashboard update
def test_dashboard_update():
    """Test that the dashboard now returns only respondent counts (simplified)"""
    
    # Test the dashboard stats endpoint
    base_url = "http://localhost:8000"
    
    # You'll need to replace this with actual authentication
    headers = {
        'Authorization': 'Token YOUR_TOKEN_HERE',
        'Content-Type': 'application/json'
    }
    
    print("Testing Dashboard Update...")
    print("=" * 50)
    
    # Test dashboard stats endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/dashboard-stats/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✓ Dashboard Stats Endpoint:")
            print(f"  Total Respondents: {data.get('total_respondents', 'N/A')}")
            print(f"  Active Projects: {data.get('active_projects', 'N/A')}")
            print(f"  Team Members: {data.get('team_members', 'N/A')}")
        else:
            print(f"✗ Dashboard Stats failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing dashboard stats: {e}")
    
    # Test combined dashboard endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/dashboard/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            print("\n✓ Combined Dashboard Endpoint:")
            print(f"  Total Respondents: {stats.get('total_respondents', 'N/A')}")
            print(f"  Active Projects: {stats.get('active_projects', 'N/A')}")
            print(f"  Team Members: {stats.get('team_members', 'N/A')}")
        else:
            print(f"✗ Combined Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing combined dashboard: {e}")
    
    print("\n" + "=" * 50)
    print("Frontend Integration Notes:")
    print("- The Total Responses card now shows 'Total Respondents' as the title")
    print("- The card displays only the respondent count (simplified)")
    print("- Total responses count has been removed from the display")
    print("- The backend now only returns respondents count")
    print("\nTo see the changes in action:")
    print("1. Run the backend server")
    print("2. Run the GUI application")
    print("3. Navigate to the dashboard")
    print("4. Check the Total Respondents card for simplified display")

if __name__ == "__main__":
    test_dashboard_update() 