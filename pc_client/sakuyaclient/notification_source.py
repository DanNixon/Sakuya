from abc import ABCMeta, abstractmethod

class NotificationSource():
    """
    Abstract class for all notification sources.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def poll():
        """
        Used to get a set of changes between data retrieved in this call and the last.
        """
        raise NotImplemented('No concrete implementation!')
