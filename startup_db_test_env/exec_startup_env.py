from startup_db_test_env.startup_env_arg_builder import StartupDBDevEnvConfigArgBuilder
from startup_db_test_env.startup_env import StartupDBDevEnv


class ExecStartupEnv:

    def __init__(self, config_arg_builder: StartupDBDevEnvConfigArgBuilder, logger_stdout=None, logger_stderr=None):
        self.__config_arg_builder = config_arg_builder
        self.__startup_db_dev_env = StartupDBDevEnv(
            replication_partition_config=config_arg_builder.get_replication_partition_config(),
            user_db_config=config_arg_builder.get_user_db_config(),
            docker_run_cmd_base_config=config_arg_builder.get_docker_cmd_base_config(),
            is_sudo=config_arg_builder.is_sudo(),
            logger_stdout=logger_stdout,
            logger_stderr=logger_stderr)

    def __startup_db_dev_env_call(self):
        self.__startup_db_dev_env.start_db_environment(self.__config_arg_builder.get_controller_create_db_container(),
                                                       self.__config_arg_builder.get_controller_create_db(),
                                                       self.__config_arg_builder.get_controller_create_user())

    def __stop_and_remove_db_instances(self):
        self.__startup_db_dev_env.stop_and_remove_db_instances()

    def execute_command_fnc(self):
        pos_arg = self.__config_arg_builder.get_root_command()
        if pos_arg == self.__config_arg_builder.get_func_start_env():
            self.__startup_db_dev_env_call()
        elif pos_arg == self.__config_arg_builder.get_func_stop_env():
            self.__stop_and_remove_db_instances()


# class ExecStartupEnv:
#     __FNC_START_ENV = "startenv"
#     __FNC_STOP_ENV = "stopenv"
#
#     def __initialize_configuration(self):
#         config_data = self.__config_data
#
#         self.__replication_partition_config = ReplicatedPartitionedDBContainerNameBuilder(
#             partition_name=config_data["partition_name"],
#             total_num_of_partitions=config_data["total_num_of_partitions"],
#             replication_name=config_data["replication_name"],
#             total_num_of_replications=config_data["total_num_of_replications"],
#         )
#
#         self.__user_db_config = UserDBConfig(
#             user_name=config_data["user_name"],
#             password=config_data["password"],
#             database_name=config_data["database_name"]
#         )
#
#         self.__docker_cmd_base_config = DockerCmdBaseConfig(
#             image_name=config_data["image_name"],
#             external_port_num_begin=config_data["external_port_num_begin"],
#             internal_port_num=config_data["internal_port_num"],
#             docker_file_path=config_data["docker_file_path"]
#         )
#
#     def __initialize_controller(self):
#         config_data = self.__config_data
#         # print(config_data)
#         create_db_container_args = config_data["ExecutionController"]["create_db_container"]
#         self.__controller_create_db_container = ExecutionController(
#             num_of_attempts=create_db_container_args["num_of_attempts"],
#             timeout=create_db_container_args["timeout"]
#         )
#
#         create_db_args = config_data["ExecutionController"]["create_db"]
#         self.__controller_create_db = ExecutionController(
#             per_attempt_wait_time=create_db_args["per_attempt_wait_time"],
#             num_of_attempts=create_db_args["num_of_attempts"]
#         )
#
#         create_user_args = config_data["ExecutionController"]["create_user"]
#         self.__controller_create_user = ExecutionController(
#             per_attempt_wait_time=create_user_args["per_attempt_wait_time"],
#             num_of_attempts=create_user_args["num_of_attempts"]
#         )
#
#     def __init__(self, logger_stdout=None, logger_stderr=None, _arg_parse_inst=StartupScriptParser):
#         self.__parser_inst = _arg_parse_inst()
#         self.__parser_inst.parse_arguments()
#         config_path = self.__parser_inst.get_config_path()
#
#         with open(config_path) as f:
#             self.__config_data = json.load(f)
#
#         self.__parser_inst.updated_config_with_args(self.__config_data)
#
#         # self.__config_data.update(self.__parser_inst.get_config_data())
#
#         is_sudo = self.__config_data["is_sudo"]
#         self.__initialize_configuration()
#         self.__initialize_controller()
#
#         self.__startup_db_dev_env = StartupDBDevEnv(replication_partition_config=self.__replication_partition_config,
#                                                     user_db_config=self.__user_db_config,
#                                                     docker_run_cmd_base_config=self.__docker_cmd_base_config,
#                                                     is_sudo=is_sudo,
#                                                     logger_stdout=logger_stdout,
#                                                     logger_stderr=logger_stderr)
#
#     def __startup_db_dev_env_call(self):
#         self.__startup_db_dev_env.start_db_environment(self.__controller_create_db_container,
#                                                        self.__controller_create_db, self.__controller_create_user)
#
#     def __stop_and_remove_db_instances(self):
#         self.__startup_db_dev_env.stop_and_remove_db_instances()
#
#     def execute_command_fnc(self):
#         pos_arg = self.__parser_inst.get_root_command()
#         if pos_arg == ExecStartupEnv.__FNC_START_ENV:
#             self.__startup_db_dev_env_call()
#         elif pos_arg == ExecStartupEnv.__FNC_STOP_ENV:
#             self.__stop_and_remove_db_instances()


if __name__ == "__main__":
    exec_startup_env = ExecStartupEnv()
    exec_startup_env.execute_command_fnc()
    # exec_startup_env.startup_db_dev_env()
    # exec_startup_env.stop_and_remove_db_instances()

    # parser = argparse.ArgumentParser()
    # parser.add_argument('--fo-o', '-fbb')
    # parser.add_argument('--bar', '-b')
    # parser.add_argument('--ab.c', '-a', action="extend", nargs="+")
    # parser.add_argument('xyz', action="extend", nargs="+")
    # parser.add_argument('efg', action="extend", nargs="+")
    # parser.add_argument('efg2', action="extend", nargs="+")
    #
    # args = parser.parse_args()
    # print(args)
    # if args.bar is not None:
    #     print(int(args.bar) + 10)
    # print(args)
    # if hasattr(args, 'ab.c'):
    #     print("hit")
    #     print(getattr(args, 'ab.c'))
    # if args.xyz is not None:
    #     print(args.xyz)
    # print(vars(args))
