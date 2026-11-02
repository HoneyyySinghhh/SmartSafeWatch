
from django.db import models


class EmergencyEvent(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CANCELLED", "Cancelled"),
        ("DEMO_ALERT_CREATED", "Demo Alert Created"),
        ("LOCATION_UNAVAILABLE", "Location Unavailable"),
    ]

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)

    source = models.CharField(
        max_length=50,
        default="SafePulse Web Prototype",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SOS #{self.id} - {self.status}"
