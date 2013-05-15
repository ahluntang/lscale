
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


def install(package):

    if os.geteuid() != 0:
        raise exceptions.InsufficientRightsException("Installing packages requires root privileges")

    cmd = ""
    if package == "all" or package == "openvswitch":
        cmd += "./configurator/templates/install_openvswitch.sh\n"

    if package == "all" or package == "lxc":
        cmd += "./configurator/templates/install_lxc.sh\n"

    # check if proxy needed
    if config.proxy:
        cmd = "export http_proxy=%s\n%s" % (config.proxy, cmd)

    try:
        script.command(cmd)
    except exceptions.ScriptException as e:
        raise exceptions.ConfiguratorException(e)


def restart(service):
    cmd = "service {} ".format(service)
    if service == "openvswitch-switch":
        parameter = "force-reload-kmod"
    else:
        parameter = "restart"
    cmd += parameter
    script.command(cmd)


def create_container(container_name="base", backing_store="none", template="ubuntu"):

    if os.geteuid() != 0:
        raise exceptions.InsufficientRightsException("Creating container requires root privileges")

    cmd = "./configurator/templates/create_container.sh %s %s %s" % (container_name, backing_store, template)

    # check if proxy needed
    if config.proxy:
        cmd = "export http_proxy=%s\n%s" % (config.proxy, cmd)

    try:
        script.command(cmd)
    except exceptions.ScriptException as e:
        raise exceptions.ConfiguratorException(e)


def clone_container(container_name, original_container="base", snapshot=False):

    if os.geteuid() != 0:
        raise exceptions.InsufficientRightsException("Cloning container requires root privileges")

    if snapshot:
        cmd = "./configurator/templates/clone_container.sh %s %s %s" % (container_name, original_container, "snapshot")
    else:
        cmd = "./configurator/templates/clone_container.sh %s %s" % (container_name, original_container)

    try:
        script.command(cmd)
    except exceptions.ScriptException as e:
        raise exceptions.ConfiguratorException(e)


def create_lvm(name="lxc", device="/dev/sda", partition="4", cachesize=30):

    if os.geteuid() != 0:
        raise exceptions.InsufficientRightsException("Creating LVM requires root privileges")

    cmd = "./configurator/templates/create_lvm.sh %s %s %s %s" % (name, device, partition, cachesize)

    try:
        script.command(cmd)
    except exceptions.ScriptException as e:
        raise exceptions.ConfiguratorException(e)
