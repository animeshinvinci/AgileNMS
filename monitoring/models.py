from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.validators import validate_email
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


def validate_email_list(email_list):
    emails = email_list.split("\n")
    for email in emails:
        validate_email(email)


class Group(models.Model):
    slug = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=200)
    notification_addresses = models.TextField(blank=True, validators=[validate_email_list])

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
            return []

        # Get list of statuses from redis and convert to python
        status_list = []
        r = redis.Redis()
        for status in r.mget([check.redis_key for check in checks]):
            if status:
                status_py = json.loads(status)
                status_py["time"] = dateutil.parser.parse(status_py["time"])
                status_list.append(status_py)
            else:
                status_list.append(None)

        # Zip with checks and return
        return [{"check": status[0], "status": status[1]} for status in zip(checks, status_list)]

    @property
    def notification_addresses_list(self):
        return tuple(email for email in self.notification_addresses.split("\n"))

    def get_absolute_url(self):
        return "".join(["/checks/groups/", self.slug, "/"])

    def __unicode__(self):
        return self.name


class Check(models.Model):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(Group, db_index=True)
    url = models.CharField("URL", max_length=300)
    notification_addresses = models.TextField(blank=True, validators=[validate_email_list])
    enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)

    @property
    def redis_key(self):
        return "check_status:" + self.url

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

    @property
    def notification_addresses_list(self):
        emails = tuple(email for email in self.notification_addresses.split("\n"))
        return self.group.notification_addresses_list + emails

    def get_absolute_url(self):
        return "".join(["/checks/", str(self.id), "/"])

    def __unicode__(self):
        if self.name:
            return self.name
        return self.url


class CheckDailyReport(models.Model):
    check = models.ForeignKey(Check, db_index=True, unique_for_date="date")
    date = models.DateField(db_index=True)
    update_count = models.IntegerField(default=0)
    status_ok = models.IntegerField(default=0)
    status_warning = models.IntegerField(default=0)
    status_critical = models.IntegerField(default=0)
    status_unknown = models.IntegerField(default=0)
    status_disabled = models.IntegerField(default=0)
    maintenance_mode = models.IntegerField(default=0)


class Problem(models.Model):
    check = models.ForeignKey(Check, db_index=True)
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField(db_index=True)
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

    @property
    def notification_addresses_list(self):
        return self.check.notification_addresses_list

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
    notification_addresses = models.TextField(blank=True, validators=[validate_email_list])

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
