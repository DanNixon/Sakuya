import os
import unittest
from sakuyaclient.jenkins import JenkinsClient

class JenkinsClientTest(unittest.TestCase):

    def setUp(self):
        self._jobs = {'1':'develop_clean', 'fake':'fake_job'}
        self._server = 'http://builds.mantidproject.org'
        self._cache_filename = 'builds_cache.txt'

        self._jenkins = JenkinsClient(self._server, self._cache_filename, [self._jobs['1']])

    def tearDown(self):
        if os.path.exists(self._cache_filename):
            os.remove(self._cache_filename)

    def test_get_job_names(self):
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

    def test_get_subscribed_jobs(self):
        result = self._jenkins.get_subscribed_jobs()

        try:
            job = (j for j in result if j['name'] == self._jobs['1']).next()
        except StopIteration:
            job = None

        self.assertIsNotNone(job)

    def test_poll(self):
        result = self._jenkins.poll()
        self.assertNotEqual(len(result), 0)

        print result

        result = self._jenkins.poll()
        self.assertEquals(len(result), 0)

        print result

if __name__ == '__main__':
    unittest.main()
