import unittest
from sakuyaclient.sources.TracAPI import TracAPI

class TracAPITest(unittest.TestCase):

    def setUp(self):
        self._server = 'http://trac.mantidproject.org/mantid'
        self._trac = TracAPI(self._server)

    def test_basic(self):
        cols = ['id', 'priority', 'status', 'summary']
        owner = ['Dan Nixon']
        status = ['assigned']

        tickets = self._trac.get_query(cols, owner, status)

        # Ensure tickets are returned
        # I'm fairly certain I will alsways have at least one ticket assigned to me
        self.assertTrue(len(tickets) > 0)

        for t in tickets:
            self.assertEquals(t['status'], 'assigned')
            self.assertIsNotNone(t['id'])
            self.assertIsNotNone(t['priority'])
            self.assertIsNotNone(t['summary'])

        print tickets

if __name__ == '__main__':
    unittest.main()
