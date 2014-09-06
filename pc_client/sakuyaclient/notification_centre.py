from trac import TracClient
from jenkins import JenkinsClient

class NotificationCentre(object):
    """
    Manages notifications from all sources.
    """

    def __init__(self):
        self._sources = dict()

    def add_notification_source(self, source_id, source):
        """
        Adds a new notification source.
        """
        if source_id in self._sources:
            raise ValueError('Source with given ID already exists')

        self._sources[source_id] = source

    def poll(self, source_ids=None):
        """
        Polls each notification source and returns changed items.
        """
        if source_ids is None:
            source_ids = self._sources.keys()

        diffs = dict()
        for source_id in source_ids:
            diffs[source_id] = self._sources[source_id].poll()

        return diffs

