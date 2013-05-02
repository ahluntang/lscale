#!/usr/bin/env python
# -*- coding: utf-8 -*-


from generator.topology import elements, exporter

from generator.examples import *


def generate(example, filename, starting_address="172.16.0.0", last_host_id=0, last_container_id=0, last_link_id=0):
    if example == 'cityflow':
        # create an example topology: cityflow preaggregation phase.
        # see examples package for more info
        created_topology = cityflow.create(last_host_id, last_container_id, last_link_id, starting_address)
    elif example == 'citybus':
        created_topology = citybus.create(last_host_id, last_container_id, last_link_id, starting_address)
    elif example == 'citystar':
        created_topology = citystar.create(last_host_id, last_container_id, last_link_id, starting_address)
    elif example == 'smalltop':
        created_topology = smalltop.create(last_host_id, last_container_id, last_link_id, starting_address)
    else:
        created_topology = cityring.create(last_host_id, last_container_id, last_link_id, starting_address)
        # export topology to xml file
    exporter.write_topology_xml(created_topology, filename)

