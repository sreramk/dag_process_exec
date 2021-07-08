import subprocess
import sys
import threading
import time

from process_exec.exec_cmd_managed import ExecCmdManaged
from startup_db_test_env.db_service_cmds import CreateDBContainerCmdFactory, ContainerNameFactory, CreateDBCmdFactory, \
    CreateUserCmdFactory, RemoveDBContainerCmdFactory


# TODO: write code to subscribe to a bunch of io_channels simultaneously

class ReplicatedPartitionedDBContainerNameBuilder:
    def __init__(self, partition_name, total_num_of_partitions, replication_name, total_num_of_replications):
        """

        :param partition_name:
        :param total_num_of_partitions:
        :param replication_name:
        :param total_num_of_replications:
        """
        self.__partition_name = partition_name
        self.__replication_name = replication_name
        self.__total_num_of_partitions = total_num_of_partitions
        self.__total_num_of_replications = total_num_of_replications

    def build_db_container_name_list(self):
        partition_name = self.__partition_name
        replication_name = self.__replication_name

        container_name_list = []

        for partition_id in range(self.__total_num_of_partitions):
            for replication_id in range(self.__total_num_of_replications):
                container_name = ContainerNameFactory(partition_name, partition_id, replication_name,
                                                      replication_id).generate_container_name()
                container_name_list.append(container_name)

        return container_name_list


class UserDBConfig:
    def __init__(self, user_name, password, database_name):
        """

        :param user_name:
        :param password:
        :param database_name:
        """
        self.__user_name = user_name
        self.__password = password
        self.__database_name = database_name

    def get_user_name(self):
        return self.__user_name

    def get_password(self):
        return self.__password

    def get_db_name(self):
        return self.__database_name


class DockerCmdBaseConfig:
    def __init__(self, image_name, external_port_num_begin, internal_port_num=5432, docker_file_path="."):
        """
        This builds the configuration needed to
        :param image_name:
        :param external_port_num_begin:
        :param internal_port_num:
        """
        self.__image_name = image_name
        self.__external_port_num_begin = external_port_num_begin
        self.__internal_port_num = internal_port_num
        self.__docker_file_path = docker_file_path

    def get_image_name(self):
        return self.__image_name

    def get_external_port_num_begin(self):
        return self.__external_port_num_begin

    def get_internal_port_num(self):
        return self.__internal_port_num


class ExecutionController:
    def __init__(self, num_of_attempts, per_attempt_wait_time=0, timeout=None):
        self.__num_of_attempts = num_of_attempts
        self.__per_attempt_wait_time = per_attempt_wait_time
        self.__timeout = timeout

    def get_num_of_attempts(self):
        return self.__num_of_attempts

    def get_per_attempt_wait_time(self):
        return self.__per_attempt_wait_time

    def get_timeout(self):
        return self.__timeout


class StartupDBDevEnv:

    @staticmethod
    def __default_logger_stdout(data):
        print(data, file=sys.stdout, end='')
        sys.stdout.flush()

    @staticmethod
    def __default_logger_stderr(data):
        print(data, file=sys.stderr, end='')
        sys.stderr.flush()
    """
        Sets the same user name, password and DB name for all storage instances.
    """

    def __init__(self, replication_partition_config: ReplicatedPartitionedDBContainerNameBuilder,
                 user_db_config: UserDBConfig,
                 docker_run_cmd_base_config: DockerCmdBaseConfig,
                 is_sudo=True,
                 logger_stdout=None,
                 logger_stderr=None):
        """

        :param replication_partition_config:
        :param user_db_config:
        :param docker_run_cmd_base_config:
        :param is_sudo: This value applies to everything except the DockerBuildConfig
        """
        self.__replication_partition_args = replication_partition_config
        self.__container_name_list = self.__replication_partition_args.build_db_container_name_list()
        self.__user_db_config = user_db_config
        self.__docker_run_cmd_base_config = docker_run_cmd_base_config
        self.__is_sudo = is_sudo
        self.__kill_process_threads = {}

        if logger_stdout is None:
            self.__logger_stdout = StartupDBDevEnv.__default_logger_stdout

        if logger_stderr is None:
            self.__logger_stderr = StartupDBDevEnv.__default_logger_stderr

    # TODO: the methods __kill_process nnd __kill_process_parallel don't belong here:
    # These methods likely belong in exec_cmd_managed. We can argue that these do not belong to execute_command as
    # execute_command must be viewed as a more lower level operation.

    # TODO: __kill_process is not needed for the current startup script. Even so, forced killing is not implemented.
    # The current kill command `` sudo kill <pid> " sends a signal to the process, which the process can ignore.
    @staticmethod
    def __kill_process(process_id, wait_time, is_sudo, status_writer, check_if_running):
        def kill_process_after_duration():
            time.sleep(wait_time)
            sys.stdout.flush()
            if check_if_running():
                status_writer(("killing pid", process_id))
                if is_sudo:
                    # print("killing pid: ", process_id)
                    subprocess.check_call(["sudo", "kill", "-9", str(process_id)])
                else:
                    subprocess.check_call(["kill", str(process_id)])

        return kill_process_after_duration

    def __kill_process_parallel(self, process_id, wait_time, check_if_running, is_sudo=True):
        """

        :param process_id:
        :param wait_time:
        :param check_if_running: Ensures that the process is running. This timeout method must not try to kill the
                                 process after it had exited. Process IDs that are not in use could be used by the
                                 operating system in allocating them to a different process.
        :param is_sudo:
        :return:
        """

        kill_process_thread = threading.Thread(target=StartupDBDevEnv.__kill_process(process_id, wait_time, is_sudo,
                                                                                     self.__logger_stdout,
                                                                                     check_if_running), daemon=True)

        if process_id in self.__kill_process_threads:
            raise RuntimeError(" A thread is already actively trying to kill process: " + str(process_id))
        self.__kill_process_threads[process_id] = kill_process_thread

    def __start_killing_processes(self):
        for killer_thread_id in self.__kill_process_threads:
            # print ("kill: ", killer_thread_id)
            if not self.__kill_process_threads[killer_thread_id].is_alive():
                self.__kill_process_threads[killer_thread_id].start()

    # TODO (low priority): __process_output, must accept two other arguments for stdout and stderr triggers.
    # These triggers must be invoked as callbacks in association with specific patterns in the received text.
    # Implementing this mechanism will complete what this method stands for.
    def __process_output(self, attempt_count, stderr_subscriptions, stdout_subscriptions, container_name_list):
        """

        :param attempt_count:
        :param stderr_subscriptions:
        :param stdout_subscriptions:
        :param container_name_list:
        :return: The list of container names; of containers from which at least one error message was received.
                 The commands executed in the context of these containers are considered to have failed if they had
                 sent at least one stderr message.
        """
        exec_failed_containers = []  # execution failed containers

        for container_name in container_name_list:
            err_string = stderr_subscriptions[container_name].read_string()
            out_string = stdout_subscriptions[container_name].read_string()
            if len(err_string) > 2:
                # assumes all error messages to be a failed attempt
                exec_failed_containers.append(container_name)
            # TODO: change this to pass on structured information rather than serialized display information.
            # this must be done to pass on the responsibility for handling the data and eventually displaying it when
            # required to the registered handling function.
            if len(out_string) > 2:
                self.__logger_stdout(
                    " attempt count: {}, container name: {}, stdout: {}".format(attempt_count, container_name,
                                                                                out_string)
                )

            if len(err_string) > 2:
                self.__logger_stderr(
                    " attempt count: {}, container name: {}, stderr: {}".format(attempt_count, container_name,
                                                                                err_string)
                )

        return exec_failed_containers

    def __execute_cmd(self, controller: ExecutionController, cmd_factory, exec_no_wait=False):

        external_port_start = self.__docker_run_cmd_base_config.get_external_port_num_begin()

        per_attempt_wait_time = controller.get_per_attempt_wait_time()
        timeout = controller.get_timeout()
        num_of_attempts = controller.get_num_of_attempts()

        exec_list = []

        stderr_subscriptions = {}
        stdout_subscriptions = {}

        container_name_list = self.__container_name_list

        for attempt_count in range(num_of_attempts):
            current_port = external_port_start
            for db_container_name in container_name_list:
                exec_cmd = ExecCmdManaged(cmd_factory(db_container_name, current_port).generate_exec_command())
                exec_cmd()

                stderr_subscriptions[db_container_name] = exec_cmd.create_stderr_subscription()
                stdout_subscriptions[db_container_name] = exec_cmd.create_stdout_subscription()

                if timeout is not None:
                    pid = exec_cmd.get_process_id()

                    def check_if_running():
                        return exec_cmd.is_running()

                    self.__kill_process_parallel(pid, timeout, check_if_running, self.__is_sudo)

                exec_list.append(exec_cmd)
                current_port += 1

            if timeout is not None:
                self.__start_killing_processes()

            if not exec_no_wait:
                for exec_cmd in exec_list:
                    exec_cmd.wait()

            container_name_list = self.__process_output(attempt_count, stderr_subscriptions, stdout_subscriptions,
                                                        container_name_list)

            if len(container_name_list) == 0:
                break

            time.sleep(per_attempt_wait_time)

    def __create_db_container(self, controller: ExecutionController):

        # external_port_start = self.__docker_run_cmd_base_config.get_external_port_num_begin()
        internal_port = self.__docker_run_cmd_base_config.get_internal_port_num()
        image_name = self.__docker_run_cmd_base_config.get_image_name()

        def cmd_factory(container_name, port_number):
            return CreateDBContainerCmdFactory(container_name, external_port_num=port_number,
                                               internal_port_num=internal_port, image_name=image_name,
                                               is_sudo=self.__is_sudo)

        self.__execute_cmd(controller, cmd_factory, exec_no_wait=False)

    def __create_db(self, controller: ExecutionController):

        database_name = self.__user_db_config.get_db_name()

        def cmd_factory(container_name, port_number):
            return CreateDBCmdFactory(container_name, database_name=database_name, is_sudo=self.__is_sudo)

        self.__execute_cmd(controller, cmd_factory)

    def __create_user(self, controller: ExecutionController):

        user_name = self.__user_db_config.get_user_name()
        password = self.__user_db_config.get_password()

        def cmd_factory(container_name, port_number):
            return CreateUserCmdFactory(container_name, user=user_name, password=password, is_sudo=self.__is_sudo)

        self.__execute_cmd(controller, cmd_factory)

    def start_db_environment(self, controller_create_db_container: ExecutionController = None,
                             controller_create_db: ExecutionController = None,
                             controller_create_user: ExecutionController = None):

        if controller_create_db_container is None:
            controller_create_db_container = ExecutionController(num_of_attempts=2)

        if controller_create_db is None:
            controller_create_db = ExecutionController(per_attempt_wait_time=30, num_of_attempts=5)

        if controller_create_user is None:
            controller_create_user = ExecutionController(per_attempt_wait_time=30, num_of_attempts=5)

        self.__create_db_container(controller_create_db_container)
        self.__create_db(controller_create_db)
        self.__create_user(controller_create_user)

    def stop_and_remove_db_instances(self):

        def cmd_factory(container_name, port_number):
            return RemoveDBContainerCmdFactory(container_name, is_sudo=self.__is_sudo)

        self.__execute_cmd(ExecutionController(num_of_attempts=1, per_attempt_wait_time=0), cmd_factory)
