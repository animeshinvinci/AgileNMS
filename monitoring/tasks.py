from urlparse import urlparse
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mass_mail
import logging
from celery import task, group
import models
import redis
import json


def alwaysok_handler(url):
    return {
        'status': 'ok',
        'status_text': "Always OK",
        'problems': [],
        'masked_problems': [],
        'metrics': [],
    }


def alwayscritical_handler(url):
    return {
        'status': 'critical',
        'status_text': "Always Critical",
        'problems': ["Critical"],
        'masked_problems': [],
        'metrics': [],
    }


def http_handler(url):
    import requests
    try:
        response = requests.get(url, timeout=10, verify=False)
    except requests.exceptions.ConnectionError as e:
        return {
            'status': 'critical',
            'status_text': "Could not connect",
            'problems': ["Connection error"],
            'masked_problems': ["HTTP error"],
            'metrics': [],
        }
    except requests.exceptions.Timeout as e:
        return {
            'status': 'critical',
            'status_text': "Request timed out",
            'problems': ["Connection error"],
            'masked_problems': ["HTTP error"],
            'metrics': [],
        }

    # Status
    status = 'ok'
    problems = []
    masked_problems = []
    response_time = int(response.elapsed.total_seconds() * 1000)
    if response_time > 1000:
        status = 'warning'
    if response.status_code >= 400 and response.status_code != 401:
        status = 'critical'
        problems.append("HTTP error")

    # Status text
    status_text = " ".join([
        "HTTP",
        str(response.status_code),
        response.reason,
        "(" + str(response_time) + "ms)"
    ])

    # Metrics
    metrics = [
        {
            'name': "Response time",
            'value': response_time,
        },
    ]

    # Return status code and text
    return {
        'status': status,
        'status_text': status_text,
        'problems': problems,
        'masked_problems': masked_problems,
        'metrics': metrics,
    }


def ping_handler(url):
    return {
        'status': 'unknown',
        'status_text': "Ping Handler not implemented",
        'problems': [],
        'masked_problems': [],
        'metrics': [],
    }


def tcp_handler(url):
    return {
        'status': 'unknown',
        'status_text': "TCP Handler not implemented",
        'problems': [],
        'masked_problems': [],
        'metrics': [],
    }


handlers = {
    'alwaysok': alwaysok_handler,
    'alwayscritical': alwayscritical_handler,
    'http': http_handler,
    'https': http_handler,
}


@task()
def submit_result(check_id, result, time):
    # Get check
    check = models.Check.objects.get(id=check_id)

    # Check that this check is enabled
    if not check.enabled:
        return

    # Submit to redis
    r = redis.StrictRedis()
    r.set(check.redis_key, json.dumps(result))

    # Problems
    if not check.maintenance_mode:
        # Get a list of problems that are not resolved
        unresolved_problems = result['problems'] + result['masked_problems']

        # All problems that are not in unresolved_problems list are resolved
        check.problem_set.filter(end_time=None).exclude(name__in=unresolved_problems).update(end_time=time, send_up_email=True)

        # Add any new problems to the list
        for problem in result['problems']:
            models.Problem.objects.get_or_create(check=check, name=problem, end_time=None, defaults=dict(start_time=time))

    # Metrics
    # TODO


@task()
def run_checks():
    # Check all checks that are enabled
    for check in models.Check.objects.filter(enabled=True):
        # Save check time
        check_time = timezone.now()

        # Get result
        scheme = urlparse(check.url).scheme
        if scheme in handlers:
            result = handlers[scheme](check.url)
        else:
            error_text = "Unrecognised URL scheme: '" + scheme + "'"
            result = dict('unknown', error_text, ["Unrecognised URL scheme"], [], [])

        # Add time to the result
        result['time'] = check_time.isoformat()

        # Submit result
        submit_result.delay(check.id, result, check_time)


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
    r = redis.StrictRedis()
    check_statuses = zip(checks, r.mget([check.redis_key for check in checks]))

    # Loop through checks
    for check, check_status in check_statuses:
        # Parse json for check_status
        if check_status:
            check_status = json.loads(check_status)

    # Reports
        # Get todays report
        report, report_created = models.CheckDailyReport.objects.get_or_create(check=check, date=date)

        # Add maintenance mode
        if check.maintenance_mode:
            report.maintenance_mode += 1

        # Add current status
        if not check.enabled:
            report.status_disabled += 1
        else:
            if not check_status:
                report.status_unknown += 1
            else:
                if check_status['status'] == 'ok':
                    report.status_ok += 1
                elif check_status['status'] == 'warning':
                    report.status_warning += 1
                elif check_status['status'] == critical:
                    report.status_critical += 1
                elif check_status['status'] == 'unknown':
                    report.status_unknown += 1

        # Save report
        report.save()

    # Problems
        # If disabled or in maintenance mode, mark all problems as resolved
        if not check.enabled or check.maintenance_mode:
            check.problem_set.filter(end_time=None).update(end_time=time)


@task()
def send_notifications():
    emails_list = []
    email_from = 'ANS Support <support@agilenetworking.co.uk>'

# Problems
    # Up
    up_problems = models.Problem.objects.filter(send_up_email=True)
    for problem in up_problems:
        # Check if there are any email addresses to send to
        addresses = problem.notification_addresses_list
        if len(addresses) > 0:
            # Send email
            email_to = addresses
            email_subject = "".join(["[AgileNMS] INFO: " , str(problem.check), " no longer has a problem '" + problem.name + "'"])
            email_message = render_to_string('monitoring/emails/problem_up.txt', {'problem': problem})
            emails_list.append((email_subject, email_message, email_from, email_to))

        # Clear send_up_email flag
        problem.send_up_email = False
        problem.save()

    # Down
    down_problems = models.Problem.objects.filter(send_down_email=True)
    for problem in down_problems:
        # Check if there are any email addresses to send to
        addresses = problem.notification_addresses_list
        if len(addresses) > 0:
            # Send email
            email_to = addresses
            email_subject = "".join(["[AgileNMS] ERROR: " , str(problem.check), " has a problem '" + problem.name + "'"])
            email_message = render_to_string('monitoring/emails/problem_down.txt', {'problem': problem})
            emails_list.append((email_subject, email_message, email_from, email_to))

        # Clear send_down_email flag
        problem.send_down_email = False
        problem.save()

    print tuple(emails_list)

    # Send emails
    send_mass_mail(tuple(emails_list))