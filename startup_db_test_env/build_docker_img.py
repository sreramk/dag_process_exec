import subprocess

from process_exec.exec_cmd_managed import ExecCmdManaged
from startup_db_test_env.img_build_cmds import DockerInspectImgToCheckItExistsCmdFactory, DockerBuildCmdFactory
from startup_db_test_env.startup_env_arg_builder import StartupDBDevEnvConfigArgBuilder


class CheckIfImageExists:
    def __init__(self, config_data, root_command, is_sudo=True):
        # if root_command == CheckIfImageExists.__ROOT_COMMAND_BUILD_IMG or
        image_name = config_data['image_name']
        self.__inspect_command = DockerInspectImgToCheckItExistsCmdFactory(image_name, is_sudo)

    def check_if_img_exists(self):
        proc = subprocess.Popen(self.__inspect_command.generate_exec_command(), stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()

        if len(stderr) > 2:
            return False

        return True


class ExecBuildImage:
    __ROOT_COMMAND_BUILD_IMG = "buildimg"

    @staticmethod
    def __default_stdout_logger(data):
        print("stdout : " + str(data))

    @staticmethod
    def __default_stderr_logger(data):
        print("stderr : " + str(data))

    def __init__(self, config_data, root_command, stdout_logger=None, stderr_logger=None, is_sudo=True):
        image_name: str
        image_name = config_data['image_name']  # or tag
        path = config_data['ImageConstructor']['docker_file_path']

        self.__build_command_factory = DockerBuildCmdFactory(path=path, tag=image_name, is_sudo=is_sudo)

        self.__root_command = root_command

        self.__stdout_logger = stdout_logger if stdout_logger is not None else ExecBuildImage.__default_stdout_logger
        self.__stderr_logger = stderr_logger if stderr_logger is not None else ExecBuildImage.__default_stderr_logger
        self.__force_build_image = config_data['ImageConstructor']['force_build_image']
        self.__rebuild_image = config_data['ImageConstructor']['rebuild_image']

    def __build_image_impl(self):
        command = self.__build_command_factory.generate_exec_command()
        cmd_managed = ExecCmdManaged(command)
        stdout_inst = cmd_managed.create_stdout_subscription()
        stderr_inst = cmd_managed.create_stderr_subscription()
        cmd_managed()

        while not cmd_managed.is_stopped():
            stdout_data = stdout_inst.read_string()
            if len(stdout_data) > 2:
                self.__stdout_logger(stdout_data)
            stderr_data = stderr_inst.read_string()
            if len(stderr_data) > 2:
                self.__stderr_logger(stderr_data)

    def build_image(self, img_exists):
        if not img_exists:
            if self.__root_command == ExecBuildImage.__ROOT_COMMAND_BUILD_IMG:
                self.__build_image_impl()
            elif self.__root_command == StartupDBDevEnvConfigArgBuilder.get_func_start_env():
                if self.__force_build_image:
                    self.__build_image_impl()
                else:
                    raise RuntimeError("Attempted to startup environment before building the image")
        elif self.__rebuild_image and self.__root_command == ExecBuildImage.__ROOT_COMMAND_BUILD_IMG:
            self.__build_image_impl()


if __name__ == "__main__":
    img_exist = CheckIfImageExists(config_data={'image_name': 'psql_ubuntu:0.4'}, root_command="")

    print(img_exist.check_if_img_exists())

    img_not_exists = CheckIfImageExists(config_data={'image_name': 'psql_ubuntu:0.5'}, root_command="")

    print(img_not_exists.check_if_img_exists())
