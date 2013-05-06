#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from generator.topology import elements, exporter

from generator.examples import *


def generate(example, filename, starting_address="172.16.0.0", last_host_id=0, last_container_id=0, last_link_id=0):
    str = "%s.create(last_host_id, last_container_id, last_link_id, starting_address)" % example
    created_topology = eval(str)
    exporter.write_topology_xml(created_topology, filename)

