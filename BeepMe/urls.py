from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi, views
from . import home

schema_view = views.get_schema_view(
    openapi.Info(
        title = "Beep-me API",
        default_version = "v1",
        description = "private API for using Beep me services",
        terms_of_service = "https://www.google.com/policies/terms/",
        contact = openapi.Contact(email = "ajibolajuwon5@gmail.com"),
        license = openapi.License(name = "MIT license"),
    ),
    public = True,
)

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    
urlpatterns = [
    path("", home.home),
    path("googlef10182ad33636f0c.html", home.google_verify),
    path('admin/', admin.site.urls),
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("account/", include("allauth.urls")),
    path("api/auth/social/google/", GoogleLogin.as_view()),
    path("docs/", schema_view.with_ui("swagger", cache_timeout = 0), name = "open-api documentation"),
    path("api/chat/", include("chat.urls"))
]
