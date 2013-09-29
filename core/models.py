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
    result_type_name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)

    def get_recent_results(self, max_age=datetime.timedelta(minutes=10)):
        min_time = timezone.now() - max_age
        return CheckResult.objects.filter(check=self, time__gt=min_time)

    def get_child(self):
        # Split type_name into list of type names
        type_names = self.type_name.split(".")

        # Traverse through each type to find the bottom object
        current_object = self
        for type_name in type_names:
            if hasattr(current_object, type_name):
                current_object = getattr(current_object, type_name)

        # Return
        return current_object

    def get_type_name(self):
        type_names = []
        current_type = self.__class__

        # Keep going until we reach the type class
        while current_type != Check:
            # Add current class to class list
            type_names.append(current_type._meta.module_name)

            # Find the next type name
            for next_type in current_type.__bases__:
                if issubclass(next_type, Check):
                    current_type = next_type
                    break

        # Reverse type list
        type_names.reverse()

        # Convert type list into single string and return it
        return ".".join(type_names)

    def get_result_type_name(self):
        type_names = []
        current_type = self.__class__.result_class

        # Keep going until we reach the type class
        while current_type != CheckResult:
            # Add current class to class list
            type_names.append(current_type._meta.module_name)

            # Find the next type name
            for next_type in current_type.__bases__:
                if issubclass(next_type, CheckResult):
                    current_type = next_type
                    break

        # Reverse type list
        type_names.reverse()

        # Convert type list into single string and return it
        return ".".join(type_names)

    def save(self, *args, **kwargs):
        if not self.type_name:
            self.type_name = self.get_type_name()
        if not self.result_type_name:
            self.result_type_name = self.get_result_type_name()
        super(Check, self).save(*args, **kwargs)

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
        
        
class CheckResult(models.Model):
    uuid = models.CharField("UUID", max_length=32, primary_key=True, blank=True)
    check = models.ForeignKey(Check)
    time = models.DateTimeField()
    maintenance_mode = models.BooleanField()

    def get_child(self):
        # Split type_name into list of type names
        type_names = self.check.result_type_name.split(".")

        # Traverse through each type to find the bottom object
        current_object = self
        for type_name in type_names:
            if hasattr(current_object, type_name):
                current_object = getattr(current_object, type_name)

        # Return
        return current_object

    def save(self, *args, **kwargs):
        if self.check and self.time:
            self.uuid = uuid.uuid5(uuid.UUID(hex=self.check.uuid), str(self.time)).hex
        super(CheckResult, self).save(*args, **kwargs)

    class Meta:
        ordering = ("-time",)
Check.result_class = CheckResult


class PollerResult(CheckResult):
    STATUS_CHOICES = (
        (1, "UP"),
        (2, "WARNING"),
        (3, "DOWN"),
    )

    status = models.IntegerField(null=True, blank=True, choices=STATUS_CHOICES)
Poller.result_class = PollerResult


class DummyPollerResult(PollerResult):
    value = models.CharField(max_length=200)
DummyPoller.result_class = DummyPollerResult


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
