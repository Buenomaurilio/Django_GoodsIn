from django.contrib.auth import views as auth_views
from accounts.views import CustomLoginView
from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='appointments/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', include('appointments.urls')),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)