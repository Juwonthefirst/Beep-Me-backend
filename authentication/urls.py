from django.urls import path, include
from . import views
urlpatterns = [
	path("", include("dj_rest_auth.urls")),
    path("registration/", include("dj_rest_auth.registration.urls")),
    path("social/google/ID", views.googleLoginByIdToken),
    path("social/google/code", views.googleLoginByCode),
]