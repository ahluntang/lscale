
#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import subprocess

from jinja2 import Environment, FileSystemLoader
from utilities import exceptions


def configure():

    if os.geteuid() == 0:
        template_environment = Environment(loader=FileSystemLoader('configurator/templates'))
        create_base_container()

    else:
        raise exceptions.InsufficientRightsException("Configuring system requires root privileges")


def create_base_container(container_name="base", backing_store=""):
    cmd = "./configurator/create_base.sh %s %s" % (container_name, backing_store)
    subprocess.call(cmd, shell=True)


def clone_container(container_name, original_container="base", snapshot=False):
    if snapshot:
        cmd = "./configurator/clone_container.sh %s %s %s" % (container_name, original_container, "snapshot")
    else:
        cmd = "./configurator/clone_container.sh %s %s" % (container_name, original_container)
    subprocess.call(cmd, shell=True)
