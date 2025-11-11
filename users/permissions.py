# users/permissions.py
from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Permiso personalizado para Administradores (Superusuarios y Staff).
    """
    def has_permission(self, request, view):
        # Soluciona el 403: Verifica que el usuario esté logueado Y sea staff/admin.
        return request.user and request.user.is_authenticated and request.user.is_staff

class IsOperator(permissions.BasePermission):
    """
    Permiso para Operadores.
    """
    def has_permission(self, request, view):
        # El usuario debe estar logueado Y (ser OPERATOR O ser Admin/Staff)
        is_operator = (request.user.role == 'OPERATOR')
        return request.user and request.user.is_authenticated and (is_operator or request.user.is_staff)

class IsCliente(permissions.BasePermission):
    """
    Permiso para Clientes.
    """
    def has_permission(self, request, view):
        is_cliente = (request.user.role == 'CLIENT')
        return request.user and request.user.is_authenticated and is_cliente