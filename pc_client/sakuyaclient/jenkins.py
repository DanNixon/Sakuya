import ast
import urllib
from notification_source import NotificationSource


class JenkinsClient(NotificationSource):
    def __init__(self, server_url, jobs=None):
        self._url = server_url + '/api/python'

        self._last_jobs = dict()
        self._subscribed_jobs = jobs

        # Default to subscribing to all jobs
        if self._subscribed_jobs is None:
            self._subscribed_jobs = self.get_all_job_names()

    def get_data(self):
        url = self._url + '?pretty=true&depth=2&tree=jobs[name,healthReport[*],lastBuild[building,result,culprits[fullName]]]'
        return ast.literal_eval(urllib.urlopen(url).read())

    def get_job(self, job_name, data):
        all_jobs = data['jobs']
        try:
            job = (j for j in all_jobs if j['name'] == job_name).next()
        except StopIteration:
            raise RuntimeError

        return job

    def get_all_job_names(self, data=None):
        if data is None:
            data = self.get_data()

        return [job['name'] for job in data['jobs']]

    def get_job_status(self, job_name, data=None):
        if data is None:
            data = self.get_data()

        job = self.get_job(job_name, data)
        status = dict()

        status['inprogress'] = job['lastBuild']['building']
        status['result'] = job['lastBuild']['result']

        job_culprits = job['lastBuild']['culprits']
        if len(job_culprits) > 0:
            status['culprits'] = [c['fullName'] for c in job_culprits]

        return status

    def get_job_health(self, job_name, data=None):
        if data is None:
            data = self.get_data()

        job = self.get_job(job_name, data)

        return job['healthReport']

    def get_subscribed_jobs(self, data=None):
        if data is None:
            data = self.get_data()

        jobs = dict()
        for job_name in self._subscribed_jobs:
            jobs[job_name] = self.get_job_status(job_name, data)

        return jobs

    def poll(self):
        jobs = self.get_subscribed_jobs()
        jobs_diff = dict()

        if not len(self._last_jobs) < 1:
            for job_name in self._subscribed_jobs:
                current = jobs[job_name]
                previous = self._last_jobs[job_name]

                if cmp(current, previous) is not 0:
                    jobs_diff[job_name] = jobs[job_name]

        self._last_jobs = jobs
        return jobs_diff
