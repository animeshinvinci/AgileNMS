from celery import task
import models


@task()
def run_pollers():
    pollers = models.Poller.objects.all()
    for poller in pollers:
        if poller.should_poll():
            poller.get_child().run()
