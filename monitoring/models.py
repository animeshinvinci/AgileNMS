from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from dateutil.relativedelta import relativedelta
import datetime
import uuid


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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Group, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return "".join(["/checks/groups/", self.slug, "/"])

    def __unicode__(self):
        return self.name


class Check(models.Model):
    uuid = models.CharField("UUID", max_length=32, primary_key=True, blank=True, default=lambda: uuid.uuid4().hex)
    name = models.CharField(max_length=100, blank=True)
    group = models.ForeignKey(Group)
    url = models.CharField("URL", max_length=300)
    enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    passive = models.BooleanField(default=False)

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

    def post_result(self, status="unknown", status_text="", problems=[], time=None):
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

        # Problems
        if not self.maintenance_mode:
            # Any problems that are not in the list are now resolved
            self.problem_set.filter(end_time=None).exclude(name__in=problems).update(end_time=time, send_up_email=True)

            # Make sure that all of the problems in the list are recorded
            for problem in problems:
                Problem.objects.get_or_create(check=self, name=problem, end_time=None, defaults={"start_time": time})

    def save(self, *args, **kwargs):
        # If disabled or switched to maintenance_mode, mark all problems as resolved but dont send up emails
        # TODO: Stick this into a background cleanup task
        if not self.enabled or self.maintenance_mode:
            self.problem_set.filter(end_time=None).update(end_time=timezone.now())

        super(Check, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return "".join(["/checks/", self.uuid, "/"])

    def __unicode__(self):
        if self.name:
            return self.name
        return self.url


class Result(models.Model):
    uuid = models.CharField("UUID", max_length=32, primary_key=True, blank=True, default=lambda: uuid.uuid4().hex)
    check = models.ForeignKey(Check)
    time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    status_text = models.CharField(max_length=200, blank=True)
    maintenance_mode = models.BooleanField()

    def get_absolute_url(self):
        return "".join(["/results/", self.uuid, "/"])

    class Meta:
        ordering = ("-time",)


class Problem(models.Model):
    uuid = models.CharField("UUID", max_length=32, primary_key=True, blank=True, default=lambda: uuid.uuid4().hex)
    check = models.ForeignKey(Check)
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    acknowledged = models.BooleanField(default=False)
    send_down_email = models.BooleanField(default=True)
    send_up_email = models.BooleanField(default=False)

    def get_status(self):
        if not self.end_time is None:
            return "resolved"
        if self.acknowledged:
            return "acknowledged"
        return "unhandled"

    def get_absolute_url(self):
        return "".join(["/problems/", self.uuid, "/"])

    def __unicode__(self):
        return self.check.__unicode__() + " - " + self.name

    class Meta:
        ordering = ("-start_time",)


class Report(models.Model):
    # Basic info
    uuid = models.CharField("UUID", max_length=32, primary_key=True, blank=True, default=lambda: uuid.uuid4().hex)
    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)

    # List of checks to include
    checks = models.ManyToManyField(Check, null=True, blank=True)
    groups = models.ManyToManyField(Group, null=True, blank=True)

    # Schedule
    schedule = models.CharField(max_length=20, choices=REPORT_SCHEDULE_CHOICES)
    start_date = models.DateField(default=datetime.date.today)

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
            "uuid": self.uuid,
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


    def get_absolute_url(self):
        return "".join(["/reports/", self.uuid, "/"])

    def __unicode__(self):
        return self.name
