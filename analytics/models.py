from django.db import models

class Visit(models.Model):
    path = models.CharField(max_length=100, unique=True)
    count = models.PositiveIntegerField(default=0)
    last_visit = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.path} → {self.count}"


class VisitLog(models.Model):
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name="logs")
    ip = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField(default=0)  # sec

    def __str__(self):
        return f"{self.ip} @ {self.visit.path} ({self.timestamp:%Y-%m-%d %H:%M:%S})"
