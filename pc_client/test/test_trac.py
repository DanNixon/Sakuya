import unittest
import os
from sakuyaclient.trac import TracClient

class TracClientTest(unittest.TestCase):

    def setUp(self):
        self._server = 'http://trac.mantidproject.org/mantid'
        self._cache_filename = 'ticket_cache.txt'
        self._trac = TracClient(self._server, self._cache_filename)

        self._owners = ['Dan Nixon']

    def tearDown(self):
        if os.path.exists(self._cache_filename):
            os.remove(self._cache_filename)

    def test_poll(self):
        status = ['closed', 'verify', 'verifying']
        self._trac.set_subscriptions(self._owners, status)

        columns = ['status', 'summary']
        self._trac.set_data_columns(columns)

        # Cache should be empty so all subscribed tickets should be returned here
        result = self._trac.poll()
        self.assertTrue(len(result) > 0)

        # When polling straight after no ticket changes should be returned
        # May actually return something if a ticket was changed between the two poll requests (although not likely)
        result = self._trac.poll()
        self.assertTrue(len(result) == 0)

if __name__ == '__main__':
    unittest.main()
