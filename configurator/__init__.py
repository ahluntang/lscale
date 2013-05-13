
#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

from jinja2 import Environment, FileSystemLoader
from utilities import exceptions, script, config


def configure():

    if os.geteuid() == 0:
        template_environment = Environment(loader=FileSystemLoader('configurator/templates'))
        create_container()

    else:
        raise exceptions.InsufficientRightsException("Configuring system requires root privileges")


def create_container(container_name="base", backing_store="none", template="ubuntu"):

    cmd = "./configurator/templates/create_container.sh %s %s %s" % (container_name, backing_store, template)

    # check if proxy needed
    if config.proxy:
        cmd = "export http_proxy=%s\n%s" % (config.proxy, cmd)

    try:
        script.command(cmd)
    except exceptions.ScriptException as e:
        raise exceptions.ConfiguratorException(e)


def clone_container(container_name, original_container="base", snapshot=False):

    if snapshot:
        cmd = "./configurator/templates/clone_container.sh %s %s %s" % (container_name, original_container, "snapshot")
    else:
        cmd = "./configurator/templates/clone_container.sh %s %s" % (container_name, original_container)

    try:
        script.command(cmd)
    except exceptions.ScriptException as e:
        raise exceptions.ConfiguratorException(e)


def create_lvm(name="lxc", device="/dev/sda", partition="1"):

    cmd = "./configurator/templates/create_lvm.sh %s %s %s" % (name, device, partition)

    try:
        script.command(cmd)
    except exceptions.ScriptException as e:
        raise exceptions.ConfiguratorException(e)
