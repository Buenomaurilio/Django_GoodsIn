# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.appointment_list, name='appointments'),
#     path('edit/<int:pk>/', views.edit_appointment, name='edit_appointment'),
# ]



from django.urls import path
from . import views

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('add/', views.add_appointment, name='add_appointment'),
    path('edit/<int:pk>/', views.edit_appointment, name='edit_appointment'),
    path('checkers/add/', views.add_checker, name='add_checker'),
    path('appointments/export/', views.export_appointments_csv, name='export_appointments_csv'),
    path('appointments/import/', views.import_appointments_csv, name='import_appointments_csv'),
]


# from django.contrib.auth import views as auth_views
# from django.urls import path
# from . import views

# urlpatterns = [
#     path("login/", auth_views.LoginView.as_view(template_name="appointments/login.html"), name="login"),
#     path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
#     path("", views.appointment_list, name="appointment_list"),
#     path("edit/<int:pk>/", views.edit_appointment, name="edit_appointment"),
# ]
