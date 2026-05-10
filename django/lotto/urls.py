from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('buy/', views.buy_ticket, name='buy_ticket'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('check-win/', views.check_win, name='check_win'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-draw/', views.admin_draw, name='admin_draw'),
    path('admin-sales/', views.admin_sales, name='admin_sales'),
    path('admin-results/', views.admin_results, name='admin_results'),
]