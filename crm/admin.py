from django.contrib import admin

from .models import Lead, OpenHouse


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "lead_type", "status", "last_contacted", "created_at")
    list_filter = ("lead_type", "status")
    search_fields = ("name", "phone_number", "address")


@admin.register(OpenHouse)
class OpenHouseAdmin(admin.ModelAdmin):
    list_display = ("title", "address", "date", "lead")
    list_filter = ("date",)
    search_fields = ("title", "address")
    ordering = ("-date",)
