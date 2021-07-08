import queue
import threading

from process_exec.queued_io_channel import ReadIOChannel, IOChannelPublication, WriteIOChannel
from process_exec.util.atomic_bool import AtomicBool


def new_thread_safe_queue():
    return queue.Queue()


class ExecuteParallelRead:

    @staticmethod
    def __none_process(read_data):
        return read_data

    def __init__(self, read_data_from_source: ReadIOChannel, write_data_to_destination: WriteIOChannel,
                 preprocess_before_write_fnc=None, _io_break_time=0.001):
        self.__exec_stopped = AtomicBool(value=False)
        self.__exec_started = AtomicBool(value=False)
        self.__call_lock = threading.Lock()

        self.__read_data_from_source = read_data_from_source
        self.__write_data_to_destination = write_data_to_destination

        if preprocess_before_write_fnc is None:
            self.__preprocess_before_write_fnc = ExecuteParallelRead.__none_process
        else:
            self.__preprocess_before_write_fnc = preprocess_before_write_fnc

        self.__io_break_time = _io_break_time

    def is_stopped(self):
        return self.__exec_stopped.get_truth_unsafe()

    def is_started(self):
        return self.__exec_started.get_truth_unsafe()

    def start_running(self):
        self.__call_lock.release()

    def stop_execution(self):
        self.__exec_stopped.set_true()

    def __call__(self):
        self.__call_lock.acquire(blocking=True)
        self.__call_lock.acquire(blocking=True)

        self.__exec_started.set_true()

        read_data = None
        while not self.__exec_stopped.get_truth_unsafe():
            try:
                if read_data is None:
                    read_data = self.__read_data_from_source.read(block=True, timeout=self.__io_break_time)
                    read_data = self.__preprocess_before_write_fnc(read_data)

                self.__write_data_to_destination.write(read_data, block=True, timeout=self.__io_break_time)
            except queue.Empty:
                pass
            except queue.Full:
                continue

            read_data = None

        self.__exec_started.set_false()

        self.__exec_stopped.set_true()


class MergeIOSubscribe:
    def __init__(self, _io_break_time=0.001):
        self.__read_io_channel_list = []
        self.__merged_publication = IOChannelPublication(new_thread_safe_queue)

    @staticmethod
    def __execute_parallel_read_func_generator(read_io_channel: ReadIOChannel):
        def execute_parallel_read():
            AtomicBool
            pass

        return execute_parallel_read

    def add_read_io_channel_to_group(self, read_io_channel: ReadIOChannel):
        self.__read_io_channel_list.append(read_io_channel)
