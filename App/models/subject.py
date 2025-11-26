class Subject:
    """
    Subject mixin for objects that notify Observers of updates.
    Classes that inherit this mixin must implement add_observer, remove_observer and notify_observers.
    """
    
    def add_observer(self, observer):
        """
        if observer not in self._observers:
            self._observers.append(observer)
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement the add_observer(observer) method."
        )
    
    def remove_observer(self, observer):
        """
        if observer in self._observers:
            self._observers.remove(observer)
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement the remove_observer(observer) method."
        )

    def notify_observers(self, message):
        """
        for observer in self._observers:
            observer.update(message)
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement the notify_observers(message) method."
        )