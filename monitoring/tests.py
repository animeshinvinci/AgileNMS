import unittest
import models
from django.utils import timezone


class CheckTestCase(unittest.TestCase):
    def test_ping_poller(self):
        ping = models.PingPoller()
        ping.ping_hostname = "www.google.co.uk"
        ping.save()

        ping.post_result(None)

        # Test that everything was saved correctly
        newping = models.PingPoller.objects.get(uuid = ping.uuid)
        results = models.PingPollerResult.objects.filter(check__uuid = ping.uuid)
        self.assertEqual(len(results), 1)

        # Some extra checks
        result = results[0]
        self.assertEqual(result.number, 1)
        self.assertEqual(result.status, 3)
        self.assertEqual(newping.last_result, 1)

        newping.post_result(600)
        results = models.PingPollerResult.objects.filter(check__uuid = ping.uuid)
        self.assertEqual(len(results), 2)
        self.assertEqual(newping.last_result, 2)
