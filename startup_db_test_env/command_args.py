import argparse
import copy


class StartupScriptParser:
    __ROOT_COMMAND = "positional"
    __CONFIGURATION_PATH = ("--config-path", "-cfp")
    __DEFAULT_CONFIG_PATH = "./default_config.json"

    def __add_flag(self, long, short, object_access_path: list, argtype):
        attribute = StartupScriptParser.__flag_to_attribute(long)
        self.__flags[attribute] = [long, short, object_access_path]
        self.__flags_storage_type[attribute] = argtype

    def __initialize_cmd_flags(self):
        self.__add_flag("--partition-name", "-pn", ["partition_name"], str)
        self.__add_flag("--num-of-partitions", "-np", ["total_num_of_partitions"], int)
        self.__add_flag("--replication-name", "-rn", ["replication_name"], str)
        self.__add_flag("--num-of-replications", "-nr", ["total_num_of_replications"], int)
        self.__add_flag("--user-name", "-un", ["user_name"], str)
        self.__add_flag("--password", "-pwd", ["password"], str)
        self.__add_flag("--database-name", "-dbn", ["database_name"], str)
        self.__add_flag("--image-name", "-img", ["image_name"], str)
        self.__add_flag("--external-port-begin", "-pb", ["external_port_num_begin"], int)
        self.__add_flag("--internal-port-num", "-pi", ["internal_port_num"], int)
        # TODO: the below flag --dockerfile-path was never in use and must be removed
        self.__add_flag("--dockerfile-path", "-dp", ["internal_port_num"], str)

        self.__add_flag("--create-db-container--num-of-attempts", "-cdca",
                        ["ExecutionController", "create_db_container", "num_of_attempts"], int)
        self.__add_flag("--create-db-container--timeout", "-cdct",
                        ["ExecutionController", "create_db_container", "timeout"], float)
        self.__add_flag("--create-db--per-attempt-wait-time", "-cdwt",
                        ["ExecutionController", "create_db", "per_attempt_wait_time"], float)
        self.__add_flag("--create-db--num-of-attempts", "-cdat",
                        ["ExecutionController", "create_db", "num_of_attempts"], int)
        self.__add_flag("--create-user--per-attempt-wait-time", "--cuwt",
                        ["ExecutionController", "create_user", "per_attempt_wait_time"], float)
        self.__add_flag("--create-user--num-of-attempts", "-cuat",
                        ["ExecutionController", "create_user", "num_of_attempts"], int)

        self.__add_flag("--image-constructor--docker-file", "-icdf", ["ImageConstructor", "docker_file_path"], str)
        self.__add_flag("--image-constructor--force-build-image", "-icfi",
                        ["ImageConstructor", "force_build_image"], bool)
        self.__add_flag("--image-constructor--rebuild-image", "-icri", ["ImageConstructor", "rebuild_image"], bool)

        self.__add_flag("--set-sudo", "-su", ["is_sudo"], bool)

    def __initialize_arguments(self):
        self.__parser = argparse.ArgumentParser()
        self.__parser.add_argument(self.__ROOT_COMMAND)
        self.__parser.add_argument(self.__CONFIGURATION_PATH[0], self.__CONFIGURATION_PATH[1])
        for value in self.__flags.values():
            # TODO: add mechanism for adding help string.
            self.__parser.add_argument(value[0], value[1])

    def __init__(self):
        self.__config_data = {}
        self.__flags = {}
        self.__flags_storage_type = {}
        self.__parser = None
        self.__positional_arg = None
        self.__parsed_namespace = None

        self.__initialize_cmd_flags()
        self.__initialize_arguments()

    def __get_commands(self):
        return self.__flags

    @staticmethod
    def __flag_to_attribute(cmd_flag):
        cmd_flag_list = list(cmd_flag)
        if cmd_flag.find("--") == 0:
            cmd_flag_list = cmd_flag_list[2:]  # eliminate the ``--" from the command
        for i in range(len(cmd_flag_list)):
            if cmd_flag_list[i] == '-':
                cmd_flag_list[i] = '_'
        return ''.join(cmd_flag_list)

    def __get_flag(self, arg_flag):
        return self.__flags[arg_flag]

    def __get_flag_storage_type(self, arg_flag):
        return self.__flags_storage_type[arg_flag]

    @staticmethod
    def __type_ensure(value, argtype):
        if argtype is not bool:
            return argtype(value)
        else:
            if value == "t" or value == "T" or value == "True" or value == "true":
                return True
            elif value == "f" or value == "F" or value == "False" or value == "false":
                return False
            else:
                raise RuntimeError("Invalid argument :\"" + str(value) + "\". Must be one of the following : "
                                                                         "\"t\", \"T\", \"true\", \"True\", "
                                                                         "\"f\", \"F\", \"false\", \"False\"")

    def parse_arguments(self, args=None):
        if self.__parsed_namespace is not None:
            # TODO: maybe it is not really an issue to call this method multiple times
            raise RuntimeError(" The parse_arguments cannot be called more than once from the same instance ")
        # if self.__parser is None:
        #     raise RuntimeError("Arguments not initialized. Try calling ``initialize_arguments\" method first")
        self.__parsed_namespace = self.__parser.parse_args(args)
        self.__apply_parsed_arguments(self.__parsed_namespace)

    def __apply_parsed_arguments(self, args: argparse.Namespace):
        for flag in vars(args):
            if flag == StartupScriptParser.__ROOT_COMMAND:
                # the positional argument is ignored because, it won't be needed in determining which flags must be
                # set and which shouldn't be set.
                self.__positional_arg = getattr(args, flag)
                continue
            if flag == StartupScriptParser.__CONFIGURATION_PATH[0]:
                continue
            new_value = getattr(args, flag)
            if new_value is not None:
                object_access_path = self.__get_flag(flag)[2]
                argtype = self.__get_flag_storage_type(flag)
                new_value = StartupScriptParser.__type_ensure(new_value, argtype)
                self.__update_config_data(object_access_path, new_value)

    def __update_config_data(self, object_access_path, new_value):
        config_data = self.__config_data
        object_access_path_size = len(object_access_path)
        for i in range(object_access_path_size):
            part = object_access_path[i]
            if i < (object_access_path_size - 1):
                if isinstance(config_data, dict) and part in config_data:
                    config_data = config_data[part]
                else:
                    config_data[part] = {}
                    config_data = config_data[part]
            else:
                config_data[part] = new_value

    def get_root_command(self):
        """
        Used in determining the operation that must be performed. This must be called after parse_arguments is called
        :return:
        """
        return self.__positional_arg

    def get_config_path(self):
        if self.__parsed_namespace is None:
            raise RuntimeError(" the method parse_arguments must be called before the config path can be retrieved")
        result = getattr(self.__parsed_namespace,
                         StartupScriptParser.__flag_to_attribute(StartupScriptParser.__CONFIGURATION_PATH[0]))
        if result is None:
            result = StartupScriptParser.__DEFAULT_CONFIG_PATH

        return result

    def get_config_data(self):
        return self.__config_data

    @staticmethod
    def __update_config_form_update_inst(data: dict, update_inst: dict):
        for key, value in update_inst.items():
            if key in data:
                data_key = data[key]
                if isinstance(data_key, dict) and isinstance(value, dict):
                    StartupScriptParser.__update_config_form_update_inst(data_key, value)
                    continue
            data[key] = copy.deepcopy(value)

    def updated_config_with_args(self, old_config):
        StartupScriptParser.__update_config_form_update_inst(old_config, self.get_config_data())
