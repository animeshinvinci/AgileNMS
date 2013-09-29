from django.db import models
from django.utils import timezone
from core.models import Poller, PollerResult


class PingPoller(Poller):
    ping_hostname = models.CharField("Hostname", max_length=200)
    ping_response_time_warning_threshold = models.IntegerField("Warning Threshold", null=True, blank=True, default=500)
    ping_response_time_error_theshold = models.IntegerField("Error Threshold", null=True, blank=True, default=1000)

    def __unicode__(self):
        return self.ping_hostname


class TCPPoller(Poller):
    tcp_hostname = models.CharField("Hostname", max_length=200)
    tcp_port = models.PositiveIntegerField("Port")
    tcp_response_time_warning_threshold = models.IntegerField("Warning Threshold", null=True, blank=True, default=500)
    tcp_response_time_error_theshold = models.IntegerField("Error Threshold", null=True, blank=True, default=1000)

    def __unicode__(self):
        return self.tcp_hostname + ":" + str(self.tcp_port)


class HTTPPoller(Poller):
    http_url = models.URLField("URL")
    http_response_time_warning_threshold = models.IntegerField("Warning Threshold", null=True, blank=True, default=500)
    http_response_time_error_theshold = models.IntegerField("Error Threshold", null=True, blank=True, default=1000)

    def run(self):
        import requests
        result = requests.get(self.http_url)
        response_time = int(result.elapsed.total_seconds() * 1000)
        status_code = result.status_code
        self.post_result({"response_time": response_time, "status_code": status_code})

    def __unicode__(self):
        return self.http_url


class PingPollerResult(PollerResult):
    ping_response_time = models.IntegerField("Response time", null=True)

    def setup(self, data):
        self.ping_response_time = data["ping_response_time"]
PingPoller.result_class = PingPollerResult


class TCPPollerResult(PollerResult):
    tcp_response_time = models.IntegerField("Response time", null=True)

    def setup(self, data):
        self.tcp_response_time = data["tcp_response_time"]
TCPPoller.result_class = TCPPollerResult


class HTTPPollerResult(PollerResult):
    http_response_time = models.IntegerField("Response time", null=True)
    http_status_code = models.IntegerField("Status code", null=True)

    def setup(self, data):
        self.http_response_time = data["http_response_time"]
        self.http_status_code = data["http_status_code"]
HTTPPoller.result_class = HTTPPollerResult
