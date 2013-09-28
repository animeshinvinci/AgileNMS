from django.db import models
from django.utils import timezone
from core.models import Poller, PollerResult


class PingPoller(Poller):
    ping_hostname = models.CharField("Hostname", max_length=200)
    ping_response_time_warning_threshold = models.IntegerField("Warning Threshold", null=True, blank=True, default=500)
    ping_response_time_error_theshold = models.IntegerField("Error Threshold", null=True, blank=True, default=1000)

    def post_result(self, ping_response_time, time=timezone.now()):
        # Create result
        result = PingPollerResult()
        result.time = time
        result.check = self
        result.maintenance_mode = self.maintenance_mode
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

    def save(self, *args, **kwargs):
        self.subtype_name = "pingpoller"
        super(DummyPoller, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.ping_hostname


class TCPPoller(Poller):
    tcp_hostname = models.CharField("Hostname", max_length=200)
    tcp_port = models.PositiveIntegerField("Port")
    tcp_response_time_warning_threshold = models.IntegerField("Warning Threshold", null=True, blank=True, default=500)
    tcp_response_time_error_theshold = models.IntegerField("Error Threshold", null=True, blank=True, default=1000)

    def post_result(self, tcp_response_time, time=timezone.now()):
        # Create result
        result = TCPPollerResult()
        result.time = time
        result.check = self
        result.maintenance_mode = self.maintenance_mode
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

    def save(self, *args, **kwargs):
        self.subtype_name = "tcppoller"
        super(DummyPoller, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.tcp_hostname + ":" + str(self.tcp_port)


class HTTPPoller(Poller):
    http_url = models.URLField("URL")
    http_response_time_warning_threshold = models.IntegerField("Warning Threshold", null=True, blank=True, default=500)
    http_response_time_error_theshold = models.IntegerField("Error Threshold", null=True, blank=True, default=1000)

    def post_result(self, http_response_time, http_status_code, time=timezone.now()):
        # Create result
        result = HTTPPollerResult()
        result.time = time
        result.check = self
        result.maintenance_mode = self.maintenance_mode
        result.http_response_time = http_response_time
        result.http_status_code = http_status_code

        # Calculate status
        if result.http_response_time is None:
            result.status = 3
        else:
            if self.http_response_time_error_theshold and result.http_response_time >= self.http_response_time_error_theshold:
                result.status = 3
            elif self.http_response_time_warning_threshold and result.http_response_time >= self.http_response_time_warning_threshold:
                result.status = 2
            else:
                result.status = 1

        # If an error status code is recieved, set to down state
        if result.http_status_code >= 400:
            result.status = 3

        # Save
        result.save()

    def save(self, *args, **kwargs):
        self.subtype_name = "httppoller"
        super(DummyPoller, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.http_url


class PingPollerResult(PollerResult):
    ping_response_time = models.IntegerField("Response time", null=True)


class TCPPollerResult(PollerResult):
    tcp_response_time = models.IntegerField("Response time", null=True)


class HTTPPollerResult(PollerResult):
    http_response_time = models.IntegerField("Response time", null=True)
    http_status_code = models.IntegerField("Status code", null=True)
