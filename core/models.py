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


class Check(models.Model):
    uuid = models.CharField("UUID", max_length=32, primary_key=True, default=lambda: uuid.uuid4().hex)
    display_name = models.CharField(max_length=100)
    type_name = models.CharField(max_length=100)
    subtype_name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)

    def get_recent_results(self, max_age=datetime.timedelta(minutes=10)):
        min_time = timezone.now() - max_age
        return CheckResult.objects.filter(check=self, time__gt=min_time)

    def get_child(self):
        if hasattr(self, self.type_name):
            child = getattr(self, self.type_name)
            if hasattr(child, self.subtype_name):
                return getattr(child, self.subtype_name)
        return None

    def get_absolute_url(self):
        return "".join(["/checks/", self.uuid, "/"])

    def __unicode__(self):
        if self.display_name:
            return self.display_name
        return self.uuid


class Poller(Check):
    poll_frequency = models.IntegerField(default=600)

    def should_poll(self):
        if not self.enabled:
            return False

        # If there havent been any checks since "poll_frequency" seconds ago, return True
        if len(self.get_recent_results(max_age=datetime.timedelta(seconds=self.poll_frequency))) == 0:
            return True

        return False

    def run(self):
        return

    def save(self, *args, **kwargs):
        self.type_name = "poller"
        super(Poller, self).save(*args, **kwargs)


class DummyPoller(Poller):
    value = models.CharField(max_length=200)

    def post_result(self, value, time=timezone.now()):
        # Create result
        result = DummyPollerResult()
        result.time = time
        result.check = self
        result.maintenance_mode = self.maintenance_mode
        result.value = value

        # Save
        result.save()

    def run(self):
        self.post_result("Greetings from the dummy poller task :)")

    def save(self, *args, **kwargs):
        self.subtype_name = "dummypoller"
        super(DummyPoller, self).save(*args, **kwargs)


class CheckResult(models.Model):
    uuid = models.CharField("UUID", max_length=32, primary_key=True, blank=True)
    check = models.ForeignKey(Check)
    time = models.DateTimeField()
    maintenance_mode = models.BooleanField()

    def get_child(self):
        type_name = self.check.type_name + "result"
        subtype_name = self.check.subtype_name + "result"
        if hasattr(self, type_name):
            child = getattr(self, type_name)
            if hasattr(child, subtype_name):
                return getattr(child, subtype_name)

    def save(self, *args, **kwargs):
        if self.check and self.time:
            self.uuid = uuid.uuid5(uuid.UUID(hex=self.check.uuid), str(self.time)).hex
        super(CheckResult, self).save(*args, **kwargs)

    class Meta:
        ordering = ("-time",)


class PollerResult(CheckResult):
    STATUS_CHOICES = (
        (1, "UP"),
        (2, "WARNING"),
        (3, "DOWN"),
    )

    status = models.IntegerField(null=True, blank=True, choices=STATUS_CHOICES)


class DummyPollerResult(PollerResult):
    value = models.CharField(max_length=200)


class Problem(models.Model):
    uuid = models.CharField("UUID", max_length=32, primary_key=True, blank=True)
    check = models.ForeignKey(Check)
    start_time = models.DateTimeField()
    acknowledge_time = models.DateTimeField(null=True, blank=True)
    resolved_time = models.DateTimeField(null=True, blank=True)
    summary = models.TextField(max_length=200)
    details = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.check and self.start_time:
            self.uuid = uuid.uuid5(uuid.UUID(hex=self.check.uuid), str(self.start_time)).hex
        super(Problem, self).save(*args, **kwargs)
