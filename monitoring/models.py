from django.db import models
from django.utils import timezone
import datetime
import uuid


class Check(models.Model):
    uuid = models.CharField("UUID", max_length=32, primary_key=True, blank=True)
    name = models.CharField(max_length=100, blank=True)
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

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4().hex
        super(Check, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return "".join(["/checks/", self.uuid, "/"])

    def __unicode__(self):
        if self.name:
            return self.name
        return self.url


class Result(models.Model):
    STATUS_CHOICES = (
        ("ok", "OK"),
        ("warning", "WARNING"),
        ("critical", "CRITICAL"),
        ("unknown", "UNKNOWN"),
    )
    uuid = models.CharField("UUID", max_length=32, primary_key=True, blank=True)
    check = models.ForeignKey(Check)
    time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    status_text = models.CharField(max_length=200, blank=True)
    maintenance_mode = models.BooleanField()

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid5(uuid.UUID(hex=self.check.uuid), str(self.time)).hex
        super(Result, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return "".join([self.check.get_absolute_url(), "results/", self.uuid, "/"])

    class Meta:
        ordering = ("-time",)
