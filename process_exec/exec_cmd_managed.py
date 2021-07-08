import multiprocessing
import queue

from process_exec.execute_command import ExecuteCommand
from process_exec.queued_io_channel import IOChannelPublication


def create_queue_thread_safe():
    return queue.Queue()


def create_queue_multiproc():
    return multiprocessing.Queue()


class ExecCmdManaged:
    def __init__(self, command, _io_timeout=0.01, _io_time_delay=0.001, _create_queue=create_queue_thread_safe):
        self.__stdout_publication = IOChannelPublication(_create_queue)
        self.__stderr_publication = IOChannelPublication(_create_queue)
        self.__stdin_publication = IOChannelPublication(_create_queue)

        stdout_writer_handle = self.__stdout_publication.create_new_write_instance()
        stderr_writer_handle = self.__stderr_publication.create_new_write_instance()
        stdin_reader_handle = self.__stdin_publication.create_subscription()

        self.__execute_command = ExecuteCommand(command, stdout_writer_handle, stderr_writer_handle,
                                                stdin_reader_handle, _io_timeout=_io_timeout,
                                                _io_time_delay=_io_time_delay)

    def __call__(self):
        self.__execute_command()

    def create_stdout_subscription(self):
        return self.__stdout_publication.create_subscription()

    def create_stderr_subscription(self):
        return self.__stderr_publication.create_subscription()

    def get_stdin_writer(self):
        return self.__stdin_publication.create_new_write_instance()

    def is_running(self):
        return self.__execute_command.is_running()

    def is_stopped(self):
        return self.__execute_command.is_stopped()

    def join_all(self, timeout=None):
        """
        Warning: this method should not be called before calling end_stdin_writer
        :param timeout:
        :return:
        """
        self.__execute_command.join_all(timeout)

    def wait(self, timeout=None):
        return self.__execute_command.wait(timeout)

    def get_process_id(self):
        return self.__execute_command.get_process_id()

    def end_stdin_writer(self):
        self.__execute_command.end_stdin_writer()


