from django.db import models

class LaneData(models.Model):
    position = models.PositiveIntegerField()
    lane = models.PositiveIntegerField(null=True)
    upper = models.CharField(max_length=6, blank=True, default="")
    lower = models.CharField(max_length=6, blank=True, default="")

    class Meta:
        unique_together = ("position", "lane")
