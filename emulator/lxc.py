import subprocess
import os

# LXC Python Library
# for compatibility with LXC 0.8 and 0.9
# on Ubuntu 12.04/12.10/13.04

# Author: Elie Deloumeau
# Contact: elie@deloumeau.fr

# The MIT License (MIT)
# Copyright (c) 2013 Elie Deloumeau

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the
#  following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
#  WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
#  ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
# USE OR OTHER DEALINGS IN THE SOFTWARE.


def _run(cmd, output=True):
    """
    To run command easier
    """
    if output:
        return subprocess.check_output('{}'.format(cmd), shell=True)
    return subprocess.check_call('{}'.format(cmd), shell=True)  # returns 0 for True


class ContainerAlreadyExists(Exception): pass


class ContainerDoesntExists(Exception): pass


class ContainerAlreadyRunning(Exception): pass


class ContainerNotRunning(Exception): pass


def exists(container):
    '''
    Check if container exists
    '''
    if container in ls(): return True
    return False


def create(container, template='ubuntu', storage=None, config=None):
    '''
    Create a container (without all options)
    Default template: Ubuntu
    '''
    if exists(container): raise ContainerAlreadyExists('Container {} already created!'.format(container))

    command = 'lxc-create -n {}'.format(container)
    command += ' -t {}'.format(template)
    if storage: command += ' -B {}'.format(storage)
    if config: command += ' -f {}'.format(config)
            
    return _run(command)


def clone(original, container, snapshot=False):
    '''
    Clones an existing container
    '''
    if exists(container): raise ContainerAlreadyExists('Container {} already created!'.format(container))
    if not exists(original): raise ContainerDoesntExists('Container {} does not exist!'.format(original))

    command = 'lxc-clone -n {} -o {}'.format(container, original)
    if snapshot: command += ' -s'
    return _run(command)


def info(container):
    '''
    Check info from lxc-info*
        *I hope that the developers will not change this output
    '''
    if not exists(container): raise ContainerDoesntExists('Container {} does not exist!'.format(container))

    output = _run('lxc-info -n {}'.format(container), output=True).splitlines()

    return {'state': output[0].split()[1],
            'pid': output[1].split()[1]}


def ls():
    '''
    List containers directory

    Note: Directory mode for Ubuntu 12/13 compatibility
    '''
    try: ct_list = os.listdir('/var/lib/lxc/')
    except OSError: ct_list = []
    return sorted(ct_list)


def listx():
    '''
    List all containers with status (Running, Frozen or Stopped) in a dict
    Same as lxc-list or lxc-ls --fancy (0.9)
    '''
    stopped = []
    frozen = []
    running = []

    for container in ls():
        state = info(container)['state']
        if state == 'RUNNING':
            running.append(container)
        elif state == 'FROZEN':
            frozen.append(container)
        elif state == 'STOPPED':
            stopped.append(container)

    return {'RUNNING': running,
            'FROZEN': frozen,
            'STOPPED': stopped}


def running():
    return listx()['RUNNING']


def frozen():
    return listx()['FROZEN']


def stopped():
    return listx()['STOPPED']


def start(container):
    '''
    Starts a container
    '''
    if not exists(container): raise ContainerDoesntExists('Container {} does not exist!'.format(container))
    if container in running(): raise ContainerAlreadyRunning('Container {} is already running!'.format(container))
    return _run('lxc-start -dn {}'.format(container))


def stop(container):
    '''
    Stops a container
    '''
    if not exists(container): raise ContainerDoesntExists('Container {} does not exist!'.format(container))
    if container in stopped(): raise ContainerNotRunning('Container {} is not running!'.format(container))
    return _run('lxc-stop -n {}'.format(container))


def freeze(container):
    '''
    Freezes a container
    '''
    if not exists(container): raise ContainerDoesntExists('Container {} does not exist!'.format(container))
    if not container in running(): raise ContainerNotRunning('Container {} is not running!'.format(container))
    return _run('lxc-freeze -n {}'.format(container))


def unfreeze(container):
    '''
    Unfreezes a container
    '''
    if not exists(container): raise ContainerDoesntExists('Container {} does not exist!'.format(container))
    if not container in frozen(): raise ContainerNotRunning('Container {} is not frozen!'.format(container))
    return _run('lxc-unfreeze -n {}'.format(container))


def destroy(container):
    '''
    Destroys a container
    '''
    if not exists(container): raise ContainerDoesntExists('Container {} does not exist!'.format(container))
    return _run('lxc-destroy -fn {}'.format(container))


def checkconfig():
    '''
    Returns the output of lxc-checkconfig (colors cleared)
    '''
    return _run('lxc-checkconfig', output=True).replace('[1;32m', '').replace('[1;33m', '').replace('[0;39m', '').replace('[1;32m', '').replace('\x1b', '').replace(': ', ':').split('\n')


def wait(name, states):
    '''
    wait until the container reaches the specified state or states
    states can be or-ed or and-ed
    '''
    if not exists(name):
        raise ContainerDoesntExists("The container {} does not exist!".format(name))

    cmd = "lxc-wait -n %s -s %s" % (name, states)

    result = None
    finished = False
    while not finished:
        try:
            result = _run(cmd)
            finished = True
        except:
            pass
    return result
