import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api/v1'

def login_admin():
    url = f'{BASE_URL}/token/'
    data = {
        'username': 'admin',
        'password': 'admin123'
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json().get('access')
    return None

def test_generate_recommendations(access_token):
    url = f'{BASE_URL}/logistics/recommendations/generate_recommendations/'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.post(url, headers=headers)
    print(f"Generate Recommendations Test:")
    print(f"Command: POST {url}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Response: {response.text}")
    print("-" * 50)
    return response.status_code == 200

def test_generate_alerts(access_token):
    url = f'{BASE_URL}/logistics/alerts/generate_alerts/'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.post(url, headers=headers)
    print(f"Generate Alerts Test:")
    print(f"Command: POST {url}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Response: {response.text}")
    print("-" * 50)
    return response.status_code == 200

if __name__ == '__main__':
    print("Starting Logistics Recommendations and Alerts Tests")
    print("=" * 60)

    access_token = login_admin()
    if access_token:
        test_generate_recommendations(access_token)
        test_generate_alerts(access_token)
    else:
        print("Admin login failed")
