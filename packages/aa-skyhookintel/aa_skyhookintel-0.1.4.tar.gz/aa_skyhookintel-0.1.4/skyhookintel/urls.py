"""Routes."""

from django.urls import path

from . import views

app_name = "skyhookintel"

urlpatterns = [
    path("", views.index, name="index"),
    path("upcoming", views.upcoming_timers, name="upcoming_timers"),
    path(
        "upcoming/data",
        views.UpcomingSkyhooksListJson.as_view(),
        name="upcoming_timers_data",
    ),
    path(
        "upcoming/fdd_data",
        views.skyhooks_with_timers_fdd_data,
        name="upcoming_fdd_data",
    ),
    path("no_timers", views.no_timers, name="no_timers"),
    path(
        "no_timers/data",
        views.NoTimersSkyhooksListJson.as_view(),
        name="no_timers_data",
    ),
    path(
        "no_timers/fdd_data",
        views.skyhooks_no_timers_fdd_data,
        name="no_timers_fdd_data",
    ),
    path(
        "add_timer/<int:planet_id>", views.add_skyhook_timer, name="add_skyhook_timer"
    ),
]
