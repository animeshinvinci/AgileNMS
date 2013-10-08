from django.db import models
from django.utils import timezone
import datetime


class Check(models.Model):
    display_name = models.CharField(max_length=100, blank=True)
    url = models.CharField(max_length=300)
    enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)

    def get_recent_results(self, max_age=datetime.timedelta(minutes=10)):
        min_time = timezone.now() - max_age
        return self.result_set.filter(time__gt=min_time)

    def get_last_result(self):
        return self.result_set.all()[0]

    def get_status(self):
        # Check if this is disabled
        if not self.enabled:
            return "disabled"

        # Get last result
        try:
            last_result = self.get_last_result()
        except:
            return "unknown"

        # Make sure it was produced in past 10 minutes
        min_time = timezone.now() - datetime.timedelta(minutes=10)
        if last_result.time < min_time:
            return "unknown"

        # Return last results status
        return last_result.status

    def post_result(self, status="unknown", status_text="", time=timezone.now()):
        # Create result
        result = Result()
        result.time = time
        result.check = self
        result.status = status
        result.status_text = status_text
        result.maintenance_mode = self.maintenance_mode

        # Save
        result.save()

    def get_absolute_url(self):
        return "".join(["/checks/", str(self.pk), "/"])

    def __unicode__(self):
        if self.display_name:
            return self.display_name
        return self.url


class Result(models.Model):
    STATUS_CHOICES = (
        ("ok", "OK"),
        ("warning", "WARNING"),
        ("critical", "CRITICAL"),
        ("unknown", "UNKNOWN"),
    )
    check = models.ForeignKey(Check)
    time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    status_text = models.CharField(max_length=200, blank=True)
    maintenance_mode = models.BooleanField()

    def get_absolute_url(self):
        return "".join([self.check.get_absolute_url(), "results/", str(self.pk), "/"])

    class Meta:
        ordering = ("-time",)
