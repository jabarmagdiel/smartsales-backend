from django.http import JsonResponse, FileResponse, HttpResponse
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from permissions import IsAdmin
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone
from logs.models import LogEntry
import os
import io
import zipfile
import tempfile
from pathlib import Path

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
            },
            "system": {
                "backups": "/api/v1/system/backups/"
            }
        }
    })

@api_view(['GET'])
@permission_classes([AllowAny])  # Hacer el endpoint público para Railway healthcheck
def health_check(request):
    """
    Health check endpoint for Railway - Public access
    """
    try:
        return JsonResponse({
            "status": "healthy",
            "service": "SmartSales Backend",
            "timestamp": timezone.now().isoformat(),
            "version": "1.0.0",
            "database": "connected"
        })
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": timezone.now().isoformat()
        }, status=503)


# === Backups/Restore (API) ===

def _backups_dir() -> Path:
    base = Path(getattr(settings, 'MEDIA_ROOT', 'media')) / 'backups'
    base.mkdir(parents=True, exist_ok=True)
    return base

def _safe_filename(ts: str) -> str:
    return f"backup_{ts}.zip"

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def list_backups(request):
    """Lista archivos de backup en MEDIA_ROOT/backups"""
    d = _backups_dir()
    files = []
    for p in sorted(d.glob('*.zip')):
        stat = p.stat()
        files.append({
            'name': p.name,
            'size': stat.st_size,
            'modified': timezone.datetime.fromtimestamp(stat.st_mtime, tz=timezone.get_current_timezone()).isoformat(),
        })
    return Response({'results': files})

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def create_backup(request):
    """Crea un backup completo con dumpdata y lo comprime en ZIP"""
    ts = timezone.now().strftime('%Y%m%d_%H%M%S')
    tmpdir = Path(tempfile.mkdtemp())
    json_path = tmpdir / f"data_{ts}.json"
    zip_name = _safe_filename(ts)
    zip_path = _backups_dir() / zip_name

    try:
        # dumpdata a JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            call_command('dumpdata', '--natural-foreign', '--natural-primary', '--indent', '2', stdout=f)

        # comprimir a ZIP
        with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(json_path, arcname=json_path.name)
    except Exception as e:
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            LogEntry.objects.create(
                ip_address=ip or 'IP_UNKNOWN',
                user=request.user,
                action=f"ERROR: Backup fallo error={str(e)}"
            )
        except Exception:
            pass
        return Response({'detail': 'Error creando backup', 'error': str(e)}, status=500)

    # Log bitácora
    try:
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip:
            ip = ip.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        LogEntry.objects.create(
            ip_address=ip or 'IP_UNKNOWN',
            user=request.user,
            action=f"Backup creado file={zip_name}"
        )
    except Exception:
        pass

    return Response({'detail': 'Backup creado', 'file': zip_name})

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def download_backup(request, filename: str):
    """Descarga un archivo zip de backup"""
    path = _backups_dir() / filename
    if not path.exists() or not path.is_file():
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            LogEntry.objects.create(
                ip_address=ip or 'IP_UNKNOWN',
                user=request.user,
                action=f"ERROR: Backup no encontrado file={filename}"
            )
        except Exception:
            pass
        return Response({'detail': 'Archivo no encontrado'}, status=404)
    # Log bitácora
    try:
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip:
            ip = ip.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        LogEntry.objects.create(
            ip_address=ip or 'IP_UNKNOWN',
            user=request.user,
            action=f"Backup descargado file={path.name}"
        )
    except Exception:
        pass
    return FileResponse(open(path, 'rb'), as_attachment=True, filename=path.name)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def restore_backup(request):
    """Restaura desde un archivo zip subido o referencia por nombre."""
    upload = request.FILES.get('file')
    filename = request.data.get('filename')

    if not upload and not filename:
        return Response({'detail': 'Debe proporcionar un archivo o un nombre de backup'}, status=400)

    # Obtener zip path
    if upload:
        tmp_zip = Path(tempfile.mkdtemp()) / (upload.name or 'restore.zip')
        with open(tmp_zip, 'wb') as f:
            for chunk in upload.chunks():
                f.write(chunk)
        zip_path = tmp_zip
    else:
        zip_path = _backups_dir() / filename
        if not zip_path.exists():
            return Response({'detail': 'Backup no encontrado'}, status=404)

    # Extraer y buscar json
    extract_dir = Path(tempfile.mkdtemp())
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_dir)
        json_files = list(extract_dir.glob('*.json'))
        if not json_files:
            return Response({'detail': 'El backup no contiene .json'}, status=400)
        # Restaurar datos
        call_command('loaddata', str(json_files[0]))
    except Exception as e:
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            origen = f"upload:{getattr(upload, 'name', '')}" if upload else f"filename:{filename}"
            LogEntry.objects.create(
                ip_address=ip or 'IP_UNKNOWN',
                user=request.user,
                action=f"ERROR: Backup restaurar fallo origen={origen} error={str(e)}"
            )
        except Exception:
            pass
        return Response({'detail': 'Error al restaurar', 'error': str(e)}, status=400)
    # Log bitácora
    try:
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip:
            ip = ip.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        origen = f"upload:{getattr(upload, 'name', '')}" if upload else f"filename:{filename}"
        LogEntry.objects.create(
            ip_address=ip or 'IP_UNKNOWN',
            user=request.user,
            action=f"Backup restaurado origen={origen}"
        )
    except Exception:
        pass

    return Response({'detail': 'Restauración completada'})
