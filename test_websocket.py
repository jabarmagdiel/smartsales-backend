import asyncio
import websockets
import json
import requests

async def test_websocket():
    uri = "ws://127.0.0.1:8001/ws/orders/"
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket connection established")

            # Simulate order creation to trigger WebSocket message
            # First, login and create an order
            login_response = requests.post('http://127.0.0.1:8000/api/v1/token/', json={
                'username': 'testuser',
                'password': 'testpass123'
            })
            if login_response.status_code == 200:
                token = login_response.json()['access']
                headers = {'Authorization': f'Bearer {token}'}

                # Add item to cart
                requests.post('http://127.0.0.1:8000/api/v1/carrito/add_item/', json={
                    'product': 1, 'quantity': 1
                }, headers=headers)

                # Checkout
                checkout_response = requests.post('http://127.0.0.1:8000/api/v1/checkout/', json={
                    'shipping_address': 'Test Address',
                    'shipping_method': 'standard'
                }, headers=headers)

                if checkout_response.status_code == 200:
                    order_id = checkout_response.json()['id']
                    print(f"Order created: {order_id}")

            # Listen for messages
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(message)
                print(f"Received: {data}")
                if data.get('type') == 'order_created':
                    print("Order creation notification received successfully!")
                else:
                    print("Unexpected message type received")
            except asyncio.TimeoutError:
                print("No message received within timeout")
    except Exception as e:
        print(f"WebSocket test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
