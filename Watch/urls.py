
from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path("", views.welcome, name="welcome"),
    path("login/", views.user_login, name="login"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.user_logout, name="logout"),

    # SafePulse SOS prototype APIs
    path(
        "api/demo-sos/",
        views.create_demo_sos,
        name="create_demo_sos",
    ),
    path(
        "api/demo-sos/<int:event_id>/cancel/",
        views.cancel_demo_sos,
        name="cancel_demo_sos",
    ),

    # Control room
    path(
        "control-room/",
        views.control_room,
        name="control_room",
    ),
    path(
        "api/control-room/",
        views.control_room_data,
        name="control_room_data",
    ),
]
