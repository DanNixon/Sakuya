import unittest
from sakuyaclient.jenkins import JenkinsClient

class JenkinsClientTest(unittest.TestCase):

    def setUp(self):
        self._jobs = {'1':'develop_clean', 'fake':'fake_job'}
        self._server = 'http://builds.mantidproject.org'
        self._jenkins = JenkinsClient(self._server)

    def test_get_jpb_names(self):
        result = self._jenkins.get_all_job_names()
        self.assertIsNotNone(result)
        self.assertTrue(type(result) is list)

        print result

    def test_get_status(self):
        result = self._jenkins.get_job_status(self._jobs['1'])
        self.assertIsNotNone(result)

        print result

    def test_get_status_fake_job(self):
        with self.assertRaises(RuntimeError):
            self._jenkins.get_job_status(self._jobs['fake'])

    def test_get_health(self):
        result = self._jenkins.get_job_health(self._jobs['1'])
        self.assertIsNotNone(result)

        print result

    def test_get_health_fake_job(self):
        with self.assertRaises(RuntimeError):
            self._jenkins.get_job_health(self._jobs['fake'])

if __name__ == '__main__':
    unittest.main()
