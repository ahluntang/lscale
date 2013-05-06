
#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import subprocess
import threading

from jinja2 import Environment, FileSystemLoader
from utilities import exceptions


def configure():

    if os.geteuid() == 0:
        template_environment = Environment(loader=FileSystemLoader('configurator/templates'))
        create_container()

    else:
        raise exceptions.InsufficientRightsException("Configuring system requires root privileges")


def create_container(container_name="base", backing_store="none", template="ubuntu"):

    cmd = "./configurator/templates/create_container.sh %s %s %s" % (container_name, backing_store, template)

    shell = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #output, error = shell.communicate()
    lines = []

    def reader(shell):
        for line in shell.stdout:
            lines.append(line)
            sys.stdout.write(line)

    t = threading.Thread(target=reader(shell))
    t.start()
    shell.wait()
    t.join()
    #print(output)

    if shell.returncode != 0:
        err_msg = "Could not create container: %s\nOUTPUT\n %s\nError\n%s" % (cmd, lines)
        raise exceptions.ConfiguratorException(err_msg)


def clone_container(container_name, original_container="base", snapshot=False):

    if snapshot:
        cmd = "./configurator/templates/clone_container.sh %s %s %s" % (container_name, original_container, "snapshot")
    else:
        cmd = "./configurator/templates/clone_container.sh %s %s" % (container_name, original_container)

    shell = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = shell.communicate()
    print(output)

    if shell.returncode != 0:
        err_msg = "Could not clone container: %s\nOUTPUT\n %s\nError\n%s" % (cmd, output, error)
        raise exceptions.ConfiguratorException(err_msg)


def create_lvm(name="lxc", device="/dev/sda", partition="1"):

    cmd = "./configurator/templates/create_lvm.sh %s %s %s" % (name, device, partition)

    shell = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = shell.communicate()
    print(output)

    if shell.returncode != 0:
        err_msg = "Could not create lvm: %s\nOUTPUT\n %s\nError\n%s" % (cmd, output, error)
        raise exceptions.ConfiguratorException(err_msg)
