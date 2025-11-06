# TODO: Registro Exhaustivo de Todos los Modelos en el Panel Admin

## Ciclo 1: Modelos Principales
- [x] Registrar modelos en users/admin.py: User
- [x] Registrar modelos en products/admin.py: Category, Product, Price, AtributoProducto, InventoryMovement
- [x] Registrar modelos en sales/admin.py: Cart, CartItem, Order, OrderItem, Payment
- [x] Registrar modelos en posventa/admin.py: Return, Warranty

## Ciclo 2: Modelos de Logs y Reportes
- [x] Registrar modelos en logs/admin.py: LogEntry
- [x] Registrar modelos en reportes/admin.py: ReporteDinamico

## Ciclo 3: Modelos de IA
- [x] Registrar modelos en ia/admin.py: ModeloConfiguracion, HistoricalSale, TrainingSession
- [x] Registrar modelos en logistics/admin.py: Alert, Recommendation

## Verificación Final
- [x] Reiniciar el servidor con `python manage.py runserver`
- [x] Acceder al panel de administración en /admin/ y verificar que todas las secciones de los 3 Ciclos sean visibles
- [x] Probar login como admin y revisar las vistas de lista de cada modelo
