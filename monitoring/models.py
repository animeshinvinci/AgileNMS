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
    parent = models.ForeignKey("Group", null=True, blank=True)
    contacts = models.ManyToManyField(Contact, null=True, blank=True)

    def get_absolute_url(self):
        return "".join(["/groups/", self.slug, "/"])

    def clean(self):
        pass # TODO: CHECK FOR LOOPS IN GROUP TREE


class Monitor(models.Model):
    PROTOCOL_CHOICES = (
        ("dummy", "Dummy"),
        ("ping", "Ping"),
        ("tcp", "TCP"),
        ("http", "HTTP"),
        ("https", "HTTPS"),
    )
    uuid = models.CharField("UUID", max_length=32, primary_key=True, default=lambda: uuid.uuid4().hex)
    display_name = models.CharField(max_length=100)
    group = models.ForeignKey(Group, null=True, blank=True)
    protocol = models.CharField(max_length=100, choices=PROTOCOL_CHOICES)
    data = models.TextField()
    contacts = models.ManyToManyField(Contact, null=True, blank=True)
    enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)

    def add_check(self, name="", data=""):
        # Create check
        check = Check()
        check.monitor = self
        check.display_name = name
        check.data = data

        # Save check
        check.save()

    def get_absolute_url(self):
        return "".join(["/monitors/", self.uuid, "/"])

    def __unicode__(self):
        if self.display_name:
            return self.display_name
        return self.uuid


class Check(models.Model):
    uuid = models.CharField("UUID", max_length=32, primary_key=True, default=lambda: uuid.uuid4().hex)
    monitor = models.ForeignKey(Monitor)
    display_name = models.CharField(max_length=100)
    data = models.TextField()
    enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)

    def get_recent_results(self, max_age=datetime.timedelta(minutes=10)):
        min_time = timezone.now() - max_age
        return Result.objects.filter(check=self, time__gt=min_time)

    def get_last_result_time(self):
        return Result.objects.all()[0]

    def post_result(self, data="", time=timezone.now()):
        # Create result
        result = Result()
        result.time = time
        result.check = self
        result.maintenance_mode = self.maintenance_mode or self.monitor.maintenance_mode
        result.data = data

        # Save
        result.save()

    def get_absolute_url(self):
        return "".join([self.monitor.get_absolute_url(), "checks/", self.uuid, "/"])

    def __unicode__(self):
        if self.display_name:
            return self.display_name
        return self.uuid


class Result(models.Model):
    uuid = models.CharField("UUID", max_length=32, primary_key=True, blank=True)
    check = models.ForeignKey(Check)
    time = models.DateTimeField()
    maintenance_mode = models.BooleanField()
    data = models.TextField()

    def save(self, *args, **kwargs):
        if self.check and self.time:
            self.uuid = uuid.uuid5(uuid.UUID(hex=self.check.uuid), str(self.time)).hex
        super(Result, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return "".join([self.check.get_absolute_url(), "results/", self.uuid, "/"])

    class Meta:
        ordering = ("-time",)


class Problem(models.Model):
    uuid = models.CharField("UUID", max_length=32, primary_key=True, blank=True)
    check = models.ForeignKey(Check)
    time = models.DateTimeField()
    details = models.TextField()

    def get_absolute_url(self):
        return "".join([self.check.get_absolute_url(), "problems/", self.uuid, "/"])


class ProblemUpdate(models.Model):
    STATUS_CHOICES = (
        (1, "Open"),
        (2, "Acknowledged"),
        (3, "On Hold"),
        (4, "Resolved"),
    )
    problem = models.ForeignKey(Problem)
    time = models.DateTimeField()
    status = models.IntegerField(choices=STATUS_CHOICES)
    comment = models.TextField()

    class Meta:
        ordering = ("-time",)


class ReportPrototype(models.Model):
    uuid = models.CharField("UUID", max_length=32, primary_key=True, default=lambda: uuid.uuid4().hex)
    display_name = models.CharField(max_length=100)
    monitors = models.ManyToManyField(Monitor, null=True, blank=True)
    groups = models.ManyToManyField(Group, null=True, blank=True)
    contacts = models.ManyToManyField(Contact, null=True, blank=True)

    def get_absolute_url(self):
        return "".join(["/reports/", self.uuid, "/"])


class ReportSchedule(models.Model):
    SCHEDULE_CHOICES = (
        (1, "Daily"),
        (2, "Weekly"),
        (3, "Monthly"),
        (4, "Quarterly"),
        (5, "Yearly"),
    )
    prototype = models.ForeignKey(ReportPrototype)
    schedule = models.IntegerField(choices=SCHEDULE_CHOICES)
    base_time = models.DateTimeField()


class Report(models.Model):
    prototype = models.ForeignKey(ReportPrototype)
    schedule = models.ForeignKey(ReportSchedule, null=True, blank=True)
    time = models.DateTimeField()

    class Meta:
        ordering = ("-time",)
