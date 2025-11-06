# Documentación: Lógica de Reportes Dinámicos (Parte 2)

## Patrones de Reglas y Expresiones Regulares

### Expresiones Regulares Utilizadas
- **DATE_PATTERN**: `r'\b(\d{1,2}/\d{1,2}/\d{4})\b'` - Busca fechas en formato dd/mm/yyyy.
- **FIELD_MAPPINGS**: Diccionario que mapea términos comunes a campos del modelo:
  - 'nombre del cliente' -> 'user__username'
  - 'monto total pagado' -> 'total'
  - 'fecha de orden' -> 'created_at'
  - 'estado' -> 'status'
  - 'método de pago' -> 'payment__method'
  - etc.

### Reglas de Filtrado
- **Palabras clave para filtros**: 'filtrar', 'donde', 'con', 'desde', 'hasta', 'entre'
- **Filtros específicos**:
  - 'pagado' -> status = 'PAID'
  - 'paypal' -> payment_method = 'PAYPAL'
  - 'stripe' -> payment_method = 'STRIPE'
  - Rango de fechas: Detecta dos fechas y las aplica como filtro de rango en created_at

### Reglas de Formato de Salida
- **Palabras clave**: 'formato', 'salida', 'exportar'
- **Formatos soportados**:
  - 'pdf' -> 'pdf'
  - 'excel' o 'xlsx' -> 'excel'
  - Default: 'json'

## Construcción de Consulta: Ejemplo de Traducción

### Prompt de Ejemplo
"Mostrar nombre del cliente, monto total pagado del 01/10/2024 al 01/01/2025 en formato PDF"

### Proceso de Parsing
1. **Campos extraídos**: ['user__username', 'total']
2. **Filtros aplicados**:
   - date_range: (2024-10-01, 2025-01-01)
   - status: 'PAID'
3. **Formato**: 'pdf'

### Consulta ORM Resultante
```python
Order.objects.select_related('user', 'payment').prefetch_related('items__product').filter(
    Q(created_at__date__range=('2024-10-01', '2025-01-01')) &
    Q(status='PAID')
).values('user__username', 'total')
```

### Flujo de Interpretación
1. **Tokenización**: Divide el prompt en palabras y busca patrones.
2. **Mapeo de Campos**: Busca términos en FIELD_MAPPINGS para identificar columnas.
3. **Extracción de Filtros**: Aplica regex para fechas y reglas para otros filtros.
4. **Determinación de Formato**: Busca palabras clave de formato.
5. **Construcción de Query**: Traduce elementos parseados a Q objects y filtros de Django ORM.
6. **Ejecución**: Ejecuta la query y limita resultados a 100 para preview.
7. **Almacenamiento**: Guarda el prompt original y la representación de la query en ReporteDinamico.

Esta lógica permite a los usuarios generar reportes dinámicos mediante lenguaje natural, traduciendo prompts a consultas eficientes del ORM de Django.
