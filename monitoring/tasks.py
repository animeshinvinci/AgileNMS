from urlparse import urlparse
import logging
from celery import task
import models


def dummy_handler(url):
    return "ok", "Hello! (" + url + ")", []


def dummycritical_handler(url):
    return "critical", "Hello! (" + url + ")", ["In Critical State"]


def http_handler(url):
    import requests
    try:
        response = requests.get(url, timeout=10, verify=False)
    except requests.exceptions.ConnectionError as e:
        return "critical", "Could not connect", ["Connection error"]
    except requests.exceptions.Timeout as e:
        return "critical", "Request timed out", ["Connection error"]

    # Work out status
    status = "ok"
    problems = []
    response_time = int(response.elapsed.total_seconds() * 1000)
    if response_time > 1000:
        status = "warning"
    if response.status_code >= 400 and response.status_code != 401:
        status = "critical"
        problems.append("HTTP error")

    # Return status code and text
    return status, "".join(["HTTP ", str(response.status_code), " ", response.reason, " (", str(response_time), "ms)"]), problems


def ping_handler(url):
    return "unknown", "Ping Handler not implemented", []


def tcp_handler(url):
    return "unknown", "TCP Handler not implemented", []


handlers = {
    "dummy": dummy_handler,
    "dummycritical": dummycritical_handler,
    "http": http_handler,
    "https": http_handler,
}


@task()
def run_checks():
    # Get check list
    checks = models.Check.objects.filter(enabled=True, passive=False)

    # Loop through checks and run them
    for check in checks:
        parsed_url = urlparse(check.url)
        if parsed_url.scheme in handlers:
            status, status_text, problems = handlers[parsed_url.scheme](check.url)
            check.post_result(status=status, status_text=status_text, problems=problems)
        else:
            error_text = "Unrecognised URL scheme: " + parsed_url.scheme
            check.post_result(status="unknown", status_text=error_text, problems=[error_text])
