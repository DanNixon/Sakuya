import logging
import threading
import time


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
        logging.getLogger(__name__).info('Added source with ID %s', source_id)

    def add_notification_sink(self, sink_id, sink):
        """
        Adds a new notification sink.
        """
        if sink_id in self._sinks:
            raise ValueError('Sink with given ID already exists')

        self._sinks[sink_id] = sink
        logging.getLogger(__name__).info('Added sink with ID %s', sink_id)

    def poll(self, source_ids=None):
        """
        Polls each notification source and returns changed items.
        """
        if source_ids is None:
            source_ids = self._sources.keys()

        diffs = dict()
        for source_id in source_ids:
            try:
                logging.getLogger(__name__).info('Polling source with ID %s', source_id)
                diffs[source_id] = (self._sources[source_id].name(), self._sources[source_id].poll())
                logging.getLogger(__name__).info('Got %d new notifications from %s', len(diffs[source_id][1]), source_id)
            except Exception as exc:
                logging.getLogger(__name__).error('Could not poll source %s: %s', source_id, str(exc))

        return diffs

    def _update(self):
        """
        Handles getting new data at a given interval.
        """
        while True:
            diffs = self.poll()

            for sink_id in self._sinks.keys():
                try:
                    logging.getLogger(__name__).info('Sending notifications to sink with ID %s', sink_id)
                    self._sinks[sink_id].handle(diffs)
                except Exception as exc:
                    logging.getLogger(__name__).error('Sink %s failed to handle notifications: %s', sink_id, str(exc))

            time.sleep(self._update_interval)
