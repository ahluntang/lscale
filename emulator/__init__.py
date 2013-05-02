#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

from jinja2 import Environment, FileSystemLoader
from emulator import topology_parser, interaction, elements
from utilities import exceptions


def emulate(filename, host_id, parsed_topology):
    """

    :param filename:
    :param host_id:
    :param parsed_topology:
    :raise:
    """
    if os.geteuid() == 0:
        template_environment = Environment(loader=FileSystemLoader('emulator/templates'))
        topology_parser.parse(filename, template_environment, parsed_topology, host_id)
        interaction.interact(parsed_topology, host_id)
        elements.cleanup(template_environment)
    else:
        raise exceptions.InsufficientRightsException("Emulating requires root privileges")
