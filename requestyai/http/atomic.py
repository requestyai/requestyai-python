import threading


class AtomicFlag:
    def __init__(self, initial_value: bool = False):
        self._value = initial_value
        self._lock = threading.Lock()

    def get_and_set(self) -> bool:
        with self._lock:
            current = self._value
            self._value = True
            return current

    def is_set(self):
        with self._lock:
            return self._value
