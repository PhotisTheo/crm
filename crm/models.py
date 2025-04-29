from io import BytesIO

import qrcode
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from storages.backends.s3boto3 import S3Boto3Storage


# ✅ Lead model
class Lead(models.Model):
    FSBO = "FSBO"
    EXPIRED = "Expired"
    LEAD_TYPES = [
        ("FSBO", "FSBO"),
        ("Expired", "Expired"),
        ("Seller", "Seller"),
        ("Buyer", "Buyer"),
        ("Open House", "Open House"),
    ]

    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("follow_up", "Follow Up"),
        ("closed", "Closed"),
    ]

    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255)
    lead_type = models.CharField(max_length=20, choices=LEAD_TYPES)
    source = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    last_contacted = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(
        storage=S3Boto3Storage(), upload_to="lead_images/", blank=True, null=True
    )  # ✅ Apply storage fix
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} – {self.lead_type}"


# ✅ PropertyVisit model
class PropertyVisit(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("visited", "Visited"),
        ("liked", "Client Liked"),
        ("disliked", "Client Disliked"),
    ]

    lead = models.ForeignKey("Lead", on_delete=models.CASCADE, related_name="visits")
    address = models.CharField(max_length=255)
    visit_date = models.DateTimeField()
    notes = models.TextField(blank=True)
    image = models.ImageField(
        storage=S3Boto3Storage(), upload_to="visit_images/", blank=True, null=True
    )  # ✅ Apply storage fix
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.address} ({self.status})"


# models.py

from io import BytesIO

import qrcode
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from django.utils import timezone
from storages.backends.s3boto3 import S3Boto3Storage


# ✅ OpenHouse model
class OpenHouse(models.Model):
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    date = models.DateTimeField()
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    lead = models.ForeignKey(
        "Lead",
        on_delete=models.CASCADE,
        related_name="openhouse_set",
        null=True,
        blank=True,
    )
    qr_code = models.ImageField(
        storage=S3Boto3Storage(), upload_to="qr_codes/", blank=True, null=True
    )

    def __str__(self):
        return f"{self.title} – {self.date.strftime('%b %d, %Y %I:%M %p')}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # First save to get primary key (self.pk)

        if not self.qr_code:
            # ✅ Build the correct QR URL based on your Railway domain
            relative_url = reverse("public_open_house_sign_in", args=[self.pk])
            full_url = f"https://crm-production-0b7b.up.railway.app{relative_url}"

            qr_img = qrcode.make(full_url)

            buffer = BytesIO()
            qr_img.save(buffer, format="PNG")
            buffer.seek(0)

            file_name = f"openhouse_{self.pk}.png"

            self.qr_code.save(file_name, ContentFile(buffer.read()), save=True)


# ✅ OpenHouseSignIn model (no image fields, no change needed)
class OpenHouseSignIn(models.Model):
    open_house = models.ForeignKey(
        OpenHouse, on_delete=models.CASCADE, related_name="sign_ins"
    )
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Automatically create a new Lead
        from crm.models import Lead

        Lead.objects.create(
            name=self.name,
            phone_number=self.phone_number,
            email=self.email,
            address=self.open_house.address,
            lead_type="Open House",
            status="new",
            notes=f"Signed in at {self.open_house.title} – {self.open_house.address}",
        )
