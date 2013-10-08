import unittest
import datetime
import json
import models, tasks
from django.utils import timezone


class DatabaseTests(unittest.TestCase):
    def test_check(self):
        # Create a check
        check = models.Check()
        check.url = "dummy://hello"
        check.save()

        # Get the check
        checkb = models.Check.objects.get(pk=check.pk)
        self.assertEqual(checkb.url, "dummy://hello")

        # Post some check results
        check.post_result(status="ok", status_text="old", time=timezone.now() - datetime.timedelta(hours=1))
        check.post_result(status="critical", status_text="new", time=timezone.now() - datetime.timedelta(minutes=1))
        checkb.post_result(status="warning", status_text="late", time=timezone.now() - datetime.timedelta(minutes=3))

        # Check should be in critical state
        self.assertEqual(check.get_status(), "critical")

        # Recent results should return the new and late statuses
        results = check.get_recent_results()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].status_text, "new")
        self.assertEqual(results[1].status_text, "late")
