from urlparse import urlparse
from django.utils import timezone
import logging
from celery import task, group
import models
import time
import redis
import json


def dummy_handler(url):
    return "ok", "Hello! (" + url + ")", [], [], []


def dummycritical_handler(url):
    return "critical", "Hello! (" + url + ")", ["In Critical State"], [], []


def http_handler(url):
    import requests
    try:
        response = requests.get(url, timeout=10, verify=False)
    except requests.exceptions.ConnectionError as e:
        return "critical", "Could not connect", ["Connection error"], ["HTTP error"], []
    except requests.exceptions.Timeout as e:
        return "critical", "Request timed out", ["Connection error"], ["HTTP error"], []

    # Work out status
    status = "ok"
    problems = []
    masked_problems = []
    response_time = int(response.elapsed.total_seconds() * 1000)
    if response_time > 1000:
        status = "warning"
    if response.status_code >= 400 and response.status_code != 401:
        status = "critical"
        problems.append("HTTP error")

    # Metrics
    metrics = [
        ("Response time", response_time),
    ]

    # Return status code and text
    return status, "".join(["HTTP ", str(response.status_code), " ", response.reason, " (", str(response_time), "ms)"]), problems, masked_problems, metrics


def ping_handler(url):
    return "unknown", "Ping Handler not implemented", [], [], []


def tcp_handler(url):
    return "unknown", "TCP Handler not implemented", [], [], []


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

    # Make task group
    task_group = group([run_check.s(check.uuid, check.url) for check in checks])

    # Run tasks
    async_results = task_group.apply_async()

    # Wait for results
    time.sleep(4)

    # Get results
    results = [result.get() for result in async_results.results if result.ready()]
    async_results.revoke(terminate=True)

    # Put results into redis
    r = redis.Redis()
    r.mset({
        "check:" + result[0] + ".status": json.dumps({
            "status": result[2][0],
            "status_text": result[2][1],
            "problems": result[2][2],
            "masked_problems": result[2][3],
            "metrics": [{
                    "name": metric[0],
                    "value": metric[1]
                } for metric in result[2][4]
            ],
            "time": result[1],
        }) for result in results
    })


@task()
def run_check(uuid, url):
    # Run
    parsed_url = urlparse(url)
    run_time = timezone.now().isoformat()
    if parsed_url.scheme in handlers:
        return uuid, run_time, handlers[parsed_url.scheme](url)
    else:
        error_text = "Unrecognised URL scheme: " + parsed_url.scheme
        return uuid, run_time, ("unknown", error_text, [error_text], [], [])