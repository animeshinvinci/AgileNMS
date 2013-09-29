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
    class_name = models.CharField(max_length=100)
    result_class_name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)

    def get_recent_results(self, max_age=datetime.timedelta(minutes=10)):
        min_time = timezone.now() - max_age
        return CheckResult.objects.filter(check=self, time__gt=min_time)

    def post_result(self, data=None, time=timezone.now()):
        # Create result
        result = self.get_child().__class__.result_class()
        result.time = time
        result.check = self.get_child()
        result.maintenance_mode = self.maintenance_mode
        result.setup(data)

        # Save
        result.save()

    def get_child(self):
        # Split class_name into list of class names
        class_names = self.class_name.split(".")

        # Traverse through each class to find the bottom object
        current_object = self
        for class_name in class_names:
            if hasattr(current_object, class_name):
                current_object = getattr(current_object, class_name)

        # Return
        return current_object

    def get_class_name(self):
        class_names = []
        current_class = self.__class__

        # Keep going until we reach the Check class
        while current_class != Check:
            # Add current class to class list
            class_names.append(current_class._meta.module_name)

            # Find the next class
            for next_class in current_class.__bases__:
                # Make sure the next class is a sub class of Check
                if issubclass(next_class, Check):
                    current_class = next_class
                    break

        # Reverse class list
        class_names.reverse()

        # Convert class list into single string and return it
        return ".".join(class_names)

    def get_result_class_name(self):
        class_names = []
        current_class = self.__class__.result_class

        # Keep going until we reach the Check class
        while current_class != CheckResult:
            # Add current class to class list
            class_names.append(current_class._meta.module_name)

            # Find the next class
            for next_class in current_class.__bases__:
                # Make sure the next class is a sub class of Check
                if issubclass(next_class, CheckResult):
                    current_class = next_class
                    break

        # Reverse class list
        class_names.reverse()

        # Convert class list into single string and return it
        return ".".join(class_names)

    def save(self, *args, **kwargs):
        if not self.class_name:
            self.class_name = self.get_class_name()
        if not self.result_class_name:
            self.result_class_name = self.get_result_class_name()
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

    def run(self):
        self.post_result("Greetings from the dummy poller task :)")


class CheckResult(models.Model):
    uuid = models.CharField("UUID", max_length=32, primary_key=True, blank=True)
    check = models.ForeignKey(Check)
    time = models.DateTimeField()
    maintenance_mode = models.BooleanField()

    def setup(self, data):
        pass

    def get_child(self):
        # Split result_class_name into list of class names
        class_names = self.check.result_class_name.split(".")

        # Traverse through each class to find the bottom object
        current_object = self
        for class_name in class_names:
            if hasattr(current_object, class_name):
                current_object = getattr(current_object, class_name)

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
    pass
Poller.result_class = PollerResult


class DummyPollerResult(PollerResult):
    value = models.CharField(max_length=200)

    def setup(self, data):
        self.value = data
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
