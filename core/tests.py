import unittest
import datetime
import models, tasks
from django.utils import timezone


class CheckTestCase(unittest.TestCase):
    def test_poller(self):
        # Create a dummy poller
        newpoller = models.DummyPoller()
        newpoller.value = "Hello World!"
        newpoller.save()

        # Check that the poller saved correctly
        poller = models.DummyPoller.objects.get(uuid=newpoller.uuid)
        self.assertEqual(poller.value, "Hello World!")

        # Post some results, make sure that they post at different times
        poller.post_result("foo", time=(timezone.now() - datetime.timedelta(minutes=1)))
        poller.post_result("bar")

        # Check that they saved correctly
        results = models.DummyPollerResult.objects.filter(check__uuid=poller.uuid)
        self.assertEqual(len(results), 2)

        # Last result must be first in the list
        self.assertEqual(results[0].value, "bar")

    def test_get_recent_results(self):
        # Create a dummy poller
        poller = models.DummyPoller()
        poller.value = "Hello World!"
        poller.save()

        # Post some results, make sure that they post at different times
        poller.post_result("foo", time=(timezone.now() - datetime.timedelta(minutes=1)))
        poller.post_result("bar")
        poller.post_result("baz", time=(timezone.now() - datetime.timedelta(hours=1)))

        # Get the results
        results = poller.get_recent_results()

        # Bar should be first in list then foo. Baz shouldnt be in this list as it is too old
        # This tests result get child
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].get_child().value, "bar")
        self.assertEqual(results[1].get_child().value, "foo")

    def test_get_child(self):
        # Create a dummy poller
        newpoller = models.DummyPoller()
        newpoller.value = "Hello World!"
        newpoller.save()

        # Get the poller again as a check
        check = models.Check.objects.get(uuid=newpoller.uuid)

        # Get the original poller back using get_child
        poller = check.get_child()

        # Get the value
        self.assertEqual(poller.value, "Hello World!")

    def test_should_poll(self):
        # Create a dummy poller
        poller = models.DummyPoller()
        poller.value = "Hello World!"
        poller.save()

        # Pollers should poll when they have no results
        self.assertEqual(poller.should_poll(), True)

        # Pollers should poll when their latest result is too old
        poller.post_result("I'm too old", time=(timezone.now() - datetime.timedelta(seconds=poller.poll_frequency + 100)))
        self.assertEqual(poller.should_poll(), True)

        # Pollers should not poll when they are disabled
        poller.enabled = False
        self.assertEqual(poller.should_poll(), False)
        poller.enabled = True
        self.assertEqual(poller.should_poll(), True)

        # Pollers should not poll when their latest result is new
        poller.post_result("I'm new!", time=(timezone.now() + datetime.timedelta(seconds=poller.poll_frequency + 100)))
        self.assertEqual(poller.should_poll(), False)

    def test_run_pollers_task(self):
        # Create a dummy poller
        poller = models.DummyPoller()
        poller.value = "Hello World!"
        poller.save()

        # Run the run pollers task
        tasks.run_pollers.delay()

        # Check for result
        results = models.DummyPollerResult.objects.filter(check__uuid=poller.uuid)
        self.assertEqual(len(results), 1)

        # Check that result was from the from the dummy poller task
        self.assertEqual(results[0].value, "Greetings from the dummy poller task :)")
