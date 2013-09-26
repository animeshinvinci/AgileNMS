import unittest
import datetime
import models, tasks
from django.utils import timezone


class CheckTestCase(unittest.TestCase):
    def test_ping_poller(self):
        ping = models.PingPoller()
        ping.ping_hostname = "www.google.co.uk"
        ping.save()

        ping.post_result(None)

        # Test that everything was saved correctly
        newping = models.PingPoller.objects.get(uuid=ping.uuid)
        results = models.PingPollerResult.objects.filter(check__uuid=ping.uuid)
        self.assertEqual(len(results), 1)

        # Some extra checks
        result = results[0]
        self.assertEqual(result.status, 3)

        newping.post_result(600)
        results = models.PingPollerResult.objects.filter(check__uuid=ping.uuid)
        self.assertEqual(len(results), 2)

    def test_get_child(self):
        # Create a ping poller
        ping = models.PingPoller()
        ping.ping_hostname = "www.test_get_child.com"
        ping.save()

        # Get the check for the ping poller
        check = models.Check.objects.get(uuid=ping.uuid)
        newping = check.get_child()

        self.assertEqual(newping.ping_hostname, ping.ping_hostname)

    def test_should_poll(self):
        # Create a ping poller
        ping = models.PingPoller()
        ping.ping_hostname = "www.test_should_poll.com"
        ping.save()

        self.assertEqual(ping.should_poll(), True)

        ping.post_result(100, time=timezone.now() - datetime.timedelta(seconds=ping.poll_frequency + 100))
        self.assertEqual(ping.should_poll(), True)

        ping.post_result(200, time=timezone.now() - datetime.timedelta(seconds=ping.poll_frequency - 100))
        self.assertEqual(ping.should_poll(), False)

    def test_run_pollers_task(self):
        # Create some pollers
        uuids = []
        for i in range(1, 10):
            poller = models.PingPoller()
            poller.ping_hostname = "host" + str(i)
            poller.save()
            uuids.append(poller.uuid)

        # Create a disabled poller
        disabled_poller = models.PingPoller()
        disabled_poller.ping_hostname = "donotpoll"
        disabled_poller.enabled = False
        disabled_poller.save()

        # Run run_pollers task
        result = tasks.run_pollers.delay()
        result.wait()

        # Check the task was successful
        self.assertEqual(result.successful(), True)

        # Check that a result was inserted for each poller
        for uuid in uuids:
            result_count = models.PingPollerResult.objects.filter(check__uuid=uuid).count()
            self.assertEqual(result_count, 1)

        # Make sure the disabled poller has no results
        result_count = models.PingPollerResult.objects.filter(check__uuid=disabled_poller.uuid).count()
        self.assertEqual(result_count, 0)
