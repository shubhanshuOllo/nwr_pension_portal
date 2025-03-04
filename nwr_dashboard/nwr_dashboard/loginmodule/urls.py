from django.urls import path
from .views import signup_view, login_view, index_view, logout_view

urlpatterns = [
    path("", index_view, name="index"),         # Homepage (index.html)
    path("signup/", signup_view, name="signup"), # Signup page
    path('login/', login_view, name='login'),    # Login page
    path("logout/", logout_view, name="logout"), # Logout user
]
