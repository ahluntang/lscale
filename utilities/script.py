# import sys
# import threading
# import subprocess
#
# from utilities import exceptions


# def reader(shell, lines):
#         for line in shell.stdout:
#             lines.append(line)
#             sys.stdout.write(line)
#
#
# def command(cmd):
#     shell = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     #output, error = shell.communicate()
#     lines = []
#
#     t = threading.Thread(target=reader(shell, lines))
#     t.start()
#     #shell.wait()
#     t.join()
#
#     if shell.returncode != 0:
#         err_msg = "Script error: %s\nOUTPUT\n %s" % (cmd, lines)
#         raise exceptions.ScriptException(err_msg)


import sys
from subprocess import PIPE, Popen
from threading import Thread

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
    cmd = "export http_proxy=http://proxy.atlantis.ugent.be:8080 \n%s" % cmd
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    q = Queue()
    t = Thread(target=enqueue_output, args=(p.stdout, q))
    t.daemon = True
    # thread dies with the program
    t.start()
    p.wait()
    # try:
    #     line = q.get_nowait()  # or q.get(timeout=.1)
    # except Empty:
    #     pass
    #     #print('no output yet')
    # else:  # got line
    #     sys.stdout.write(line)
