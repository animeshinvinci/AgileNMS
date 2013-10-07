import unittest
import datetime
import json
import models, tasks
from django.utils import timezone


class DatabaseTests(unittest.TestCase):
    def test_monitor(self):
        # Create an HTTP monitor
        monitor = models.Monitor()
        monitor.protocol = "http"
        monitor.data = json.dumps({
            "host": "www.google.co.uk",
            "port": 80,
        })
        monitor.save()

        # Add a homepage check
        monitor.add_check(data=json.dumps({
            "method": "GET",
            "path": "/"
        }))

        # Check that the check went in correctly
        checks = monitor.check_set.all()
        self.assertEqual(len(checks), 1)
        check = checks[0]

        # Post a result
        check.post_result(data=json.dumps({
            "status_code": 200,
            "elapsed": 1,
        }))

        # Post an old result
        check.post_result(data=json.dumps({
            "status_code": 200,
            "elapsed": 2,
        }), time=(timezone.now() - datetime.timedelta(minutes=1)))

        # Post a very old result
        check.post_result(data=json.dumps({
            "status_code": 200,
            "elapsed": 3,
        }), time=(timezone.now() - datetime.timedelta(hours=1)))

        # Check the get_recent results function
        # This should return two results, the new result first then the old result
        # The very old result shouldnt be returned
        results = check.get_recent_results()
        self.assertEqual(len(results), 2)
        self.assertEqual(json.loads(results[0].data)["elapsed"], 1)
        self.assertEqual(json.loads(results[1].data)["elapsed"], 2)

    def test_groups(self):
        def create_group(monitor_count):
            # Create a group
            group = models.Group()
            
            # Create some monitors
            for i in range(monitor_count):
                monitor = models.Monitor()
                monitor.protocol = "dummy"
                monitor.group = group
                monitor.save()
                
            return group
            
        group_a = create_group(3)
        group_b = create_group(3)
        group_c = create_group(3)
        
        self.assertEqual(group_a.monitor_set.count(), 3)
        # TODO
        
