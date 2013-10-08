from django.db import models
from django.utils import timezone
import datetime


class Check(models.Model):
    display_name = models.CharField(max_length=100, blank=True)
    url = models.CharField(max_length=300, verbose_name="URL")
    enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)

    def get_recent_results(self, max_age=datetime.timedelta(minutes=10)):
        min_time = timezone.now() - max_age
        return self.result_set.filter(time__gt=min_time)

    def get_last_result(self):
        results = self.result_set.all()
        if len(results) > 0:
            return results[0]
        else:
            return None

    def get_status(self):
        # Check if this is disabled
        if not self.enabled:
            return "disabled"

        # Get last result
        last_result = self.get_last_result()

        # Check if last result exists
        if not last_result:
            return "unknown"

        # Make sure it was produced in past 10 minutes
        min_time = timezone.now() - datetime.timedelta(minutes=10)
        if last_result.time < min_time:
            return "unknown"

        # Return last results status
        return last_result.status

    def post_result(self, status="unknown", status_text="", time=None):
        # Create result
        result = Result()
        if time is None:
            time = timezone.now()
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
