import unittest
from sakuyaclient.trac_api import TracAPI

class TracAPITest(unittest.TestCase):

    def setUp(self):
        self._server = 'http://trac.mantidproject.org/mantid'
        self._trac = TracAPI(self._server)

    def test_basic(self):
        cols = ['id', 'priority', 'status', 'summary']
        owner = ['Dan Nixon']
        status = ['verify', 'verifying']

        result = self._trac.get_query(cols, owner, status)
        print result

if __name__ == '__main__':
    unittest.main()
