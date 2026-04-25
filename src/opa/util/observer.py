from abc import ABC, abstractmethod


class EventType:

    SIGNAL: str = "SIGNAL"
    UPDATE: str = "UPDATE"


class Observer(ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """

    @abstractmethod
    def update(self) -> None:
        """
        Receive update from subject.
        @param subject: a Subject object
        @return: None

        """
        pass


class Subject(ABC):
    """
    The Subject interface declares a set of methods for managing subscribers.
    """
    @abstractmethod
    def attach(self, observer: Observer) -> None:
        """
        Attach an observer object to a subject.
        @param observer: an object that needs to be notified from an event.
        @return: None
        """
        pass

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        """
        Detach an observer object to a subject.
        @param observer: an object that needs to be notified from an event.
        @return: None
        """
        pass

    @abstractmethod
    def notify(self) -> None:
        """
        Notify all observers about an event.
        @return: Nones
        """