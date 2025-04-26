from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from tracker_app.admin import admin_site  # Import the custom admin site

urlpatterns = [
    # Custom admin site URL
    path('admin/', admin_site.urls),  # Use custom admin site

    # Root URL redirects to the login page
    path('', lambda request: redirect('login')),  # Root URL redirects to login

    # Include your app's URLs (tracker_app)
    path('', include('tracker_app.urls')),        # Your app's URL patterns
]
