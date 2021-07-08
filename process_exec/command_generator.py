import abc


class CommandGenerator(abc.ABC):

    @abc.abstractmethod
    def generate_exec_command(self) -> list:
        pass

    @abc.abstractmethod
    def is_sudo(self) -> bool:
        pass
