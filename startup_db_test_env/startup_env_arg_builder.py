from startup_db_test_env.startup_env import ReplicatedPartitionedDBContainerNameBuilder, UserDBConfig, \
    DockerCmdBaseConfig, ExecutionController


class StartupDBDevEnvConfigArgBuilder:
    __FNC_START_ENV = "startenv"
    __FNC_STOP_ENV = "stopenv"

    def __initialize_configuration(self, config_data):
        self.__replication_partition_config = ReplicatedPartitionedDBContainerNameBuilder(
            partition_name=config_data["partition_name"],
            total_num_of_partitions=config_data["total_num_of_partitions"],
            replication_name=config_data["replication_name"],
            total_num_of_replications=config_data["total_num_of_replications"],
        )

        self.__user_db_config = UserDBConfig(
            user_name=config_data["user_name"],
            password=config_data["password"],
            database_name=config_data["database_name"]
        )

        self.__docker_cmd_base_config = DockerCmdBaseConfig(
            image_name=config_data["image_name"],
            external_port_num_begin=config_data["external_port_num_begin"],
            internal_port_num=config_data["internal_port_num"],
            docker_file_path=config_data["docker_file_path"]
        )

    def __initialize_controller(self, config_data):
        # print(config_data)
        create_db_container_args = config_data["ExecutionController"]["create_db_container"]
        self.__controller_create_db_container = ExecutionController(
            num_of_attempts=create_db_container_args["num_of_attempts"],
            timeout=create_db_container_args["timeout"]
        )

        create_db_args = config_data["ExecutionController"]["create_db"]
        self.__controller_create_db = ExecutionController(
            per_attempt_wait_time=create_db_args["per_attempt_wait_time"],
            num_of_attempts=create_db_args["num_of_attempts"]
        )

        create_user_args = config_data["ExecutionController"]["create_user"]
        self.__controller_create_user = ExecutionController(
            per_attempt_wait_time=create_user_args["per_attempt_wait_time"],
            num_of_attempts=create_user_args["num_of_attempts"]
        )

    def __init__(self, config_data, root_command):
        self.__initialize_configuration(config_data)
        self.__initialize_controller(config_data)
        self.__root_command = root_command
        self.__is_sudo = config_data["is_sudo"]

    @staticmethod
    def get_func_start_env():
        return StartupDBDevEnvConfigArgBuilder.__FNC_START_ENV

    @staticmethod
    def get_func_stop_env():
        return StartupDBDevEnvConfigArgBuilder.__FNC_STOP_ENV

    def get_replication_partition_config(self):
        return self.__replication_partition_config

    def get_user_db_config(self):
        return self.__user_db_config

    def get_docker_cmd_base_config(self):
        return self.__docker_cmd_base_config

    def get_controller_create_db_container(self):
        """
        Controller for creating the DB container.
        :return:
        """
        return self.__controller_create_db_container

    def get_controller_create_db(self):
        """
        Controller for creating a DB within a DB container
        :return:
        """
        return self.__controller_create_db

    def get_controller_create_user(self):
        """
        Controller for creating a user within a DB
        :return:
        """
        return self.__controller_create_user

    def is_sudo(self):
        return self.__is_sudo

    def get_root_command(self):
        return self.__root_command
