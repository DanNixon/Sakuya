from abc import ABCMeta, abstractmethod


class NotificationSink():
    """
    Abstract class for all notification sinks/handlers.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def handle(self, updates):
        """
        Used to handle new updates retrieved by NotificationCentre.
        """
        raise NotImplementedError('No concrete implementation!')
