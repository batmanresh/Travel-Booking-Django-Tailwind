from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('base/', views.base, name='base'),
    path('product_list/', views.product_list_view, name='product_list'),
    path('product_detail/<str:pid>/', views.product_detail_view, name='product_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('checkout/', views.checkout, name='checkout'),
    path('check_availability/', views.check_availability, name='check_availability'),
    
    
]

