from abc import ABC, abstractmethod

class AbstractListener(ABC):

    def __init__(self, host, port):
        self._host = host
        self._post = port

    @abstractmethod
    def listen(self):
        pass


