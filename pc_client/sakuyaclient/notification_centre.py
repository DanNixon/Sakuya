import threading
import time
from trac import TracClient
from jenkins import JenkinsClient

class NotificationCentre(object):
    """
    Manages notifications from all sources and distributes them to sinks.
    """

    def __init__(self, update_interval):
        self._sources = dict()
        self._sinks = dict()

        self._update_interval = update_interval
        self._update_thread = None

    def start(self, join=True):
        self._update_thread = threading.Thread(target=self._update, args=())
        self._update_thread.start()
        if join:
            self._update_thread.join()

    def add_notification_source(self, source_id, source):
        """
        Adds a new notification source.
        """
        if source_id in self._sources:
            raise ValueError('Source with given ID already exists')

        self._sources[source_id] = source

    def add_notification_sink(self, sink_id, sink):
        """
        Adds a new notification sink.
        """
        if sink_id in self._sinks:
            raise ValueError('Sink with given ID already exists')

        self._sinks[sink_id] = sink

    def poll(self, source_ids=None):
        """
        Polls each notification source and returns changed items.
        """
        if source_ids is None:
            source_ids = self._sources.keys()

        diffs = dict()
        for source_id in source_ids:
            diffs[source_id] = (self._sources[source_id].name(), self._sources[source_id].poll())

        return diffs

    def _update(self):
        """
        Handles getting new data at a given interval.
        """
        while(1):
            diffs = self.poll()

            for sink_id in self._sinks.keys():
                self._sinks[sink_id].handle(diffs)

            time.sleep(self._update_interval)
