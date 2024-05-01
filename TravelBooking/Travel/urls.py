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
    path('check_availability/<str:pid>/',views.check_availability, name='check_availability'),
    path('booking_details/<int:product_id>/',views.booking_details, name='booking_details'),
    path('submit_booking/', views.submit_booking, name='submit_booking'),
    path('payment-response/', views.payment_response, name='payment_response'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('search/', views.search_results, name='search_results'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('compare/', views.compare_products, name='compare'),


    

    
    path('customize/', views.customize, name='customize'),
    
    
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('vendor_products/', views.vendor_products, name='vendor_products'),
    path('add_product/', views.add_product, name='add_product'),
    path('vendor_login/', views.vendor_login, name='vendor_login'),
    path('vendor_register/', views.vendor_register, name='vendor_register'),
    path('vendor_dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    
    
]

