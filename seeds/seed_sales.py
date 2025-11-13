from decimal import Decimal
from datetime import datetime, timedelta, date
import random

from django.contrib.auth import get_user_model
from products.models import Product
from sales.models import Order, OrderItem, Payment
from ia.models import HistoricalSale

User = get_user_model()

# 1) Ensure a demo client exists
client, _ = User.objects.get_or_create(
    username="cliente_demo",
    defaults={
        "email": "cliente@example.com",
        "role": "CLIENT",
        "is_active": True,
    },
)
# set a default password if newly created
client.set_password("123456")
client.save()

# 2) Create a few orders for the client if none exist
if not Order.objects.filter(user=client).exists():
    products = list(Product.objects.all()[:5])
    if products:
        for i in range(3):
            # pick 2 random products
            picks = random.sample(products, k=min(2, len(products)))
            total = Decimal("0.00")
            address = f"Av. Principal {100+i}, Ciudad"
            order = Order.objects.create(
                user=client,
                status="PAID",
                total=Decimal("0.00"),
                shipping_cost=Decimal("10.00"),
                address=address,
            )
            for p in picks:
                qty = random.randint(1, 3)
                OrderItem.objects.create(
                    order=order,
                    product=p,
                    quantity=qty,
                    price=p.price,
                )
                total += (p.price * qty)
            order.total = total
            order.save()

            Payment.objects.create(
                order=order,
                amount=order.total + order.shipping_cost,
                method=random.choice(["PAYPAL", "STRIPE"]),
                status="APPROVED",
                transaction_id=f"seed_txn_{order.id}"
            )

print("SEEDED_ORDERS_OK")

# 3) Generate simple historical sales for IA if empty
if not HistoricalSale.objects.exists():
    products = list(Product.objects.all()[:5])
    if products:
        start = date.today() - timedelta(days=60)
        for day in range(60):
            d = start + timedelta(days=day)
            for p in products:
                q = random.randint(1, 10)
                HistoricalSale.objects.create(date=d, product=p, quantity=q)
        print("SEEDED_IA_HISTORY_OK")
