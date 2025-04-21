from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login')),  # 👈 Root URL redirects to login
    path('', include('tracker_app.urls')),        # 👈 Include your app's URLs
]
