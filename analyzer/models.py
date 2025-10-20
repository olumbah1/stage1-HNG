from django.db import models
from django.contrib.postgres.fields import JSONField # safe fallback
import django


# Use built-in JSONField available in Django 3.1+ (backed by sqlite or postgres)
try:
    from django.db.models import JSONField as BuiltinJSONField
except Exception:
    BuiltinJSONField = models.JSONField


class StringRecord(models.Model):
    id = models.CharField(primary_key=True, max_length=64) # SHA-256 hex
    value = models.TextField()
    properties = BuiltinJSONField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"StringRecord({self.id})"
