import json

from startup_db_test_env.build_docker_img import CheckIfImageExists, ExecBuildImage
from startup_db_test_env.command_args import StartupScriptParser
from startup_db_test_env.exec_startup_env import ExecStartupEnv
from startup_db_test_env.startup_env_arg_builder import StartupDBDevEnvConfigArgBuilder


def parse_and_get_config_data():
    parser_inst = StartupScriptParser()
    parser_inst.parse_arguments()
    config_path = parser_inst.get_config_path()

    with open(config_path) as f:
        config_data = json.load(f)

    parser_inst.updated_config_with_args(config_data)
    root_command = parser_inst.get_root_command()
    return config_data, root_command


def execution_list(logger_stdout=None, logger_stderr=None):
    config_data, root_command = parse_and_get_config_data()

    chk_image_exists = CheckIfImageExists(config_data, root_command)

    exec_build_image = ExecBuildImage(config_data, root_command, logger_stdout, logger_stderr)
    exec_build_image.build_image(chk_image_exists.check_if_img_exists())

    if chk_image_exists.check_if_img_exists():
        """
        Images are not supposed to be pulled from the docker hub, and doing so is treated as a security issue. 
        """
        startup_db_env_config = StartupDBDevEnvConfigArgBuilder(config_data, root_command)
        exec_startup_env = ExecStartupEnv(config_arg_builder=startup_db_env_config, logger_stdout=logger_stdout,
                                          logger_stderr=logger_stderr)
        exec_startup_env.execute_command_fnc()

