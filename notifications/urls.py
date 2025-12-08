from django.urls import path
from .views import FCMTokenView, delete_fcm_token, NotificationLogListView

urlpatterns = [
    path('fcm-token/', FCMTokenView.as_view(), name='fcm-token'),
    path('fcm-token/<str:token>/', delete_fcm_token, name='delete-fcm-token'),
    path('notifications/', NotificationLogListView.as_view(), name='notification-log'),
]
