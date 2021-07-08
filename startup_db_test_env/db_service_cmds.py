from process_exec.command_generator import CommandGenerator

"""
Note: The arguments of some of the following classes use <constant string>.replace( ... ) to inject arguments into 
      strings. These arguments are NOT SAFE, and could be susceptible to injecting arbitrary bash script code. So 
      if this code is used in building a server, text from the end users must not be directly inputted into a command 
      creator factory.
"""


class ContainerNameFactory:
    def __init__(self, partition_name, partition_id, replication_name, replication_id):
        self.__partition_name = partition_name
        self.__partition_id = partition_id
        self.__replication_name = replication_name
        self.__replication_id = replication_id

    def generate_container_name(self):
        return self.__partition_name + str(self.__partition_id) + self.__replication_name + str(
            self.__replication_id)


class CreateDBContainerCmdFactory(CommandGenerator):

    def __init__(self, service_name, external_port_num, internal_port_num=5432,
                 image_name="psql_ubuntu:0.3", is_sudo=True):
        self.__service_name = service_name

        self.__external_port_num = external_port_num
        self.__internal_port_num = internal_port_num
        self.__image_name = image_name
        self.__is_sudo = is_sudo

    def is_sudo(self) -> bool:
        return self.__is_sudo

    def generate_exec_command(self) -> list:
        port_map = str(self.__external_port_num) + ":" + str(self.__internal_port_num)
        command = ['docker', 'run', '--name', self.__service_name, '--rm', '-p', port_map, self.__image_name]

        if self.__is_sudo:
            command.insert(0, "sudo")

        return command


class RemoveDBContainerCmdFactory(CommandGenerator):

    def __init__(self, service_name, is_sudo=True):
        self.__service_name = service_name
        self.__is_sudo = is_sudo

    def generate_exec_command(self) -> list:
        command = ['docker', 'stop', self.__service_name]

        if self.__is_sudo:
            command.insert(0, "sudo")

        return command

    def is_sudo(self) -> bool:
        return self.__is_sudo


class CreateDBCmdFactory(CommandGenerator):
    __CREATE_DATABASE_COMMAND = "su - postgres -c \"psql -c 'CREATE DATABASE <<string_1>>'\""

    def __init__(self, service_name, database_name, is_sudo=True):
        self.__service_name = service_name
        self.__database_name = database_name
        self.__is_sudo = is_sudo

    def generate_exec_command(self) -> list:
        command = ['docker', 'exec', self.__service_name, "/bin/bash", "-c",
                   CreateDBCmdFactory.__CREATE_DATABASE_COMMAND.replace("<<string_1>>", self.__database_name)]
        if self.__is_sudo:
            command.insert(0, 'sudo')

        return command

    def is_sudo(self) -> bool:
        return self.__is_sudo


class CreateUserCmdFactory(CommandGenerator):
    __CREATE_USER_COMMAND = "su - postgres -c \"psql -c " \
                            "\\\"CREATE ROLE <<string_1>> WITH SUPERUSER PASSWORD '<<string_2>>'\\\"\""

    def __init__(self, service_name, user, password, is_sudo=True):
        self.__service_name = service_name
        self.__user = user
        self.__password = password
        self.__is_sudo = is_sudo

    def is_sudo(self) -> bool:
        return self.__is_sudo

    def generate_exec_command(self) -> list:
        command = ['docker', 'exec', self.__service_name, "/bin/bash", "-c",
                   CreateUserCmdFactory.__CREATE_USER_COMMAND.replace("<<string_1>>", self.__user).replace(
                       "<<string_2>>", self.__password)]
        if self.__is_sudo:
            command.insert(0, 'sudo')

        return command



