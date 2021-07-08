import threading


class AtomicBool:

    def __init__(self, value=False):
        self.__value = value
        self.__lock = threading.Lock()

    def set_true(self):
        with self.__lock:
            self.__value = True

    def set_false(self):
        with self.__lock:
            self.__value = False

    def get_truth_unsafe(self):
        """
        Returns the truth of the boolean value. Though the lock prevents race condition, the actual value could have
        been modified a few milliseconds after the retrieval.
        :return:
        """
        with self.__lock:
            result = self.__value
        return result

    def get_truth_remain_locked(self):
        """
        Warning: this method does not release the lock. The lock may have to be released externally.
        :return:
        """
        self.__lock.acquire(blocking=True)
        return self.__value

    def unlock_after_get_truth(self):
        self.__lock.release()
