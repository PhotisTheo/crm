from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("", views.lead_list, name="lead_list"),
    path("new/", views.lead_create, name="lead_create"),
    path("edit/<int:pk>/", views.lead_update, name="lead_update"),
    path("lead/<int:pk>/", views.lead_detail, name="lead_detail"),
    path(
        "update-visit-status/<int:pk>/",
        views.update_visit_status,
        name="update_visit_status",
    ),
    path("delete-visit/<int:pk>/", views.delete_visit, name="delete_visit"),
    path(
        "update-visit-notes/<int:pk>/",
        views.update_visit_notes,
        name="update_visit_notes",
    ),
    path(
        "update-lead-status/<int:pk>/",
        views.update_lead_status,
        name="update_lead_status",
    ),
    path(
        "open-house/<int:pk>/sign-in/",
        views.open_house_sign_in,
        name="open_house_sign_in",
    ),
    path(
        "open-house/thank-you/", views.open_house_thank_you, name="open_house_thank_you"
    ),  # Temp redirect
    path("open-houses/", views.open_house_list, name="open_house_list"),
    path("open-houses/new/", views.create_open_house, name="create_open_house"),
    path("delete-lead/<int:pk>/", views.delete_lead, name="delete_lead"),
    path(
        "open-houses/create/<int:pk>/",
        views.create_open_house_for_lead,
        name="create_open_house_for_lead",
    ),
    path(
        "open-houses/delete/<int:pk>/",
        views.delete_open_house,
        name="delete_open_house",
    ),
    path("export-new-leads/", views.export_new_leads, name="export_new_leads"),
    path(
        "public-open-house-sign-in/<int:event_id>/",
        views.public_open_house_sign_in,
        name="public_open_house_sign_in",
    ),
    path("open-house/<int:pk>/", views.open_house_detail, name="open_house_detail"),
    path("calendar.ics", views.calendar_feed, name="calendar_feed"),
    path(
        "delete-calendar-event/<str:event_type>/<int:event_id>/",
        views.delete_calendar_event,
        name="delete_calendar_event",
    ),
]
