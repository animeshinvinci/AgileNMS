from urlparse import urlparse
from django.utils import timezone
from django.conf import settings
from django.db.models import F
from django.template.loader import get_template
from django.core.mail import send_mass_mail
import logging
from celery import task, group
import models
import time
import redis
import json


def alwaysok_handler(url):
    return "ok", "Hello!", [], [], []


def alwayscritical_handler(url):
    return "critical", "Hello!", ["Critical"], [], []


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
    "alwaysok": alwaysok_handler,
    "alwayscritical": alwayscritical_handler,
    "http": http_handler,
    "https": http_handler,
}


@task()
def run_checks():
    # Get check list
    checks = models.Check.objects.filter(enabled=True)

    # Make task group
    task_group = group([run_check.s(check.redis_key, check.url) for check in checks])

    # Run tasks
    async_results = task_group.apply_async()

    # Wait for results
    timeout = getattr(settings, "MONITORING_CHECKRUNNER_TIMEOUT", 120)
    time.sleep(timeout)

    # Get results
    results = [result.get() for result in async_results.results if result.ready()]
    async_results.revoke(terminate=True)

    # Put results into redis
    r = redis.Redis()
    r.mset({
        result[0]: json.dumps({
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
def run_check(redis_key, url):
    # Run
    parsed_url = urlparse(url)
    run_time = timezone.now().isoformat()
    if parsed_url.scheme in handlers:
        return redis_key, run_time, handlers[parsed_url.scheme](url)
    else:
        error_text = "Unrecognised URL scheme" + parsed_url.scheme
        return redis_key, run_time, ("unknown", error_text, ["Unrecognised URL scheme"], [], [])


@task()
def update():
    # Get check list
    checks = models.Check.objects.all()

    # Check if there are any checks
    if len(checks) == 0:
        return

    # Date and time
    time = timezone.now()
    date = time.date()

    # Take a snapshot of all the current states
    r = redis.Redis()
    check_statuses = zip(checks, r.mget([check.redis_key for check in checks]))

    # Loop through checks
    for check, check_status in check_statuses:
        # Parse json for check_status
        if check_status:
            check_status = json.loads(check_status)

    # Reports
        # Get todays report
        try:
            report = models.CheckDailyReport.objects.get(check=check, date=date)
        except models.CheckDailyReport.DoesNotExist:
            report = moels.CheckDailyReport()
            report.check = check
            report.date = date

        # Add maintenance mode
        if check.maintenance_mode:
            report.maintenance_mode = F("maintenance_mode") + 1

        # Add current status
        if not check.enabled:
            report.status_disabled = F("status_disabled") + 1
        else:
            if not check_status:
                report.status_unknown = F("status_unknown") + 1
            else:
                if check_status["status"] == "ok":
                    report.status_ok = F("status_ok") + 1
                elif check_status["status"] == "warning":
                    report.status_warning = F("status_warning") + 1
                elif check_status["status"] == "critical":
                    report.status_critical = F("status_critical") + 1
                elif check_status["status"] == "unknown":
                    report.status_unknown = F("status_unknown") + 1

        # Save report
        report.save()

    # Problems
        if check_status and check.enabled and not check.maintenance_mode:
            # Get a list of problems that are not resolved
            unresolved_problems = check_status["problems"] + check_status["masked_problems"]

            # All problems that are not in unresolved_problems list are resolved
            check.problem_set.filter(end_time=None).exclude(name__in=unresolved_problems).update(end_time=time, send_up_email=True)

            # Add any new problems to the list
            for problem in check_status["problems"]:
                models.Problem.objects.get_or_create(check=check, name=problem, end_time=None, defaults=dict(start_time=time))

         # If disabled or in maintenance mode, mark all problems as resolved but dont send up emails
        if not check.enabled or check.maintenance_mode:
            check.problem_set.filter(end_time=None).update(end_time=time)

    # Metrics
        # TODO


@task
def send_notifications():
    emails_list = []
    email_from = "support@agilenetworking.co.uk"

# Problems
    # Up
    up_problems = models.Problem.objects.filter(send_up_email=True)
    problem_up_template = get_template("monitoring/emails/problem_up.txt")
    for problem in up_problems:
        # Check if there are any email addresses to send to
        addresses = problem.notification_addresses_list
        if len(addresses) > 0:
            # Send email
            email_to = addresses
            email_subject = "".join(["[AgileNMS] INFO: " , problem.check, " no longer has a '" + problem.name + "'"])
            email_message = problem_up_template.render({"problem": problem})
            emails_list.append((email_subject, email_message, email_from, email_to))

        # Clear send_up_email flag
        problem.send_up_email = False
        problem.save()

    # Down
    down_problems = models.Problem.objects.filter(send_down_email=True)
    problem_down_template = get_template("monitoring/emails/problem_down.txt")
    for problem in up_problems:
        # Check if there are any email addresses to send to
        addresses = problem.notification_addresses_list
        if len(addresses) > 0:
            # Send email
            email_to = addresses
            email_subject = "".join(["[AgileNMS] ERROR: " , problem.check, " has a '" + problem.name + "'"])
            email_message = problem_down_template.render({"problem": problem}),
            emails_list.append((email_subject, email_message, email_from, email_to))

        # Clear send_down_email flag
        problem.send_down_email = False
        problem.save()

# Send emails
    send_mass_mail(tuple(emails_list))