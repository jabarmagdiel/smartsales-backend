import requests
import json

BASE_URL = 'http://127.0.0.1:8000'

def login_admin():
    url = f'{BASE_URL}/api/v1/token/'
    data = {
        'username': 'admin',
        'password': 'admin123'
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json().get('access')
    return None

def test_backup_endpoint(access_token):
    # Use session to handle cookies and CSRF
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {access_token}'})

    # First get the admin page to set cookies
    session.get(f'{BASE_URL}/admin/')

    # Get CSRF token from cookies
    csrf_token = session.cookies.get('csrftoken') or session.cookies.get('csrf_token')
    if csrf_token:
        session.headers.update({'X-CSRFToken': csrf_token})

    url = f'{BASE_URL}/admin/backup/'
    response = session.post(url)
    print(f"Admin Backup Test:")
    print(f"Command: POST {url}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Response: {response.text}")
    print("-" * 50)
    return response.status_code == 200

if __name__ == '__main__':
    print("Starting Admin Backup Test")
    print("=" * 60)

    access_token = login_admin()
    if access_token:
        test_backup_endpoint(access_token)
    else:
        print("Admin login failed")
