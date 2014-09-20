from abc import ABCMeta, abstractmethod


class NotificationSource():
    """
    Abstract class for all notification sources.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def poll(self):
        """
        Used to get a set of changes between data retrieved in this call and the last.
        """
        raise NotImplementedError('No concrete implementation!')

    @abstractmethod
    def name(self):
        """
        Returns a unique name for the source type.
        """
        raise NotImplementedError('No concrete implementation!')
