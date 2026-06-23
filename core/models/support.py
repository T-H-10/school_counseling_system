from django.db import models

from .base import BaseModel


class SupportRequest(BaseModel):
    STATUS_OPEN = "open"
    STATUS_RESOLVED = "resolved"
    STATUS_CHOICES = [
        (STATUS_OPEN, "פתוח"),
        (STATUS_RESOLVED, "טופל"),
    ]

    counselor = models.ForeignKey(
        "Counselor",
        on_delete=models.SET_NULL,
        null=True,
        related_name="support_requests",
    )
    school = models.ForeignKey(
        "School",
        on_delete=models.CASCADE,
        related_name="support_requests",
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)

    class Meta:
        ordering = ["-created_at"]
