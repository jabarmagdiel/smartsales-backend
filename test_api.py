import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api/v1'

def test_registration():
    url = f'{BASE_URL}/registro/'
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    response = requests.post(url, json=data)
    print(f"Registration Test:")
    print(f"Command: POST {url}")
    print(f"Data: {json.dumps(data)}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json() if response.content else 'No content'}")
    print("-" * 50)
    return response

def test_login():
    url = f'{BASE_URL}/token/'
    data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    response = requests.post(url, json=data)
    print(f"Login Test:")
    print(f"Command: POST {url}")
    print(f"Data: {json.dumps(data)}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json() if response.content else 'No content'}")
    print("-" * 50)
    if response.status_code == 200:
        return response.json().get('access')
    return None

def test_create_product(access_token):
    url = f'{BASE_URL}/productos/'
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        'name': 'Test Product',
        'description': 'A test product',
        'price': 10.00,
        'stock': 100,
        'category': 'Test Category',  # Use category name
        'sku': 'TEST004'  # Add required SKU
    }
    response = requests.post(url, json=data, headers=headers)
    print(f"Create Product Test:")
    print(f"Command: POST {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data)}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json() if response.content else 'No content'}")
    print("-" * 50)
    if response.status_code == 201:
        return response.json().get('id')
    return None

def test_inventory_in(access_token, product_id):
    url = f'{BASE_URL}/movimientos-inventario/'
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        'product': product_id,
        'movement_type': 'IN',
        'quantity': 50,
        'reason': 'Stock entry test'
    }
    response = requests.post(url, json=data, headers=headers)
    print(f"Inventory IN Test:")
    print(f"Command: POST {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data)}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json() if response.content else 'No content'}")
    print("-" * 50)

def test_inventory_out(access_token, product_id):
    url = f'{BASE_URL}/movimientos-inventario/'
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        'product': product_id,
        'movement_type': 'OUT',
        'quantity': 10,
        'reason': 'Stock sale test'
    }
    response = requests.post(url, json=data, headers=headers)
    print(f"Inventory OUT Test:")
    print(f"Command: POST {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data)}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json() if response.content else 'No content'}")
    print("-" * 50)

def test_add_to_cart(access_token, product_id):
    url = f'{BASE_URL}/carrito/add_item/'
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        'product': product_id,
        'quantity': 2
    }
    response = requests.post(url, json=data, headers=headers)
    print(f"Add to Cart Test:")
    print(f"Command: POST {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data)}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Response: {response.text}")
    print("-" * 50)

def test_checkout(access_token):
    url = f'{BASE_URL}/checkout/'
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        'shipping_address': '123 Test St, Test City',
        'shipping_method': 'standard'
    }
    response = requests.post(url, json=data, headers=headers)
    print(f"Checkout Test:")
    print(f"Command: POST {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data)}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json() if response.content else 'No content'}")
    print("-" * 50)
    if response.status_code == 200:
        return response.json().get('id')
    return None

def test_payment(access_token, order_id):
    url = f'{BASE_URL}/pago/'
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        'order_id': order_id,
        'simulate_success': True
    }
    response = requests.post(url, json=data, headers=headers)
    print(f"Payment Test:")
    print(f"Command: POST {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data)}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json() if response.content else 'No content'}")
    print("-" * 50)

if __name__ == '__main__':
    print("Starting API Tests for backend_salessmart")
    print("=" * 60)

    # Test registration
    reg_response = test_registration()

    # Test login
    access_token = test_login()

    if access_token:
        # Test create product (may fail if not admin)
        product_id = test_create_product(access_token)

        if product_id:
            # Test inventory movements
            test_inventory_in(access_token, product_id)
            test_inventory_out(access_token, product_id)

            # Test cart and checkout
            test_add_to_cart(access_token, product_id)
            order_id = test_checkout(access_token)

            if order_id:
                test_payment(access_token, order_id)
        else:
            print("Product creation failed, skipping dependent tests")
    else:
        print("Login failed, skipping authenticated tests")
