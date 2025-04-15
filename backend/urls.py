from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pg_data.urls")),  # Add this if your rooms app has a separate urls.py
]
