from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from dateutil.relativedelta import relativedelta
import dateutil.parser
import datetime
import redis
import json


STATUS_CHOICES = (
    ("ok", "OK"),
    ("warning", "WARNING"),
    ("critical", "CRITICAL"),
    ("unknown", "UNKNOWN"),
    ("disabled", "DISABLED"),
)


REPORT_SCHEDULE_CHOICES = (
    ("1 day", "Daily"),
    ("7 day", "Weekly"),
    ("1 month", "Monthly"),
    ("3 month", "Quarterly"),
    ("1 year", "Yearly"),
)


class Group(models.Model):
    slug = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=200)
    notification_addresses = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Group, self).save(*args, **kwargs)

    @property
    def status_list(self):
        # Get list of checks
        checks = list(self.check_set.all())

        # Check if there are any checks
        if len(checks) == 0:
            return

        # Get list of statuses from redis
        r = redis.Redis()
        status_list = r.mget([check.redis_key for check in checks])

        # Load json
        status_list = [json.loads(status) for status in status_list]

        # Convert to python times
        for status in status_list:
            status["time"] = dateutil.parser.parse(status["time"])

        # Zip with checks and return
        return [{"check": status[0], "status": status[1]} for status in zip(checks, status_list)]

    def get_absolute_url(self):
        return "".join(["/checks/groups/", self.slug, "/"])

    def __unicode__(self):
        return self.name


class Check(models.Model):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(Group)
    url = models.CharField("URL", max_length=300)
    notification_addresses = models.TextField(blank=True)
    enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)

    @property
    def redis_key(self):
        return ":".join(["check", self.url, "status"])

    @property
    def status(self):
        r = redis.Redis()
        status_json = r.get(self.redis_key)
        if status_json:
            status = json.loads(status_json)
            status["time"] = dateutil.parser.parse(status["time"])
            return status
        else:
            return None

    def get_absolute_url(self):
        return "".join(["/checks/", str(self.id), "/"])

    def __unicode__(self):
        if self.name:
            return self.name
        return self.url


class CheckDailyReport(models.Model):
    check = models.ForeignKey(Check)
    date = models.DateField()
    update_count = models.IntegerField(default=0)
    status_ok = models.IntegerField(default=0)
    status_warning = models.IntegerField(default=0)
    status_critical = models.IntegerField(default=0)
    status_unknown = models.IntegerField(default=0)
    status_disabled = models.IntegerField(default=0)
    maintenance_mode = models.IntegerField(default=0)

    class Meta:
        unique_together = (
            ("check", "date"),
        )


class Problem(models.Model):
    check = models.ForeignKey(Check)
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    acknowledged = models.BooleanField(default=False)
    send_down_email = models.BooleanField(default=True)
    send_up_email = models.BooleanField(default=False)

    @property
    def status(self):
        if self.end_time is not None:
            return "resolved"
        if self.acknowledged:
            return "acknowledged"
        return "unhandled"

    def get_absolute_url(self):
        return "".join(["/problems/", str(self.id), "/"])

    def __unicode__(self):
        return self.check.__unicode__() + " - " + self.name

    class Meta:
        ordering = ("-start_time",)


class Report(models.Model):
    # Basic info
    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)

    # List of checks to include
    checks = models.ManyToManyField(Check, null=True, blank=True)
    groups = models.ManyToManyField(Group, null=True, blank=True)

    # Schedule
    schedule = models.CharField(max_length=20, choices=REPORT_SCHEDULE_CHOICES)
    start_date = models.DateField(default=datetime.date.today)
    
    # Notification addresses
    notification_addresses = models.TextField(blank=True)

    def decode_schedule(self):
        # Split schedule into unit and value
        schedule_split = self.schedule.split()
        if len(schedule_split) != 2:
            raise ValueError("Invalid schedule: \"" + self.schedule + "\"")

        # Get value
        try:
            schedule_value = int(schedule_split[0])
        except ValueError:
            raise ValueError("Invalid schedule: \"" + self.schedule + "\"")

        # Get unit
        schedule_unit = schedule_split[1]

        # Work out start and end date for this report
        if schedule_unit == "day":
            return schedule_value, 0, 0
        if schedule_unit == "month":
            return 0, schedule_value, 0
        if schedule_unit == "year":
            return 0, 0, schedule_value
        else:
            raise ValueError("Invalid schedule: \"" + self.schedule + "\"")

    def generate(self, number):
        report = {}

        # Metadata
        report["meta"] = {
            "id": self.id,
            "name": self.name,
        }

        # Decode schedule
        try:
            schedule_days, schedule_months, schedule_years = self.decode_schedule()
        except ValueError as e:
            report.update({"error": e.value})
            return report

        # Work out start and end dates
        start_date = self.start_date + relativedelta(days=schedule_days*number, months=schedule_months*number, years=schedule_years*number)
        end_date = start_date + relativedelta(days=schedule_days-1, months=schedule_months, years=schedule_years)
        total_days = (end_date - start_date).days + 1
        report["start_date"] = start_date
        report["end_date"] = end_date
        report["total_days"] = total_days

        return report

    def generate_today(self):
        return False

    def get_absolute_url(self):
        return "".join(["/reports/", str(self.id), "/"])

    def __unicode__(self):
        return self.name
