from celery import task
import models


def poll_ping(hostname):
    return None


def poll_tcp(hostname, port):
    return None


def poll_http(url):
    return None, None


@task()
def run_pollers():
    pollers = models.Poller.objects.all()
    for poller in pollers:
        if poller.should_poll():
            run_poller.delay(poller.uuid)


@task()
def run_poller(uuid):
    poller = models.Poller.objects.get(uuid=uuid).get_child()

    if poller.type_name == "Ping Poller":
        poller.post_result(poll_ping(poller.ping_hostname))
    elif poller.type_name == "TCP Poller":
        poller.post_result(poll_tcp(poller.tcp_hostname, poller.tcp_port))
    elif poller.type_name == "HTTP Poller":
        poller.post_result(poll_http(poller.http_url))
