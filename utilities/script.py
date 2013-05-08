import sys
import multiprocessing
import subprocess

from utilities import exceptions


def reader(cmd, lines):
    shell = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in shell.stdout:
        lines.append(line)
        sys.stdout.write(line)
    return lines


def command(cmd):

    #output, error = shell.communicate()
    lines = []

    t = multiprocessing.Process(target=reader, args=(cmd, lines))
    t.start()
    t.join()

    #if shell.returncode != 0:
    #    err_msg = "Script error: %s\nOUTPUT\n %s" % (cmd, lines)
    #    raise exceptions.ScriptException(err_msg)
