import abc


class WriterBase(abc.ABC):

    @abc.abstractmethod
    def set_pipe(self, pipe):
        pass

    @abc.abstractmethod
    def parallel_write_end_loop(self) -> None:
        pass

    @abc.abstractmethod
    def is_running(self):
        pass

    @abc.abstractmethod
    def is_stopped(self):
        pass

    @abc.abstractmethod
    def start_running(self):
        pass

    @abc.abstractmethod
    def __call__(self):
        pass


class ReaderBase(abc.ABC):

    @abc.abstractmethod
    def set_pipe(self, pipe):
        pass

    @abc.abstractmethod
    def is_running(self):
        pass

    @abc.abstractmethod
    def is_stopped(self):
        pass

    @abc.abstractmethod
    def start_running(self):
        pass

    @abc.abstractmethod
    def __call__(self):
        pass
