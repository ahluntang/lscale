

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


def command(cmd):
    try:
        cmd = "%s" % cmd
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        q = Queue()
        t = Thread(target=enqueue_output, args=(p.stdout, q))
        t.daemon = True
        # thread dies with the program
        t.start()
        p.wait()
    except Exception as e:
        raise exceptions.ScriptException(e)
