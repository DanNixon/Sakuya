import ast
import json
import urllib
from notification_source import NotificationSource

class JenkinsClient(NotificationSource):
    """
    Access Jenkins and get updates for a given set of jobs.
    """

    def name(self):
        return 'Jenkins'

    def __init__(self, server_url, cache_filename, jobs=None):
        self._url = server_url + '/api/python'
        self._cache_filename = cache_filename

        self._subscribed_jobs = jobs

        # Default to subscribing to all jobs
        if self._subscribed_jobs is None:
            self._subscribed_jobs = self.get_all_job_names()

    def _write_cache(self, filename, jobs):
        """
        Writes the builds dictionary to file.
        """
        with open(filename, 'w+') as cache_file:
            json.dump(jobs, cache_file)

    def _read_cache(self, filename):
        """
        Reads the ticket dictionary from file.
        """
        try:
            with open(filename, 'r') as cache_file:
                builds = json.load(cache_file)
                return builds
        except IOError:
            return []

    def _get_data(self):
        """
        Gets raw data from Jenkins server.
        """
        url = self._url + '?pretty=true&depth=2&tree=jobs[name,healthReport[*],lastBuild[building,result,culprits[fullName]]]'
        return ast.literal_eval(urllib.urlopen(url).read())

    def _get_raw_job(self, job_name, data):
        """
        Gets raw data for a given job.
        """
        all_jobs = data['jobs']
        try:
            job = (j for j in all_jobs if j['name'] == job_name).next()
        except StopIteration:
            raise RuntimeError

        return job

    def get_all_job_names(self, data=None):
        """
        Gets the name of all jobs on the server.
        """
        if data is None:
            data = self._get_data()

        return [job['name'] for job in data['jobs']]

    def get_job_status(self, job_name, data=None):
        """
        Gets the status of a given job.
        """
        if data is None:
            data = self._get_data()

        job = self._get_raw_job(job_name, data)
        status = dict()

        status['inprogress'] = job['lastBuild']['building']
        status['result'] = job['lastBuild']['result']

        if status['result'] is not None:
            status['result'] = status['result'].lower()
        else:
            status['result'] = 'in progress'

        job_culprits = job['lastBuild']['culprits']
        if len(job_culprits) > 0:
            status['culprits'] = [c['fullName'] for c in job_culprits]

        return status

    def get_job_health(self, job_name, data=None):
        """
        Gets the health data for a given job.
        """
        if data is None:
            data = self._get_data()

        job = self._get_raw_job(job_name, data)

        return job['healthReport']

    def get_subscribed_jobs(self, data=None):
        """
        Gets data for all subscribed jobs.
        """
        if data is None:
            data = self._get_data()

        jobs = list()
        for job_name in self._subscribed_jobs:
            job_data = self.get_job_status(job_name, data)
            job_data['name'] = job_name
            jobs.append(job_data)

        return jobs

    def poll(self):
        """
        Updates the local job list from Jenkins and returns jobs with changed status.
        """
        new = self.get_subscribed_jobs()
        old = self._read_cache(self._cache_filename)
        jobs_diff = list()

        for job in new:
            try:
                old_job = (j for j in old if j['name'] == job['name']).next()
            except StopIteration:
                old_job = None

            if old_job is None:
                jobs_diff.append(job)
                continue

            if job['result'] != old_job['result']:
                job['last_result'] = old_job['result']
                jobs_diff.append(job)
                continue

        self._write_cache(self._cache_filename, new)
        return jobs_diff
