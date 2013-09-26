from celery import task
import models


def poll_ping(hostname):
    return None


def poll_tcp(hostname, port):
    return None


def poll_http(url):
    import requests
    result = requests.get(url)
    return int(result.elapsed.total_seconds() * 1000), result.status_code


@task()
def run_pollers():
    pollers = models.Poller.objects.all()
    for poller in pollers:
        if poller.should_poll():
            run_poller(poller.get_child())


def run_poller(poller):
    if poller.type_name == "Ping Poller":
        ping_response_time = poll_ping(poller.ping_hostname)
        poller.post_result(ping_response_time)
    elif poller.type_name == "TCP Poller":
        tcp_response_time = poll_tcp(poller.tcp_hostname, poller.tcp_port)
        poller.post_result(tcp_response_time)
    elif poller.type_name == "HTTP Poller":
        http_response_time, http_status_code = poll_http(poller.http_url)
        poller.post_result(http_response_time, http_status_code)
