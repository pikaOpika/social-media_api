from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include("users.urls", namespace="users")),
    path('api/', include("posts.urls", namespace="posts")),
    path("doc/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("doc/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("doc/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
