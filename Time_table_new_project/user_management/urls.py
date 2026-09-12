from django.urls import path

from user_management import views

app_name = 'accounts'

urlpatterns = [
    path('', views.login, name='login'),
    #path('sync_gsb_employees', views.sync_gsb_employees, name='sync_gsb_employees'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('switch-group/<int:membership_id>/', views.switch_group, name='switch_group'),
]
