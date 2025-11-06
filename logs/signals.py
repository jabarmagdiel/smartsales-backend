from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import LogEntry

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    log_entry = LogEntry(
        user=user,
        action=f"LOGIN exitoso. Rol: {user.role}.",
    )
    log_entry.get_client_ip(request)
    log_entry.save()
