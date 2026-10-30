from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('items/', views.item_list, name='item_list'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),
    path('report/', views.report_item, name='report_item'),
    path('items/<int:pk>/edit/', views.edit_item, name='edit_item'),
    path('items/<int:pk>/delete/', views.delete_item, name='delete_item'),
    path('items/<int:item_pk>/claim/', views.submit_claim, name='submit_claim'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/claims/<int:pk>/review/', views.review_claim, name='review_claim'),
    path('admin-panel/items/<int:pk>/status/', views.admin_update_item_status, name='admin_update_item_status'),
]
