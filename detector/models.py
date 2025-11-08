from django.db import models

class ScannedEmail(models.Model):
    subject = models.CharField(max_length=512, blank=True)
    sender = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    rules_triggered = models.TextField(blank=True)
    ml_label = models.CharField(max_length=50, blank=True)
    final_label = models.CharField(max_length=50)
    score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} - {self.subject[:40]}"
