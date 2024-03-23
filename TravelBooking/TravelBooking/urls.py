from django.contrib import admin
from django.urls import path,include
from Travel import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("Travel.urls")),
    path('_reload_/', include('django_browser_reload.urls')),
    path('base/', views.Home, name="base"),
    path('signup/', views.Signup, name="signup"),
    path('login/', views.Login, name="login"),
    path('navbar/', views.navbar, name='navbar'),]