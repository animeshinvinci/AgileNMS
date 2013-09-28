import unittest
import datetime
import models, tasks
from django.utils import timezone


class CheckTestCase(unittest.TestCase):
    def test_poller(self):
        # Create a dummy poller
        poller = models.DummyPoller()
        poller.value = "Hello World!"
        poller.save()

        # Check that the poller saved correctly
        poller = models.DummyPoller.objects.get(uuid=poller.uuid)
        self.assertEqual(poller.value, "Hello World!")

        # Post some results
        poller.post_result("foo")
        poller.post_result("bar")

        # Check that they saved correctly
        results = models.DummyPollerResult.objects.filter(check__uuid=poller.uuid)
        self.assertEqual(len(results), 2)

        # Last result must be first in the list
        self.assertEqual(results[0].value, "bar")
