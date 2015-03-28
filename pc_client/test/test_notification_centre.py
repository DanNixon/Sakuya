import os
import unittest
from sakuyaclient.sources.JenkinsSource import JenkinsSource
from sakuyaclient.sources.TracSource import TracSource
from sakuyaclient.NotificationCentre import NotificationCentre

class NotificationCentreTest(unittest.TestCase):

    def setUp(self):
        self._trac_cache_file = 'ticket_cache.txt'
        self._builds_cache_file = 'builds_cache.txt'

        self._jenkins = JenkinsSource('http://builds.mantidproject.org', self._builds_cache_file, ['develop_clean'])
        self._trac = TracSource('http://trac.mantidproject.org/mantid', self._trac_cache_file)
        self._trac.set_subscriptions(['Dan Nixon'])

        self._notifications = NotificationCentre(300)
        self._notifications.add_notification_source('tickets', self._trac)
        self._notifications.add_notification_source('builds', self._jenkins)

    def tearDown(self):
        if os.path.exists(self._trac_cache_file):
            os.remove(self._trac_cache_file)

        if os.path.exists(self._builds_cache_file):
            os.remove(self._builds_cache_file)

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
            self.assertNotEqual(len(results[key][1]), 0)

        # Second poll should return no diffs
        results = self._notifications.poll()
        for key in results.keys():
            self.assertEqual(len(results[key][1]), 0)

if __name__ == '__main__':
    unittest.main()
