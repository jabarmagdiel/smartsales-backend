from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import LogEntry
from .serializers import LogEntrySerializer
from permissions import IsAdmin
from django.utils.dateparse import parse_date # Importar para las fechas
from django.http import HttpResponse
import csv
from io import BytesIO
import datetime

# Importaciones condicionales para reportes
try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from openpyxl import Workbook
    HAS_REPORT_LIBS = True
except ImportError:
    HAS_REPORT_LIBS = False
    SimpleDocTemplate = None
    Paragraph = None
    Spacer = None
    Table = None
    TableStyle = None
    getSampleStyleSheet = None
    letter = None
    A4 = None
    colors = None
    Workbook = None

class LogEntryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LogEntry.objects.all().order_by('-timestamp')
    serializer_class = LogEntrySerializer
    permission_classes = [IsAdmin]

    # --- (NUEVO) AÑADIDO PARA FILTROS (CU-Bitácora) ---
    def get_queryset(self):
        """
        Sobrescribimos este método para aplicar filtros de la URL.
        """
        # Empezamos con la consulta base
        queryset = LogEntry.objects.all().order_by('-timestamp')

        # Obtenemos los parámetros de la URL (ej: /log/?user=admin)
        user_param = self.request.query_params.get('user', None)
        start_date_param = self.request.query_params.get('start_date', None)
        end_date_param = self.request.query_params.get('end_date', None)
        action_param = self.request.query_params.get('action', None)

        # 1. Aplicar filtro de usuario (búsqueda parcial en username)
        if user_param:
            queryset = queryset.filter(user__username__icontains=user_param)

        # 2. Aplicar filtro de fecha de inicio (mayor o igual)
        if start_date_param:
            start_date = parse_date(start_date_param)
            if start_date:
                queryset = queryset.filter(timestamp__date__gte=start_date)

        # 3. Aplicar filtro de fecha de fin (menor o igual)
        if end_date_param:
            end_date = parse_date(end_date_param)
            if end_date:
                queryset = queryset.filter(timestamp__date__lte=end_date)
        
        # 4. Filtro por texto contenido en 'action'
        if action_param:
            queryset = queryset.filter(action__icontains=action_param)
                
        return queryset

    @action(detail=False, methods=['get'], url_path='export')
    def export(self, request):
        """
        Exporta la bitácora en CSV o PDF respetando los mismos filtros.
        /api/v1/admin/logs/export/?format=csv|pdf&user=&action=&start_date=&end_date=
        """
        fmt = request.query_params.get('format', 'csv').lower()
        logs_qs = self.get_queryset()
        # Registrar en bitácora la exportación
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip:
                ip = ip.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            LogEntry.objects.create(
                ip_address=ip or 'IP_UNKNOWN',
                user=request.user,
                action=f"Logs exportados formato={fmt} filtros={{user:{request.query_params.get('user','')}, action:{request.query_params.get('action','')}, start:{request.query_params.get('start_date','')}, end:{request.query_params.get('end_date','')}}}"
            )
        except Exception:
            pass

        if fmt == 'csv':
            try:
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="bitacora.csv"'
                writer = csv.writer(response)
                writer.writerow(['timestamp', 'usuario', 'ip', 'accion'])
                for l in logs_qs:
                    writer.writerow([
                        l.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        (l.user.username if l.user else ''),
                        l.ip_address,
                        l.action,
                    ])
                return response
            except Exception as e:
                return Response({'detail': 'Error generando CSV', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        elif fmt == 'xlsx':
            if not HAS_REPORT_LIBS or not Workbook:
                return Response({
                    'detail': 'Excel export not available',
                    'error': 'openpyxl library is required for Excel exports'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            try:
                wb = Workbook()
                ws = wb.active
                ws.title = "Bitácora del Sistema"
                
                # Headers
                headers = ['Fecha', 'Usuario', 'IP', 'Acción']
                ws.append(headers)
                
                # Data
                for log in logs_qs:
                    ws.append([
                        log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        log.user.username if log.user else '-',
                        log.ip_address,
                        log.action
                    ])
                
                # Save to buffer
                excel_buffer = BytesIO()
                wb.save(excel_buffer)
                excel_buffer.seek(0)
                
                response = HttpResponse(
                    excel_buffer.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="bitacora_{datetime.datetime.now().strftime("%Y%m%d")}.xlsx"'
                return response
            except Exception as e:
                return Response({'detail': 'Error generando Excel', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        elif fmt == 'pdf':
            if not HAS_REPORT_LIBS or not SimpleDocTemplate:
                return Response({
                    'detail': 'PDF export not available',
                    'error': 'reportlab library is required for PDF exports'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            try:
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4)
                styles = getSampleStyleSheet()
                elements = []

                # Title
                title = Paragraph('Bitácora del Sistema SmartSales', styles['Title'])
                elements.append(title)
                elements.append(Spacer(1, 12))
                
                # Info
                info = Paragraph(f'Generado el: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', styles['Normal'])
                elements.append(info)
                elements.append(Spacer(1, 12))

                # Table data
                data = [['Fecha', 'Usuario', 'IP', 'Acción']]
                for log in logs_qs[:1000]:  # Limit for PDF
                    data.append([
                        log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        log.user.username if log.user else '-',
                        log.ip_address,
                        log.action[:50] + '...' if len(log.action) > 50 else log.action
                    ])

                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                elements.append(table)

                doc.build(elements)
                pdf_content = buffer.getvalue()
                buffer.close()

                response = HttpResponse(pdf_content, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="bitacora_{datetime.datetime.now().strftime("%Y%m%d")}.pdf"'
                return response
            except Exception as e:
                return Response({'detail': 'Error generando PDF', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Formato no soportado. Use: csv, xlsx, pdf'}, status=status.HTTP_400_BAD_REQUEST)

