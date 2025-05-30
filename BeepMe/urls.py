from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi, views

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
    url="https://beep-me-api.onrender.com"
)


urlpatterns = [
    path("", include("home.urls")),
    path('admin/', admin.site.urls),
    path("api/auth", include("authentication.urls"))
    path("docs/", schema_view.with_ui("swagger", cache_timeout = 0), name = "open-api documentation"),
    path("api/chat/", include("chat.urls"))
]
