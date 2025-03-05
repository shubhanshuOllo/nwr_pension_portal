from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile
import json
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


# Signup View
@csrf_exempt
def signup_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON request body
            fullname = data.get("fullname")
            email = data.get("email")
            password = data.get("password")

            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "Email is already registered."}, status=400)

            user = User.objects.create_user(username=email, email=email, password=password)
            UserProfile.objects.create(user=user, fullname=fullname, email=email)

            login(request, user)  # Auto-login after signup
            return JsonResponse({"success": True, "redirect": "/index/"})  # Redirect to index

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid request format."}, status=400)

    return render(request, "signup.html")

@csrf_exempt
# Login View
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON request body
            email = data.get("email")
            password = data.get("password")

            user = authenticate(request, username=email, password=password)  # Authenticate user
            if user is not None:
                login(request, user)
                return JsonResponse({"success": True, "redirect": "/dashboard/dash/"})  # Return JSON response
            else:
                return JsonResponse({"error": "Invalid email or password."}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid request format."}, status=400)

    return render(request, "login.html")

@csrf_exempt
# Index (Homepage)
def index_view(request):
    if not request.user.is_authenticated:
        return redirect("login")  # Redirect unauthenticated users to login page
    return render(request, "index.html")

@csrf_exempt
# Logout View
def logout_view(request):
    logout(request)
    return redirect("login")  # Redirect to login page after logout
