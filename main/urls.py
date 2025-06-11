from django.urls import path, include
from . import views
urlpatterns = [
    path("", views.home, name="home"),
    path("register_fingerprint/", views.register_fingerprint, name="register_fingerprint"),
    path("fingerprint_login/", views.fingerprint_login, name="fingerprint_login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("register_fingerprint_begin/", views.register_fingerprint_begin, name="register_fingerprint_begin"),
    path("fingerprint_login_begin/", views.fingerprint_login_begin, name="fingerprint_login_begin"),
]
