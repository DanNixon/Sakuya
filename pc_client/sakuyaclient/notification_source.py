from abc import ABCMeta, abstractmethod

class NotificationSource():

    __metaclass__ = ABCMeta

    @abstractmethod
    def poll():
        raise NotImplemented('No concrete implementation!')
