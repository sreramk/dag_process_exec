import sys
import time

from process_exec.exec_cmd_managed import ExecCmdManaged
from third_party.kbhit import KBHit

if __name__ == "__main__":

    cmd_managed = ExecCmdManaged(["sudo", "-S", "sh"])
    # cmd_managed = ExecCmdManaged(["sh"])

    cmd_managed()

    stdout_inst = cmd_managed.create_stdout_subscription()
    stderr_inst = cmd_managed.create_stderr_subscription()
    stdin_inst = cmd_managed.get_stdin_writer()

    kb = KBHit()

    while not cmd_managed.is_stopped():

        out_data = stdout_inst.read_string()
        if len(out_data) != 0:
            print("out:", out_data, end='')
            sys.stdout.flush()

        err_data = stderr_inst.read_string()
        if len(err_data) != 0:
            print("err :", file=sys.stderr, end='')
            print(err_data, file=sys.stderr,  end='')
            sys.stderr.flush()

        if kb.kbhit():
            c = kb.getch()
            stdin_inst.write_nowait(str.encode(c))
            print(c, end='')
            sys.stdout.flush()

    # Note that, we may have to manually end the stdin loop.
    cmd_managed.end_stdin_writer()
    time.sleep(0.001)
    out_data = stdout_inst.read_string()
    if len(out_data) != 0:
        print("out:", out_data, end='')

    err_data = stderr_inst.read_string()
    if len(err_data) != 0:
        print("err :", end='')
        print(err_data, end='')
