from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import secrets


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_valid(self):
        return (not self.used) and (timezone.now() - self.created_at <= timedelta(minutes=10))

    @classmethod
    def create_for_user(cls, user):
        code = f"{secrets.randbelow(10**6):06d}"
        return cls.objects.create(user=user, code=code)

    def mark_used(self):
        self.used = True
        self.save()

    def __str__(self):
        return f"OTP for {self.user} - {self.code}"
