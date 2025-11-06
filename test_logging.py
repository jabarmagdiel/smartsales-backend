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

def test_log_endpoint_access():
    print("=== Testing Log Endpoint Access Control ===")

    # Test as CLIENT (should fail)
    print("\n1. Testing CLIENT access (should be 403 Forbidden):")
    access_token, _ = login_user('testuser', 'testpass123')
    if access_token:
        headers = {'Authorization': f'Bearer {access_token}'}
        url = f'{BASE_URL}/log/'
        response = requests.get(url, headers=headers)
        print(f"CLIENT Log Access: {response.status_code} - {response.text if response.content else 'No content'}")
    else:
        print("Failed to login as client")

    # Test as OPERATOR (should fail)
    print("\n2. Testing OPERATOR access (should be 403 Forbidden):")
    access_token, _ = login_user('operator', 'operator123')
    if access_token:
        headers = {'Authorization': f'Bearer {access_token}'}
        url = f'{BASE_URL}/log/'
        response = requests.get(url, headers=headers)
        print(f"OPERATOR Log Access: {response.status_code} - {response.text if response.content else 'No content'}")
    else:
        print("Failed to login as operator")

    # Test as ADMIN (should succeed)
    print("\n3. Testing ADMIN access (should be 200 OK):")
    access_token, _ = login_user('admin2', 'admin123')
    if access_token:
        headers = {'Authorization': f'Bearer {access_token}'}
        url = f'{BASE_URL}/log/'
        response = requests.get(url, headers=headers)
        print(f"ADMIN Log Access: {response.status_code}")
        if response.status_code == 200:
            logs = response.json()
            # Handle paginated response
            if isinstance(logs, dict) and 'results' in logs:
                log_list = logs['results']
            else:
                log_list = logs
            print(f"Number of log entries: {len(log_list)}")
            if len(log_list) > 0:
                print("Sample log entry:")
                print(json.dumps(log_list[0], indent=2))
            else:
                print("No log entries found.")
        else:
            print(f"Response: {response.text if response.content else 'No content'}")
        return access_token
    else:
        print("Failed to login as admin")
        return None

def test_middleware_logging(admin_token):
    print("\n=== Testing Middleware Logging ===")

    headers = {'Authorization': f'Bearer {admin_token}'}

    # Test POST (Create Product) by Admin
    print("\n1. Testing POST (Create Product) logging:")
    url = f'{BASE_URL}/productos/'
    import time
    sku = f'LOG{int(time.time())}'  # Unique SKU
    data = {
        'name': 'Logged Product',
        'description': 'Product created for logging test',
        'price': 25.50,
        'stock': 150,
        'category': 'Test Category',
        'sku': sku
    }
    response = requests.post(url, json=data, headers=headers)
    print(f"Create Product: {response.status_code} - {response.json() if response.content else 'No content'}")

    # Test PUT (Update Stock) by Operator
    print("\n2. Testing PUT (Update Stock) logging:")
    # First login as operator
    op_token, _ = login_user('operator', 'operator123')
    if op_token:
        op_headers = {'Authorization': f'Bearer {op_token}'}
        # Get first product ID
        products_url = f'{BASE_URL}/productos/'
        products_response = requests.get(products_url, headers=op_headers)
        if products_response.status_code == 200 and products_response.json():
            product_id = products_response.json()[0]['id']
            # Update stock via inventory movement
            inv_url = f'{BASE_URL}/movimientos-inventario/'
            inv_data = {
                'product': product_id,
                'movement_type': 'IN',
                'quantity': 20,
                'reason': 'Stock update test'
            }
            inv_response = requests.post(inv_url, json=inv_data, headers=op_headers)
            print(f"Inventory Movement (PUT equivalent): {inv_response.status_code} - {inv_response.json() if inv_response.content else 'No content'}")
        else:
            print("Failed to get products for operator test")
    else:
        print("Failed to login as operator")

def check_logs_after_actions(admin_token):
    print("\n=== Checking Log Entries After Actions ===")

    headers = {'Authorization': f'Bearer {admin_token}'}
    url = f'{BASE_URL}/log/'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        logs = response.json()
        # Handle paginated response
        if isinstance(logs, dict) and 'results' in logs:
            log_list = logs['results']
        else:
            log_list = logs
        print(f"Total log entries: {len(log_list)}")

        # Show recent entries
        recent_logs = log_list[:5]  # Last 5 entries
        print("\nRecent log entries:")
        for i, log in enumerate(recent_logs, 1):
            print(f"{i}. {log['timestamp']} - {log['user_username']} - {log['action']} - IP: {log['ip_address']}")
    else:
        print(f"Failed to retrieve logs: {response.status_code} - {response.text if response.content else 'No content'}")

if __name__ == '__main__':
    print("Starting Logging Functionality Tests")
    print("=" * 60)

    # Test endpoint access control
    admin_token = test_log_endpoint_access()

    if admin_token:
        # Test middleware logging
        test_middleware_logging(admin_token)

        # Check logs after actions
        check_logs_after_actions(admin_token)

    print("\n" + "=" * 60)
    print("Logging tests completed!")
