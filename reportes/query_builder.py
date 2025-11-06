import re
from datetime import datetime
from django.db.models import Q, Sum, Count
from sales.models import Order, Payment

# Diccionarios para mapear términos comunes a campos del modelo
FIELD_MAPPINGS = {
    'nombre del cliente': 'user__username',
    'monto total pagado': 'total',
    'fecha de orden': 'created_at',
    'estado': 'status',
    'método de pago': 'payment__method',
    'cantidad': 'items__quantity',
    'producto': 'items__product__name',
    'precio': 'items__price',
}

FILTER_KEYWORDS = ['filtrar', 'donde', 'con', 'desde', 'hasta', 'entre']
FORMAT_KEYWORDS = ['formato', 'salida', 'exportar']
DATE_PATTERN = r'\b(\d{1,2}/\d{1,2}/\d{4})\b'

def parse_prompt(prompt):
    """
    Parsea el prompt para extraer campos, filtros y formato.
    Retorna un diccionario con 'fields', 'filters', 'format'.
    """
    prompt_lower = prompt.lower()

    # Extraer campos a mostrar
    fields = []
    for key, field in FIELD_MAPPINGS.items():
        if key in prompt_lower:
            fields.append(field)

    # Extraer filtros
    filters = {}
    # Buscar fechas
    dates = re.findall(DATE_PATTERN, prompt)
    if len(dates) >= 2:
        start_date = datetime.strptime(dates[0], '%d/%m/%Y').date()
        end_date = datetime.strptime(dates[1], '%d/%m/%Y').date()
        filters['date_range'] = (start_date, end_date)
    elif len(dates) == 1:
        # Si solo una fecha, asumir filtro por día
        date = datetime.strptime(dates[0], '%d/%m/%Y').date()
        filters['date'] = date

    # Buscar otros filtros (ej: estado, método)
    if 'pagado' in prompt_lower:
        filters['status'] = 'PAID'
    if 'paypal' in prompt_lower:
        filters['payment_method'] = 'PAYPAL'
    if 'stripe' in prompt_lower:
        filters['payment_method'] = 'STRIPE'

    # Extraer formato
    output_format = 'json'  # default
    if 'pdf' in prompt_lower:
        output_format = 'pdf'
    elif 'excel' in prompt_lower or 'xlsx' in prompt_lower:
        output_format = 'excel'

    return {
        'fields': fields or ['user__username', 'total', 'created_at'],  # default fields
        'filters': filters,
        'format': output_format
    }

def build_query(parsed_data):
    """
    Construye la consulta ORM basada en los datos parseados.
    """
    fields = parsed_data['fields']
    filters = parsed_data['filters']

    # Base query
    queryset = Order.objects.select_related('user', 'payment').prefetch_related('items__product')

    # Aplicar filtros
    q_filters = Q()
    if 'date_range' in filters:
        start, end = filters['date_range']
        q_filters &= Q(created_at__date__range=(start, end))
    if 'date' in filters:
        q_filters &= Q(created_at__date=filters['date'])
    if 'status' in filters:
        q_filters &= Q(status=filters['status'])
    if 'payment_method' in filters:
        q_filters &= Q(payment__method=filters['payment_method'])

    queryset = queryset.filter(q_filters)

    # Seleccionar campos
    select_fields = []
    for field in fields:
        if '__' in field:
            parts = field.split('__')
            if len(parts) == 2:
                select_fields.append(f'{parts[0]}__{parts[1]}')
        else:
            select_fields.append(field)

    # Para agregaciones si es necesario
    if 'total' in fields:
        queryset = queryset.annotate(total_sum=Sum('total'))

    return queryset, select_fields
