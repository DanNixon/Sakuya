import unittest
import os
from sakuyaclient.jenkins import JenkinsClient
from sakuyaclient.trac import TracClient
from sakuyaclient.notification_centre import NotificationCentre

class NotificationCentreTest(unittest.TestCase):

    def setUp(self):
        self._trac_cache_file = 'ticket_cache.txt'

        self._jenkins = JenkinsClient('http://builds.mantidproject.org', ['develop_clean'])
        self._trac = TracClient('http://trac.mantidproject.org/mantid', self._trac_cache_file)
        self._trac.set_subscriptions(['Dan Nixon'])

        self._notifications = NotificationCentre()
        self._notifications.add_notification_source('tickets', self._trac)
        self._notifications.add_notification_source('builds', self._jenkins)

    def tearDown(self):
        if os.path.exists(self._trac_cache_file):
            os.remove(self._trac_cache_file)

    def test_poll(self):
        results = self._notifications.poll()

        self.assertIsNotNone(results)

        self.assertTrue('tickets' in results)
        self.assertTrue('builds' in results)

        print results

    def test_selective_poll(self):
        results = self._notifications.poll(['builds'])

        self.assertIsNotNone(results)

        self.assertTrue('tickets' not in results)
        self.assertTrue('builds' in results)

        print results

    def test_multi_poll(self):
        # First poll should return diffs
        results = self._notifications.poll()
        for key in results.keys():
            self.assertNotEqual(len(results[key]), 0)

        # Second poll should return no diffs
        results = self._notifications.poll()
        for key in results.keys():
            self.assertEqual(len(results[key]), 0)

if __name__ == '__main__':
    unittest.main()
