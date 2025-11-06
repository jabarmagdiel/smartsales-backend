import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api/v1'

def login_user(username, password):
    url = f'{BASE_URL}/token/'
    data = {'username': username, 'password': password}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json().get('access'), response.json().get('refresh')
    return None, None

def test_admin_permissions():
    print("=== Testing ADMIN Permissions ===")
    access_token, refresh_token = login_user('admin2', 'admin123')
    if not access_token:
        print("Failed to login as admin")
        return

    headers = {'Authorization': f'Bearer {access_token}'}

    # Test product creation (should succeed)
    url = f'{BASE_URL}/productos/'
    data = {'name': 'Admin Product', 'description': 'Created by admin', 'price': 50.0, 'stock': 200, 'category': 'Test Category', 'sku': 'ADMIN001'}
    response = requests.post(url, json=data, headers=headers)
    print(f"Admin Product Creation: {response.status_code} - {response.json() if response.content else 'No content'}")

    # Test user management (should succeed)
    url = f'{BASE_URL}/usuarios/'
    response = requests.get(url, headers=headers)
    print(f"Admin User Management: {response.status_code} - {len(response.json()) if response.status_code == 200 else 'Failed'}")

def test_operator_permissions():
    print("\n=== Testing OPERATOR Permissions ===")
    access_token, refresh_token = login_user('operator', 'operator123')
    if not access_token:
        print("Failed to login as operator")
        return

    headers = {'Authorization': f'Bearer {access_token}'}

    # Test inventory movement (should succeed)
    url = f'{BASE_URL}/movimientos-inventario/'
    data = {'product': 1, 'movement_type': 'IN', 'quantity': 10, 'reason': 'Operator test'}
    response = requests.post(url, json=data, headers=headers)
    print(f"Operator Inventory Movement: {response.status_code} - {response.json() if response.content else 'No content'}")

    # Test product creation (should fail)
    url = f'{BASE_URL}/productos/'
    data = {'name': 'Operator Product', 'description': 'Should fail', 'price': 30.0, 'stock': 100, 'category': 'Test Category', 'sku': 'OP001'}
    response = requests.post(url, json=data, headers=headers)
    print(f"Operator Product Creation (should fail): {response.status_code} - {response.json() if response.content else 'No content'}")

def test_client_permissions():
    print("\n=== Testing CLIENT Permissions ===")
    access_token, refresh_token = login_user('testuser', 'testpass123')
    if not access_token:
        print("Failed to login as client")
        return

    headers = {'Authorization': f'Bearer {access_token}'}

    # Test cart operations (should succeed)
    url = f'{BASE_URL}/carrito/add_item/'
    data = {'product': 1, 'quantity': 1}
    response = requests.post(url, json=data, headers=headers)
    print(f"Client Cart Add Item: {response.status_code} - {response.json() if response.content else 'No content'}")

    # Test product creation (should fail)
    url = f'{BASE_URL}/productos/'
    data = {'name': 'Client Product', 'description': 'Should fail', 'price': 20.0, 'stock': 50, 'category': 'Test Category', 'sku': 'CLIENT001'}
    response = requests.post(url, json=data, headers=headers)
    print(f"Client Product Creation (should fail): {response.status_code} - {response.json() if response.content else 'No content'}")

    # Test user management (should fail)
    url = f'{BASE_URL}/usuarios/'
    response = requests.get(url, headers=headers)
    print(f"Client User Management (should fail): {response.status_code} - {response.json() if response.content else 'No content'}")

def test_logout():
    print("\n=== Testing LOGOUT ===")
    access_token, refresh_token = login_user('testuser', 'testpass123')
    if not access_token or not refresh_token:
        print("Failed to login for logout test")
        return

    # Test logout
    url = f'{BASE_URL}/logout/'
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {'refresh': refresh_token}
    response = requests.post(url, json=data, headers=headers)
    print(f"Logout: {response.status_code} - {response.json() if response.content else 'No content'}")

    # Try to use the token after logout (should fail)
    url = f'{BASE_URL}/carrito/'
    response = requests.get(url, headers=headers)
    print(f"Access after logout (should fail): {response.status_code} - {response.json() if response.content else 'No content'}")

if __name__ == '__main__':
    print("Starting Role-Based Permission Tests")
    print("=" * 60)

    test_admin_permissions()
    test_operator_permissions()
    test_client_permissions()
    test_logout()

    print("\n" + "=" * 60)
    print("Role-based permission tests completed!")
