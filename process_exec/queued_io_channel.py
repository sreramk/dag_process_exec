import queue


class ReadIOChannel:

    def __init__(self, queue_inst):
        """

        :param queue_inst: shared Queue instance mediating the unidirectional communication. If None, defaults to
                           queue.Queue
        """
        self.__queue_inst = queue_inst

    def read(self, block=True, timeout=None):
        return self.__queue_inst.get(block=block, timeout=timeout)

    def read_nowait(self):
        return self.__queue_inst.get_nowait()

    def read_queue_empty(self):
        """
        WARNING: The result provided by this method will be approximate when used in threads. Do not use this method
                 as a terminator while reading the elements from the queue. Instead capture the ``queue.Empty"
                 exception, which will be a better indicator for the presence of elements in the queue.
        :return:
        """
        return self.__queue_inst.qsize() == 0

    def read_string(self):
        """

        :return:
        """
        data = []
        while True:
            try:
                data.append(self.read_nowait().decode("utf-8"))
            except queue.Empty:
                break

        return "".join(data)


class WriteIOChannel:
    def __init__(self, queue_inst_list):
        """

        :param queue_inst_list: shared Queue instance mediating the unidirectional communication. If None, defaults to
                           queue.Queue
        """
        self.__queue_inst_list = queue_inst_list

    def write(self, data, block=True, timeout=None):
        for queue_inst in self.__queue_inst_list:
            queue_inst.put(data, block=block, timeout=timeout)

    def write_nowait(self, data):
        for queue_inst in self.__queue_inst_list:
            queue_inst.put_nowait(data)

    def is_write_queue_full(self):
        """
        NOTE: This method is approximate and will not always report the correct result. Therefore this is not
              thread safe. Try to use exceptions to check if the queue is empty.
        :return:
        """
        return (queue_inst.qsize() == queue_inst.maxsize for queue_inst in self.__queue_inst_list)


# TODO: (BUG) This class's methods must be made thread safe. Using locks is not an option.
# Locks cannot be an option because, in the case of multiprocessing, classes with defined locks cannot be moved between
# processes. Every instance of a QueueCollection may have to interact with each other through messaging implemented
# with a queue appropriate for the particular kind of communication. So, an implementation like this will message the
# other instances of a new queue that may have been created, in response to having them replicating that action.
#
# Currently lists are themselves thread-safe, and this is because of the GIL. So this will not create inconstancy.
class QueueCollection:
    def __init__(self, queue_inst_generator):
        self.__queue_inst_generator = queue_inst_generator
        self.__queue_collection = []

    def add_new_queue(self):
        new_queue = self.__queue_inst_generator()
        self.__queue_collection.append(new_queue)
        return new_queue

    def remove_queue(self, queue_inst):
        self.__queue_collection.remove(queue_inst)

    def __len__(self):
        return len(self.__queue_collection)

    def __iter__(self):
        return iter(self.__queue_collection)

    def __contains__(self, item):
        return item in self.__queue_collection


class IOChannelPublication:
    """
    Note: this class is NOT thread safe. All calls to the methods in this class must be manually serialized. If the
          master-slave pattern is used, this class is usually handled in the master.
    """

    def __init__(self, queue_inst_generator):
        self.__queue_inst_generator = queue_inst_generator
        self.__queue_collection = QueueCollection(self.__queue_inst_generator)

        self.__read_channel_inst_set = set()
        self.__write_inst_set = set()
        self.__subscription_to_queue_map = {}

    def create_subscription(self):
        new_queue_inst = self.__queue_collection.add_new_queue()
        new_subscription_instance = ReadIOChannel(new_queue_inst)

        self.__read_channel_inst_set.add(new_subscription_instance)
        self.__subscription_to_queue_map[new_subscription_instance] = new_queue_inst

        return new_subscription_instance

    # TODO: (BUG) when a WriteIOChannel is created without any subscription, data written to this channel gets lost.
    # A queue is created when a subscription is created. Until there is a subscription, there will not be any queue to
    # write the data to. And a subscription is able to only get the data that it sees after it was create. This must
    # not be the case for the first subscription. Which must also retain the that was received before it was created.
    def create_new_write_instance(self):
        new_write_io_channel = WriteIOChannel(self.__queue_collection)
        self.__write_inst_set.add(new_write_io_channel)
        return new_write_io_channel

    def remove_subscription(self, subscription_instance: ReadIOChannel):
        if subscription_instance in self.__read_channel_inst_set:
            self.__read_channel_inst_set.remove(subscription_instance)
            queue_inst = self.__subscription_to_queue_map[subscription_instance]
            self.__queue_collection.remove_queue(queue_inst)
            del self.__subscription_to_queue_map[subscription_instance]
            return True
        return False
