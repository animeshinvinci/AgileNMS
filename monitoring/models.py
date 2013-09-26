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
    type_name = "Check"

    uuid = models.CharField("UUID", max_length=32, primary_key=True, default=lambda: uuid.uuid4().hex)
    enabled = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    last_result = models.IntegerField(default=0)
    last_problem = models.IntegerField(default=0)

    def setup_result(self, result):
        self.last_result += 1
        result.check = self
        result.number = self.last_result
        result.maintenance_mode = self.maintenance_mode
        self.save()

    def get_last_result(self):
        if self.last_result == 0:
            return None

        return CheckResult.objects.get(check=self, number=self.last_result)

    def get_child(self):
        if hasattr(self, "poller"):
            return self.poller.get_child()
        if hasattr(self, "trap"):
            return self.trap.get_child()
        return None

    def get_absolute_url(self):
        return "".join(["/checks/", self.uuid, "/"])

    def __unicode__(self):
        return self.uuid


class Poller(Check):
    type_name = "Poller"

    poll_frequency = models.IntegerField(default=600)

    def should_poll(self):
        last_result = self.get_last_result()
        if not last_result:
            return True

        if last_result.time + datetime.timedelta(seconds=self.poll_frequency) < timezone.now():
            return True

        return False

    def get_child(self):
        if hasattr(self, "pingpoller"):
            return self.pingpoller
        if hasattr(self, "tcppoller"):
            return self.tcppoller
        if hasattr(self, "httppoller"):
            return self.httppoller
        return None


class PingPoller(Poller):
    type_name = "Ping Poller"

    ping_hostname = models.CharField("Hostname", max_length=200)
    ping_response_time_warning_threshold = models.IntegerField("Warning Threshold", null=True, blank=True, default=500)
    ping_response_time_error_theshold = models.IntegerField("Error Threshold", null=True, blank=True, default=1000)

    def post_result(self, ping_response_time, time=timezone.now()):
        # Create result
        result = PingPollerResult()
        self.setup_result(result)
        result.time = time

        # Set value
        result.ping_response_time = ping_response_time

        # Calculate status
        if result.ping_response_time is None:
            result.status = 3
        else:
            if self.ping_response_time_error_theshold and result.ping_response_time >= self.ping_response_time_error_theshold:
                result.status = 3
            elif self.ping_response_time_warning_threshold and result.ping_response_time >= self.ping_response_time_warning_threshold:
                result.status = 2
            else:
                result.status = 1

        # Save
        result.save()

    def __unicode__(self):
        return self.ping_hostname


class TCPPoller(Poller):
    type_name = "TCP Poller"

    tcp_hostname = models.CharField("Hostname", max_length=200)
    tcp_port = models.PositiveIntegerField("Port")
    tcp_response_time_warning_threshold = models.IntegerField("Warning Threshold", null=True, blank=True, default=500)
    tcp_response_time_error_theshold = models.IntegerField("Error Threshold", null=True, blank=True, default=1000)

    def post_result(self, tcp_response_time, time=timezone.now()):
        # Create result
        result = TCPPollerResult()
        self.setup_result(result)
        result.time = time

        # Set value
        result.tcp_response_time = tcp_response_time

        # Calculate status
        if result.tcp_response_time is None:
            result.status = 3
        else:
            if self.tcp_response_time_error_theshold and result.tcp_response_time >= self.tcp_response_time_error_theshold:
                result.status = 3
            elif self.tcp_response_time_warning_threshold and result.tcp_response_time >= self.tcp_response_time_warning_threshold:
                result.status = 2
            else:
                result.status = 1

        # Save
        result.save()

    def __unicode__(self):
        return self.tcp_hostname + ":" + str(self.tcp_port)


class HTTPPoller(Poller):
    type_name = "HTTP Poller"

    http_url = models.URLField("URL")
    http_response_time_warning_threshold = models.IntegerField("Warning Threshold", null=True, blank=True, default=500)
    http_response_time_error_theshold = models.IntegerField("Error Threshold", null=True, blank=True, default=1000)

    def __unicode__(self):
        return self.http_url


class CheckResult(models.Model):
    check = models.ForeignKey(Check)
    number = models.IntegerField()
    time = models.DateTimeField()
    maintenance_mode = models.BooleanField()

    class Meta:
        unique_together = (
            ("check", "number"),
        )


class PollerResult(CheckResult):
    STATUS_CHOICES = (
        (1, "UP"),
        (2, "WARNING"),
        (3, "DOWN"),
    )

    status = models.IntegerField(null=True, blank=True, choices=STATUS_CHOICES)


class PingPollerResult(PollerResult):
    ping_response_time = models.IntegerField("Response time", null=True)


class TCPPollerResult(PollerResult):
    tcp_response_time = models.IntegerField("Response time", null=True)


class HTTPPollerResult(PollerResult):
    http_response_time = models.IntegerField("Response time")
    http_status_code = models.IntegerField("Status code")


class Problem(models.Model):
    check = models.ForeignKey(Check)
    number = models.IntegerField()
    start_date = models.DateTimeField()
    acknowledge_date = models.DateTimeField(null=True, blank=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    result_number = models.IntegerField(null=True, blank=True)
    summary = models.TextField(max_length=200)
    details = models.TextField(null=True, blank=True)
