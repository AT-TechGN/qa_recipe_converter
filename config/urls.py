from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('api/', include('apps.api.urls')),
    path('api/', include('apps.teams.urls')),
    path('teams/', include('apps.teams.web_urls')),   # Django template pages
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
