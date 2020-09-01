from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from insta.urls import urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('insta.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)