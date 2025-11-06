from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'ADMIN'

class IsOperator(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ['ADMIN', 'OPERATOR']

class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ['ADMIN', 'OPERATOR', 'CLIENT']
