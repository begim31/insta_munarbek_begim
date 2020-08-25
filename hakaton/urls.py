from django.contrib import admin
from django.urls import path, include
from insta.urls import urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include((urlpatterns, 'instagram_app')))
]