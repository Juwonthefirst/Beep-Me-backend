import os
from urllib.parse import urlsplit
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from drf_yasg import openapi, views
from rest_framework.permissions import AllowAny

schema_view = views.get_schema_view(
    openapi.Info(
        title="Beep API",
        default_version="v1",
        description="private API for Beep chat",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="ajibolajuwon5@gmail.com"),
        license=openapi.License(name="MIT license"),
    ),
    public=True,
    url=(
        os.getenv("HOST_DOMAIN")
        if os.getenv("ENVIROMENT") == "production"
        else "http://localhost:8000"
    ),
    permission_classes=[AllowAny],
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("authentication.urls")),
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="open-api documentation",
    ),
    path("api/chats/", include("chat_room.urls")),
    path("api/groups/", include("group.urls")),
    path("api/users/", include("user.urls")),
    path("api/uploads/", include("upload.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
