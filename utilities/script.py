import sys
import threading
import subprocess

from utilities import exceptions


def reader(shell, lines):
        for line in shell.stdout:
            lines.append(line)
            sys.stdout.write(line)


def command(cmd):
    shell = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #output, error = shell.communicate()
    lines = []

    t = threading.Thread(target=reader(shell, lines))
    t.start()
    shell.wait()
    t.join()

    if shell.returncode != 0:
        err_msg = "Script error: %s\nOUTPUT\n %s" % (cmd, lines)
        raise exceptions.ScriptException(err_msg)
