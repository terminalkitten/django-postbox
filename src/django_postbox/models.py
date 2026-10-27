import uuid

from django.db import models


class Message(models.Model):
    """A captured mail as one recipient received it, stored as raw RFC 822 bytes"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.CharField(max_length=320)
    hash = models.CharField(max_length=16, db_index=True)
    sender = models.CharField(max_length=320, blank=True)
    subject = models.CharField(max_length=998, blank=True)
    raw = models.BinaryField()
    created_at = models.DateTimeField(db_index=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.subject
