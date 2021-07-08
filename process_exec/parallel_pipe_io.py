import errno
import queue
import threading
import os
import time

from process_exec.parallel_pipe_io_base import WriterBase, ReaderBase
from process_exec.queued_io_channel import ReadIOChannel, WriteIOChannel
from process_exec.util.atomic_bool import AtomicBool

# TODO: These parallel read write class instances can only be run once: raise error when attempted to run again.


class ParallelWritePipe(WriterBase):

    def __assert_pip_blocking(self):
        if not os.get_blocking(self.__pipe.fileno()):
            raise RuntimeError("Only blocking processes are handled by the \"ParallelWritePipe\" class")

    @staticmethod
    def __assert_out_data(out_data):
        if not isinstance(out_data, ReadIOChannel):
            raise RuntimeError("Expected an instance of " + str(type(ReadIOChannel)) + " but " + str(type(out_data)) +
                               " was given")

    def __init__(self, out_data: ReadIOChannel, pipe=None, _io_timeout=0.01, _io_time_delay=0.001):

        WriterBase.__init__(self)

        self.__pipe = pipe

        ParallelWritePipe.__assert_out_data(out_data)
        self.__out_data = out_data

        self.__io_timeout = _io_timeout

        self.__io_time_delay = _io_time_delay

        if pipe is not None:
            self.__assert_pip_blocking()

        self.__call_lock = threading.Lock()

        self.__write_loop = AtomicBool(value=True)

        # self.__exec_started = False
        self.__exec_started = AtomicBool(value=False)
        self.__exec_stopped = AtomicBool(value=False)

    def set_pipe(self, pipe):
        if self.__exec_started.get_truth_unsafe():
            raise RuntimeError("Attempt to modify the pipe in a running execution is forbidden")
        self.__pipe = pipe
        self.__assert_pip_blocking()

    def parallel_write_end_loop(self):
        self.__write_loop.set_false()

    def is_running(self):
        return self.__exec_started.get_truth_unsafe()

    def is_stopped(self):
        """

        :return: If the execution had stopped
        """

        # The ``unsafe" get method is fine for this case because, once the execution is marked stopped it will never
        # be started again.
        return self.__exec_stopped.get_truth_unsafe()

    def start_running(self):
        self.__call_lock.release()

    def __call__(self):
        self.__call_lock.acquire(blocking=True)
        self.__call_lock.acquire(blocking=True)

        self.__exec_started.set_true()
        # self.__exec_started = True

        if self.__pipe is None:
            raise TypeError("Expected a valid pipe, None given")

        # TODO: this locking method must be changed to avoid the thread to sleep for __io_time_delay.
        # Waiting for the thread to resume after __io_time_delay amount of time is not a good design, if we consider the
        # possibility that within that time the __out_data's queue could fill up. Any kind of data clogging must not be
        # encouraged.
        while self.__write_loop.get_truth_remain_locked():
            try:
                write_data = self.__out_data.read(block=True, timeout=self.__io_timeout)
                self.__pipe.write(write_data)
                self.__pipe.flush()
            except queue.Empty:
                pass
            except IOError as e:
                if e.errno == errno.EPIPE:
                    # TODO: handle the error. This must be done by logging the error that was raised.
                    # Currently this project does not have a logging mechanism.
                    # This error is raised when the pipe was already closed.
                    self.__write_loop.unlock_after_get_truth()
                    break

            self.__write_loop.unlock_after_get_truth()
            time.sleep(self.__io_time_delay)

        self.__exec_started.set_false()
        # self.__exec_started = False

        self.__exec_stopped.set_true()
        # print("stdin exited")


class ParallelReadPipe(ReaderBase):

    def __assert_pip_blocking(self):
        if not os.get_blocking(self.__pipe.fileno()):
            raise RuntimeError("Only blocking processes are handled by the \"ParallelReadPipe\" class")

    @staticmethod
    def __assert_in_data(in_data):
        if not isinstance(in_data, WriteIOChannel):
            raise RuntimeError("Expected an instance of " + str(type(WriteIOChannel)) + " but " + str(type(in_data)) +
                               " was given")

    def __init__(self, in_data: WriteIOChannel, pipe=None, read_size=1):
        ReaderBase.__init__(self)

        self.__pipe = pipe
        ParallelReadPipe.__assert_in_data(in_data)
        self.__in_data = in_data
        self.__read_size = read_size
        if pipe is not None:
            self.__assert_pip_blocking()
        # self.__exec_started = False
        self.__exec_started = AtomicBool(value=False)
        self.__exec_stopped = AtomicBool(value=False)
        self.__call_lock = threading.Lock()

    def set_pipe(self, pipe):
        if self.__exec_started.get_truth_unsafe():
            raise RuntimeError("Attempt to modify the pipe in a running execution is forbidden")

        self.__pipe = pipe
        self.__assert_pip_blocking()

    def is_running(self):
        return self.__exec_started.get_truth_unsafe()

    def is_stopped(self):
        return self.__exec_stopped.get_truth_unsafe()

    def start_running(self):
        self.__call_lock.release()

    def __call__(self):

        self.__call_lock.acquire(blocking=True)
        self.__call_lock.acquire(blocking=True)

        # self.__exec_started = True
        self.__exec_started.set_true()

        if self.__pipe is None:
            raise TypeError("Expected a valid pipe, None given")
        read_data = self.__pipe.read(self.__read_size)
        while len(read_data) > 0:
            # len(read_data) == 0 implies EOF. This is because self.__pipe.read(...) is a blocking system call (for
            # pipes)
            self.__in_data.write(read_data)
            read_data = self.__pipe.read(self.__read_size)

        # self.__exec_started = False
        self.__exec_started.set_false()

        self.__exec_stopped.set_true()
        # print("stdout or stderr exited")


class ParallelReadLinePipe(ReaderBase):

    def __assert_pip_blocking(self):
        if not os.get_blocking(self.__pipe.fileno()):
            raise RuntimeError("Only blocking processes are handled by the \"ParallelReadLinePipe\" class")

    @staticmethod
    def __assert_in_data(in_data):
        if not isinstance(in_data, WriteIOChannel):
            raise RuntimeError("Expected an instance of " + str(type(WriteIOChannel)) + " but " + str(type(in_data)) +
                               " was given")

    def __init__(self, in_data: WriteIOChannel, pipe=None, read_size=-1):
        ReaderBase.__init__(self)

        self.__pipe = pipe

        ParallelReadLinePipe.__assert_in_data(in_data)
        self.__in_data = in_data
        self.__read_size = read_size

        if pipe is not None:
            self.__assert_pip_blocking()

        # self.__exec_started = False
        self.__exec_started = AtomicBool(value=False)

        self.__exec_stopped = AtomicBool(value=False)
        self.__call_lock = threading.Lock()

    def set_pipe(self, pipe):
        if self.__exec_started.get_truth_unsafe():
            raise RuntimeError("Attempt to modify the pipe in a running execution is forbidden")

        self.__pipe = pipe
        self.__assert_pip_blocking()

    def is_running(self):
        return self.__exec_started.get_truth_unsafe()

    def is_stopped(self):
        return self.__exec_stopped.get_truth_unsafe()

    def start_running(self):
        self.__call_lock.release()

    def __call__(self):
        self.__call_lock.acquire(blocking=True)
        self.__call_lock.acquire(blocking=True)

        # self.__exec_started = True
        self.__exec_started.set_true()

        if self.__pipe is None:
            raise TypeError("Expected a valid pipe, None given")
        read_data = self.__pipe.readline(self.__read_size)
        while len(read_data) > 0:
            self.__in_data.write(read_data)
            read_data = self.__pipe.readline(self.__read_size)
        # self.__exec_started = False
        self.__exec_started.set_false()
        self.__exec_stopped.set_true()
