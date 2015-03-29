import os
import unittest
from sakuyaclient.NotificationCentre import NotificationCentre


class NotificationCentreTest(unittest.TestCase):

    def setUp(self):
        self._notifications = NotificationCentre(300)


    def test_poll(self):
        results = self._notifications.poll()
        self.assertIsNotNone(results)


    def test_selective_poll(self):
        results = self._notifications.poll()
        self.assertIsNotNone(results)


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
