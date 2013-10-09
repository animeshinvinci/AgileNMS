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

    def test_result(self):
        # Create a check
        check = models.Check()
        check.url = "dummy://hello"
        check.save()

        # Post some check results
        check.post_result(status="ok", status_text="old", time=timezone.now() - datetime.timedelta(hours=1))
        check.post_result(status="critical", status_text="new", time=timezone.now() - datetime.timedelta(minutes=1))
        check.post_result(status="warning", status_text="late", time=timezone.now() - datetime.timedelta(minutes=3))

        # Check should be in critical state
        self.assertEqual(check.get_status(), "critical")

        # Recent results should return the new and late statuses
        results = check.get_recent_results()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].status_text, "new")
        self.assertEqual(results[1].status_text, "late")

    def test_problem(self):
        # Create a check
        check = models.Check()
        check.url = "dummy://hello"
        check.save()

        # Post a bad result
        check.post_result(status="critical", status_text="Oh no!", problems=["Something went wrong"])

        # This should've made a problem
        self.assertEqual(check.problem_set.count(), 1)

        # Post another bad result
        check.post_result(status="critical", status_text="Oh no!", problems=["Something went wrong"])

        # As the problem had the same name, there should still only be one problem
        self.assertEqual(check.problem_set.count(), 1)

        # Post a result with two problems
        check.post_result(status="critical", status_text="Oh no!", problems=["Something went wrong", "Something else went wrong"])

        # There should be two problems now
        self.assertEqual(check.problem_set.count(), 2)

        # Post a result with the new problem only, this should mark the old one as resolved
        check.post_result(status="critical", status_text="Oh no!", problems=["Something else went wrong"])

        # Post a result with both problems
        check.post_result(status="critical", status_text="Oh no!", problems=["Something went wrong", "Something else went wrong"])

        # There should be three problems now as the old one would be recreated
        self.assertEqual(check.problem_set.count(), 3)

        # Put check in maintenance mode
        check.maintenance_mode = True
        check.save()

        # This should've cleared all problems
        self.assertEqual(check.problem_set.filter(end_time=None).count(), 0)

        # Try adding a new problem, this shouldnt work
        check.post_result(status="critical", status_text="Oh no!", problems=["This shouldnt work"])
        self.assertEqual(check.problem_set.count(), 3)

        # Disable maintenance mode
        check.maintenance_mode = False
        check.save()

        # Post a result with both problems
        check.post_result(status="critical", status_text="Oh no!", problems=["Something went wrong", "Something else went wrong"])

        # Both problems should be re added but in different objects
        self.assertEqual(check.problem_set.count(), 5)
        self.assertEqual(check.problem_set.filter(end_time=None).count(), 2)
