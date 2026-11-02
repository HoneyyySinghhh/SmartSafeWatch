
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from .models import EmergencyEvent


def welcome(request):
    return render(request, "welcome.html")


def user_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not email or not password:
            messages.error(request, "Please fill in all fields.")

        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")

        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")

        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")

        else:
            User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            messages.success(
                request,
                "Account created successfully. Please log in."
            )
            return redirect("login")

    return render(request, "register.html")


@login_required(login_url="login")
def dashboard(request):
    recent_events = EmergencyEvent.objects.order_by("-created_at")[:10]

    return render(
        request,
        "dashboard.html",
        {"recent_events": recent_events}
    )


@login_required(login_url="login")
@require_POST
@csrf_protect
def create_demo_sos(request):
    try:
        data = json.loads(request.body or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Invalid request data."},
            status=400
        )

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    accuracy = data.get("accuracy")

    if (latitude is None) != (longitude is None):
        return JsonResponse(
            {"error": "Latitude and longitude must be supplied together."},
            status=400
        )

    try:
        if latitude is not None:
            latitude = float(latitude)
            longitude = float(longitude)

            if not (-90 <= latitude <= 90):
                raise ValueError

            if not (-180 <= longitude <= 180):
                raise ValueError

        if accuracy is not None:
            accuracy = float(accuracy)
            if accuracy < 0:
                raise ValueError

    except (TypeError, ValueError):
        return JsonResponse(
            {"error": "Invalid GPS coordinates or accuracy."},
            status=400
        )

    status = (
        "DEMO_ALERT_CREATED"
        if latitude is not None
        else "LOCATION_UNAVAILABLE"
    )

    event = EmergencyEvent.objects.create(
        status=status,
        latitude=latitude,
        longitude=longitude,
        accuracy=accuracy,
        source="SafePulse Web Prototype",
    )

    return JsonResponse({
        "success": True,
        "event_id": event.id,
        "status": event.status,
        "message": "Prototype event saved. No police alert was sent."
    })


@login_required(login_url="login")
@require_POST
@csrf_protect
def cancel_demo_sos(request, event_id):
    event = get_object_or_404(EmergencyEvent, pk=event_id)

    if event.status not in (
        "PENDING",
        "LOCATION_UNAVAILABLE",
        "DEMO_ALERT_CREATED",
    ):
        return JsonResponse(
            {"error": "This event cannot be cancelled."},
            status=409
        )

    event.status = "CANCELLED"
    event.save(update_fields=["status", "updated_at"])

    return JsonResponse({
        "success": True,
        "event_id": event.id,
        "status": event.status,
        "message": "Prototype event cancelled."
    })


@login_required(login_url="login")
def control_room(request):
    events = EmergencyEvent.objects.order_by("-created_at")[:100]

    return render(
        request,
        "control_room.html",
        {"events": events}
    )


@login_required(login_url="login")
def control_room_data(request):
    events = EmergencyEvent.objects.order_by("-created_at")[:100]

    data = [
        {
            "id": event.id,
            "status": event.status,
            "latitude": event.latitude,
            "longitude": event.longitude,
            "accuracy": event.accuracy,
            "source": event.source,
            "created_at": event.created_at.isoformat(),
        }
        for event in events
    ]

    return JsonResponse({"events": data})


@login_required(login_url="login")
def user_logout(request):
    logout(request)
    return redirect("welcome")
