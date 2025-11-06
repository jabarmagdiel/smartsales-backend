from rest_framework import viewsets
from .models import LogEntry
from .serializers import LogEntrySerializer
from permissions import IsAdmin

class LogEntryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LogEntry.objects.all().order_by('-timestamp')
    serializer_class = LogEntrySerializer
    permission_classes = [IsAdmin]
