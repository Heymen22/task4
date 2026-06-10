from django.urls import path

from . import views

urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/purchase/', views.purchase_book, name='purchase_book'),
    path('books/<int:pk>/rent/', views.rent_book, name='rent_book'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/books/create/', views.admin_book_create, name='admin_book_create'),
    path('admin-panel/books/<int:pk>/edit/', views.admin_book_edit, name='admin_book_edit'),
    path('admin-panel/books/<int:pk>/delete/', views.admin_book_delete, name='admin_book_delete'),
    path('admin-panel/books/<int:pk>/quick-edit/', views.admin_book_quick_edit, name='admin_book_quick_edit'),
    path('admin-panel/reminders/', views.admin_reminders, name='admin_reminders'),
]
