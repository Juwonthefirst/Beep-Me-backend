from django.urls import path, include
from . import views


urlpatterns = [
	path("login/", views.CustomLoginView.as_view()),
	path("logout/", views.logoutView),
    path("registration/", include("dj_rest_auth.registration.urls")),
    path("social/google/ID/", views.googleLoginByIdToken),
    path("social/google/code/", views.googleLoginByCode),
	path("token/refresh/", views.CustomTokenRefreshView.as_view()),
	path("user/csrf/", views.get_csrf),
	path("", include("dj_rest_auth.urls")),
]