from django.db import models

class LaneData(models.Model):
    position = models.PositiveIntegerField()
    lane = models.PositiveIntegerField(null=True)
    upper = models.CharField(max_length=6, blank=True, default="")
    lower = models.CharField(max_length=6, blank=True, default="")

    class Meta:
        unique_together = ("position", "lane")

class Planogram(models.Model):
    lane_number = models.IntegerField(default=0)
    lane_name = models.CharField(max_length=255, default="")
    in_staged = models.IntegerField(default=0)
    mapped = models.IntegerField(default=0)
    missing = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    trucks_required = models.IntegerField(default=0)
    trucks_ordered = models.IntegerField(default=0)

class Pending(models.Model):
    lane = models.ForeignKey(Planogram, null=True, default=None, on_delete=models.CASCADE)
    pending_id = models.CharField(max_length=6)

class Processed(models.Model):
    lane = models.ForeignKey(Planogram, null=True, default=None, on_delete=models.CASCADE)
    processed_id = models.CharField(max_length=6)

