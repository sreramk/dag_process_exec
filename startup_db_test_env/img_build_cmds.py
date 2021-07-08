from process_exec.command_generator import CommandGenerator


class DockerInspectImgToCheckItExistsCmdFactory(CommandGenerator):
    """
        This command is used for checking if the image exists locally
    """

    def __init__(self, image_name, is_sudo=True):
        self.__image_name = image_name
        self.__is_sudo = is_sudo

    def is_sudo(self) -> bool:
        return self.__is_sudo

    def generate_exec_command(self) -> list:
        command = ["docker", "inspect", "--type", "image", self.__image_name]
        if self.__is_sudo:
            command.insert(0, 'sudo')
        return command


class DockerBuildCmdFactory(CommandGenerator):
    def __init__(self, path, tag, is_sudo=True):
        self.__path = path
        self.__tag = tag
        self.__is_sudo = is_sudo

    def is_sudo(self) -> bool:
        return self.__is_sudo

    def generate_exec_command(self) -> list:
        command = ["docker", "build",  self.__path, "--tag", self.__tag]
        if self.__is_sudo:
            command.insert(0, 'sudo')

        return command
