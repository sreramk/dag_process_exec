import subprocess
import threading

from process_exec.parallel_pipe_io import ParallelWritePipe, ParallelReadPipe
from process_exec.queued_io_channel import ReadIOChannel, WriteIOChannel


# TODO: write a mechanism to get the exit code

class ExecuteCommand:
    def __init__(self, command, stdout_writer_handle: WriteIOChannel, stderr_writer_handle: WriteIOChannel,
                 stdin_reader_handle: ReadIOChannel, _io_timeout=0.01, _io_time_delay=0.001):
        self.__command = command

        self.__stdout_writer_handle = stdout_writer_handle
        self.__stderr_writer_handle = stderr_writer_handle
        self.__stdin_reader_handle = stdin_reader_handle

        self.__io_timeout = _io_timeout
        self.__io_time_delay = _io_time_delay

        self.__stdout_reader_thread = None
        self.__stderr_reader_thread = None
        self.__stdin_writer_thread = None

        self.__stdout_reader = None
        self.__stderr_reader = None
        self.__stdin_writer = None

        self.__proc = None

        self.__called_once = False

    def get_stdout_reader_thread(self):
        return self.__stdout_reader_thread

    def get_stderr_reader_thread(self):
        return self.__stderr_reader_thread

    def get_stdin_writer_thread(self):
        return self.__stdin_writer_thread

    def is_running(self):
        return self.__stdout_reader.is_running()

    def is_stopped(self):
        # print (self.__stdout_reader.is_stopped())
        return self.__stdout_reader.is_stopped()

    def __execute_popen(self, command, stdout_writer_handle: WriteIOChannel, stderr_writer_handle: WriteIOChannel,
                        stdin_reader_handle: ReadIOChannel):
        if self.__called_once:
            raise RuntimeError(" And instance of ExecuteCommand can only be called once ")

        self.__called_once = True

        self.__stdout_reader = ParallelReadPipe(stdout_writer_handle)
        self.__stdout_reader_thread = threading.Thread(target=self.__stdout_reader, daemon=True)

        self.__stderr_reader = ParallelReadPipe(stderr_writer_handle)
        self.__stderr_reader_thread = threading.Thread(target=self.__stderr_reader, daemon=True)

        self.__stdin_writer = ParallelWritePipe(stdin_reader_handle, _io_timeout=self.__io_timeout,
                                                _io_time_delay=self.__io_time_delay)
        self.__stdin_writer_thread = threading.Thread(target=self.__stdin_writer, daemon=True)

        self.__stdout_reader_thread.start()
        self.__stderr_reader_thread.start()
        self.__stdin_writer_thread.start()

        self.__proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)

        self.__stdout_reader.set_pipe(self.__proc.stdout)
        self.__stdout_reader.start_running()

        self.__stderr_reader.set_pipe(self.__proc.stderr)
        self.__stderr_reader.start_running()

        self.__stdin_writer.set_pipe(self.__proc.stdin)
        self.__stdin_writer.start_running()

    def __call__(self):
        self.__execute_popen(self.__command, self.__stdout_writer_handle, self.__stderr_writer_handle,
                             self.__stdin_reader_handle)

    def get_stdin_writer(self):
        return self.__stdin_writer

    def end_stdin_writer(self):
        return self.__stdin_writer.parallel_write_end_loop()

    def get_process_id(self):
        return self.__proc.pid

    def get_proc(self):
        return self.__proc

    def join_all(self, timeout=None):
        self.__stdout_reader_thread.join(timeout)
        self.__stderr_reader_thread.join(timeout)
        self.__stdin_writer_thread.join(timeout)

    def wait(self, timeout=None):
        return self.__proc.wait(timeout)
