

import sys
from subprocess import PIPE, Popen
from threading import Thread
from utilities import exceptions

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
        sys.stdout.write(line)
    out.close()


def command(cmd, verbose=True):
    try:
        if verbose:
            print_start_command(cmd)
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        q = Queue()
        t = Thread(target=enqueue_output, args=(p.stdout, q))
        t.daemon = True
        # thread dies with the program
        t.start()
        p.wait()
        if verbose:
            print_done_command(cmd)
    except Exception as e:
        raise exceptions.ScriptException(e)


def print_start_command(cmd):
    before = "================\n" \
             "Running command:\n"
    after = "\n================\n"
    print("%s%s%s" % (before, cmd, after))


def print_done_command(cmd):
    before = "================\n" \
             "Done running command:\n"
    after = "\n================\n"
    print("%s%s%s" % (before, cmd, after))
