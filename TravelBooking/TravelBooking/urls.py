from django.contrib import admin
from django.urls import path, include
from Travel import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("Travel.urls")),
    path('_reload_/', include('django_browser_reload.urls')),
    path('base/', views.base, name="base"),
    path('destination/', views.destination, name="destination"),
    path('destination_details/', views.destination_details, name="destination_details"),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]

# Static and Media URL Configuration for Development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
