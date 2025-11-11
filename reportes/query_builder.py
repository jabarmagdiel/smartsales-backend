import re
# --- CORRECCIÓN 1: Necesitamos 'datetime' para saber el año actual ---
from datetime import datetime
from django.db.models import Q, Sum, Count
from sales.models import Order, Payment

# Mapeo de meses en español a números
MONTH_MAP = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}
# Regex más flexible (prefijo opcional)
MONTH_REGEX = r'\b(de|en|del)?\s*(' + '|'.join(MONTH_MAP.keys()) + r')\b'
YEAR_REGEX = r'\b(del|año)?\s*(\d{4})\b'

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

    # --- LÓGICA DE FILTROS MEJORADA ---
    filters = {}
    
    # 1. Buscar fechas específicas (dd/mm/yyyy)
    dates = re.findall(DATE_PATTERN, prompt)
    if len(dates) >= 2:
        try:
            start_date = datetime.strptime(dates[0], '%d/%m/%Y').date()
            end_date = datetime.strptime(dates[1], '%d/%m/%Y').date()
            filters['date_range'] = (start_date, end_date)
        except ValueError:
            pass # Formato de fecha inválido
    elif len(dates) == 1:
        try:
            date = datetime.strptime(dates[0], '%d/%m/%Y').date()
            filters['date'] = date
        except ValueError:
            pass # Formato de fecha inválido

    # 2. Buscar Meses (ej. "ventas de octubre")
    month_match = re.search(MONTH_REGEX, prompt_lower)
    if month_match:
        month_name = month_match.group(2) 
        filters['month'] = MONTH_MAP[month_name]

    # 3. Buscar Años (ej. "ventas del 2025")
    year_match = re.search(YEAR_REGEX, prompt_lower)
    if year_match:
        filters['year'] = int(year_match.group(2))
    # --- CORRECCIÓN 2: AÑO POR DEFECTO ---
    # Si el usuario pidió un mes, PERO NO un año,
    # debemos asumir el año actual.
    elif month_match and not year_match:
        # (Si el prompt fue "noviembre" pero no "2025")
        filters['year'] = datetime.now().year
    # --- FIN DE LA CORRECCIÓN ---


    # 4. Buscar otros filtros (ej: estado, método)
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
        'fields': fields or ['user__username', 'total', 'created_at'],
        'filters': filters,
        'format': output_format
    }

def build_query(parsed_data):
    """
    Construye la consulta ORM basada en los datos parseados.
    """
    fields = parsed_data['fields']
    filters = parsed_data['filters']

    # Base query (Esta es correcta, usa 'sales.models' como confirmamos)
    queryset = Order.objects.select_related('user', 'payment').prefetch_related('items__product')

    # Aplicación de filtros (Ahora incluye el 'year' por defecto)
    q_filters = Q()
    
    if 'date_range' in filters:
        start, end = filters['date_range']
        q_filters &= Q(created_at__date__range=(start, end))
    elif 'date' in filters:
        q_filters &= Q(created_at__date=filters['date'])
    
    if 'month' in filters:
        q_filters &= Q(created_at__month=filters['month'])
    
    if 'year' in filters:
        q_filters &= Q(created_at__year=filters['year'])
        
    if 'status' in filters:
        q_filters &= Q(status=filters['status'])
    if 'payment_method' in filters:
        q_filters &= Q(payment__method=filters['payment_method'])

    queryset = queryset.filter(q_filters)

    # Lógica de Select Fields (Restaurada y correcta)
    select_fields = []
    fields_to_process = fields or ['user__username', 'total', 'created_at']

    for field in fields_to_process:
        if '__' in field:
            parts = field.split('__')
            if len(parts) == 2:
                select_fields.append(f'{parts[0]}__{parts[1]}')
        else:
            select_fields.append(field)

    return queryset, select_fields
