from django.urls import path
from . import views

urlpatterns = [
    # Registration URLs
    path('register/user/', views.register_user, name='register_user'),
    path('register/admin/', views.register_admin, name='register_admin'),

    # Login URLs
    path('login/user/', views.login_user, name='login_user'),
    path('login/admin/', views.login_admin, name='login_admin'),

    # Dashboard URLs
    path('dashboard/user/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    # Logout URL
    path('logout/admin/', views.logout_admin, name='logout_admin'),
    path('logout/user/', views.logout_user, name='logout_user'),

]
