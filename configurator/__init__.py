
#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

from jinja2 import Environment, FileSystemLoader
from utilities import exceptions, script, systemconfig


def auto_configure():

    print("Autoconfiguration selected.")
    if os.geteuid() == 0:
        install("all")
        create_lvm()
        create_container("base", "lvm", "ubuntu")
        create_container("base_no_backingstore", "none", "ubuntu")
        build_routeflow(True)

        print("Finished autoconfiguration of this host.")
    else:
        raise exceptions.InsufficientRightsException("Configuring system requires root privileges")


def install(package):
    print("Installing package: {}".format(package))
    if os.geteuid() != 0:
        raise exceptions.InsufficientRightsException("Installing packages requires root privileges")

    cmd = ""
    if package == "all" or package == "openvswitch":
        cmd += "./configurator/templates/install_openvswitch.sh\n"

    if package == "all" or package == "lxc":
        cmd += "./configurator/templates/install_lxc.sh\n"

    # check if proxy needed
    if systemconfig.proxy:
        cmd = "export http_proxy=%s\n%s" % (systemconfig.proxy, cmd)

    try:
        script.command(cmd)
    except exceptions.ScriptException as e:
        raise exceptions.ConfiguratorException(e)


def restart(service):
    print("Restarting service: {}".format(service))
    cmd = "service {}".format(service)
    if service == "openvswitch-switch":
        parameter = " force-reload-kmod"
    elif service == "openvswitch":
        parameter = "-switch force-reload-kmod"
    else:
        parameter = " restart"
    cmd += parameter
    script.command(cmd)


def create_container(container_name="base", backing_store="none", template="ubuntu"):

    print("Creating container {} based on {} with {} as backingstore".format(container_name, template, backing_store))
    if os.geteuid() != 0:
        raise exceptions.InsufficientRightsException("Creating container requires root privileges")

    cmd = "./configurator/templates/create_container.sh %s %s %s" % (container_name, backing_store, template)

    # check if proxy needed
    if systemconfig.proxy:
        cmd = "export http_proxy=%s\n%s" % (systemconfig.proxy, cmd)

    try:
        script.command(cmd)
    except exceptions.ScriptException as e:
        raise exceptions.ConfiguratorException(e)


def clone_container(container_name, original_container="base", snapshot=False):
    suffix = ""
    if snapshot:
        suffix = "using snapshot"
    print("Cloning {} to {} {}".format(original_container, container_name, suffix))
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

    print("Setting up LVM volume group named {} on {}{} with a cache of {}G".format(name, device, partition, cachesize))
    if os.geteuid() != 0:
        raise exceptions.InsufficientRightsException("Creating LVM requires root privileges")

    cmd = "./configurator/templates/create_lvm.sh %s %s %s %s" % (name, device, partition, cachesize)

    try:
        script.command(cmd)
    except exceptions.ScriptException as e:
        raise exceptions.ConfiguratorException(e)

def build_routeflow(create_vms=False):
    print("Setting up system for RouteFlow.")
    if os.geteuid() != 0:
        raise exceptions.InsufficientRightsException("Setting up system for RouteFlow requires root privileges")

    if create_vms:
        options = "-i"
    else:
        options = ""
    cmd = "./configurator/templates/routeflow.sh %s " % options

    # check if proxy needed
    if systemconfig.proxy:
        cmd = "export http_proxy=%s\n%s" % (systemconfig.proxy, cmd)

    try:
        script.command(cmd)
    except exceptions.ScriptException as e:
        raise exceptions.ConfiguratorException(e)
