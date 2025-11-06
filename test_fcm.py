import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api/v1'

def login_client():
    url = f'{BASE_URL}/token/'
    data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json().get('access')
    return None

def add_to_cart(access_token):
    url = f'{BASE_URL}/carrito/add_item/'
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {'product': 1, 'quantity': 1}
    response = requests.post(url, json=data, headers=headers)
    return response.status_code == 200

def checkout(access_token):
    url = f'{BASE_URL}/checkout/'
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {'shipping_address': 'Test Address', 'shipping_method': 'standard'}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json().get('id')
    return None

def test_payment_fcm(access_token, order_id):
    url = f'{BASE_URL}/pago/'
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {'order_id': order_id, 'simulate_success': True}
    response = requests.post(url, json=data, headers=headers)
    print(f"FCM Payment Test:")
    print(f"Command: POST {url}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json() if response.content else 'No content'}")
    print("-" * 50)
    return response.status_code == 200

if __name__ == '__main__':
    print("Starting FCM Simulation Test")
    print("=" * 60)

    access_token = login_client()
    if access_token:
        if add_to_cart(access_token):
            order_id = checkout(access_token)
            if order_id:
                test_payment_fcm(access_token, order_id)
            else:
                print("Checkout failed")
        else:
            print("Add to cart failed")
    else:
        print("Client login failed")
