from django.db import models
from django.utils import timezone
import uuid
import datetime


class Contact(models.Model):
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()

    def __unicode__(self):
        name_parts = []

        # First name
        if self.first_name:
            name_parts.append(self.first_name)
            name_parts.append(" ")

            # Last name
            if self.last_name:
                name_parts.append(self.last_name)
                name_parts.append(" ")

        # Email
        name_parts.extend(["<", self.email, ">"])

        # Join everything and return
        return "".join(name_parts)


class Group(models.Model):
    slug = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    contacts = models.ManyToManyField(Contact, null=True, blank=True)
    
    def get_status(self):
        # Get check list
        checks = self.check_set.all()

        # Initialise status structure
        status = {
            "status": "unknown",
            "status_bootstrap_class": "primary",
            "check_statuses": {
                "ok": 0,
                "warning": 0,
                "critical": 0,
                "unknown": 0,
                "disabled": 0,
            }
        }

        # Loop through checks
        for check in checks:
            check_status = check.get_status()
            status["check_statuses"][check_status] += 1

        # Work out status
        if status["check_statuses"]["critical"] > 0:
            status["status"] = "critical"
            status["status_bootstrap_class"] = "danger"
        elif status["check_statuses"]["warning"] > 0:
            status["status"] = "warning"
            status["status_bootstrap_class"] = "warning"
        elif status["check_statuses"]["unknown"] > 0:
            status["status"] = "unknown"
            status["status_bootstrap_class"] = "primary"
        elif status["check_statuses"]["ok"] > 0:
            status["status"] = "ok"
            status["status_bootstrap_class"] = "success"
        elif status["check_statuses"]["disabled"] > 0:
            status["status"] = "disabled"
            status["status_bootstrap_class"] = "muted"

        # Return status
        return status

    def get_absolute_url(self):
        return "".join(["/groups/", self.slug, "/"])
        
    def __unicode__(self):
        return self.name


class Check(models.Model):
    display_name = models.CharField(max_length=100)
    group = models.ForeignKey(Group)
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
        if not self.enabled or not self.monitor.enabled:
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
        result.maintenance_mode = self.maintenance_mode or self.monitor.maintenance_mode

        # Save
        result.save()

    def get_absolute_url(self):
        return "".join([self.monitor.get_absolute_url(), "checks/", self.uuid, "/"])

    def __unicode__(self):
        if self.display_name:
            return self.display_name
        return self.uuid

    
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
    status_text = models.CharField(max_length=200)
    maintenance_mode = models.BooleanField()

    def get_absolute_url(self):
        return "".join([self.check.get_absolute_url(), "results/", self.uuid, "/"])

    class Meta:
        ordering = ("-time",)
        
    
class Report(models.Model):
    SCHEDULE_CHOICES = (
        (1, "Daily"),
        (2, "Weekly"),
        (3, "Monthly"),
        (4, "Quarterly"),
        (5, "Yearly"),
    )
    display_name = models.CharField(max_length=100)
    monitors = models.ManyToManyField(Monitor, null=True, blank=True)
    groups = models.ManyToManyField(Group, null=True, blank=True)
    contacts = models.ManyToManyField(Contact, null=True, blank=True)
    schedule = models.IntegerField(choices=SCHEDULE_CHOICES)
    base_time = models.DateTimeField(default=timezone.now)
    last_scheduled_send = models.DateTimeField(null = True)
    send_oneoff = models.BooleanField(default = False)

