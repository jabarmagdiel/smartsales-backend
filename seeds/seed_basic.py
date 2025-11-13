from products.models import Category, Product

cats = [
    ("Electrónica", ""),
    ("Hogar", ""),
    ("Ropa", ""),
]
created = {}
for name, desc in cats:
    c, _ = Category.objects.get_or_create(name=name, defaults={"description": desc})
    created[name] = c

products = [
    ("Laptop Pro", "Alta gama", created["Electrónica"], "SKU-LAP-001", 25, 5, 1499.99),
    ("Auriculares BT", "Con cancelación", created["Electrónica"], "SKU-AUD-002", 120, 10, 89.90),
    ("TV 55\" 4K", "Smart TV", created["Electrónica"], "SKU-TV-003", 40, 5, 599.00),
    ("Sartén Antiadherente", "28cm", created["Hogar"], "SKU-SAR-004", 80, 10, 24.50),
    ("Cafetera", "Goteo 1.5L", created["Hogar"], "SKU-CAF-005", 35, 5, 39.99),
    ("Zapatillas Runner", "Talla 42", created["Ropa"], "SKU-ZAP-006", 60, 8, 74.99),
    ("Camisa Casual", "Talla M", created["Ropa"], "SKU-CAM-007", 50, 6, 29.90),
    ("Aspiradora", "1200W", created["Hogar"], "SKU-ASP-008", 22, 4, 129.00),
    ("Tablet 10\"", "64GB", created["Electrónica"], "SKU-TAB-009", 30, 5, 229.00),
    ("Monitor 27\"", "144Hz", created["Electrónica"], "SKU-MON-010", 18, 3, 219.00),
]

for name, desc, cat, sku, stock, min_stock, price in products:
    Product.objects.get_or_create(
        sku=sku,
        defaults={
            "name": name,
            "description": desc,
            "category": cat,
            "stock": stock,
            "min_stock": min_stock,
            "price": price,
        },
    )

print("SEEDED_BASIC_OK")
