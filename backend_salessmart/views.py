from django.http import JsonResponse
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from permissions import IsAdmin

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def backup_database(request):
    """
    Simulate PostgreSQL database backup
    In production, this would use pg_dump or similar tools
    """
    try:
        # Get database connection info
        db_settings = connection.settings_dict

        # Simulate backup process
        backup_info = {
            'database': db_settings['NAME'],
            'host': db_settings['HOST'],
            'port': db_settings['PORT'],
            'backup_type': 'full_backup',
            'timestamp': '2024-01-01T12:00:00Z',
            'status': 'success',
            'file_size': '150MB',
            'message': 'Database backup completed successfully'
        }

        return Response({
            'backup': backup_info,
            'note': 'This is a simulation. In production, implement actual pg_dump backup.'
        })

    except Exception as e:
        return Response({
            'error': str(e),
            'status': 'failed'
        }, status=500)

def root_view(request):
    """
    Root endpoint that returns a simple status message.
    """
    return JsonResponse({
        "status": "SmartSales Backend is running",
        "version": "v1",
        "endpoints": {
            "products": "/api/v1/products/",
            "users": "/api/v1/users/",
            "sales": "/api/v1/sales/",
            "logistics": "/api/v1/logistics/",
            "posventa": "/api/v1/posventa/",
            "logs": "/api/v1/logs/",
            "reportes": "/api/v1/reportes/",
            "ia": "/api/v1/ia/",
            "admin": {
                "backup": "/admin/backup/"
            }
        }
    })
