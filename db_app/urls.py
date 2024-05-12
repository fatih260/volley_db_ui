from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    
    #path('csrf_token/', views.csrf_token, name='csrf_token'),
    #path('session/', views.session, name='session'),
    path('db_admin_dashboard/', views.db_admin_dashboard, name='db_admin_dashboard'),
    path('player_dashboard/', views.player_dashboard, name='player_dashboard'),
    path('coach_dashboard/', views.coach_dashboard, name='coach_dashboard'),
    path('jury_dashboard/', views.jury_dashboard, name='jury_dashboard'),
    
]