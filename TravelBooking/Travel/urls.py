from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, \
    CustomPasswordResetCompleteView, ForgotPasswordView


urlpatterns = [
    path('', views.index, name='index'),
    path('base/', views.base, name='base'),
    path('product_list/', views.product_list_view, name='product_list'),
    path('product_list/<int:category_id>/', views.filtered_product_list_view, name='filtered_product_list'),
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

    path('contact/', views.contact_us, name='contact_us'),
    path('contact/success/', views.contact_success, name='contact_success'),
    
    
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('vendor_products/', views.vendor_products, name='vendor_products'),
    path('add_product/', views.add_product, name='add_product'),
    path('vendor_login/', views.vendor_login, name='vendor_login'),
    path('vendor_register/', views.vendor_register, name='vendor_register'),
    path('vendor_dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor_settings/', views.vendor_settings, name='vendor_settings'),
    path('vendor_edit_profile/', views.vendor_edit_profile, name='vendor_edit_profile'),




    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    
    
]

