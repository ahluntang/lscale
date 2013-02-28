#!/usr/bin/env python

import os, traceback, time, logging, itertools

from elements import Container, Bridge, NetworkInterface

import topology

def define_topology_details(resources):
    topology.set_resources(resources)

    topology_root = {}
    components = {}

    cityflow(topology_root, components)

    # merge components into main network topology
    for component_id, component in components.items():
        topology.add_component_to_topology(topology_root, component)

    return topology_root

def cityflow(topology_root, components):
    # adding a host to topology
    host_id = topology.add_host(topology_root)

    # create two bridge components, and connect them
    br1_component = topology.NetworkComponent()
    topology.create_bridge(host_id, br1_component)
    components[br1_component.component_id] = br1_component

    br2_component = topology.NetworkComponent()
    topology.create_bridge(host_id, br2_component)
    components[br2_component.component_id] = br2_component

    # create link between bridges
    topology.connect_components(br1_component,br2_component)

    # create a ring component for topology
    ringcomponent = topology.NetworkComponent()
    topology.create_ring(host_id, ringcomponent)
    components[ringcomponent.component_id] = ringcomponent

    # add ring to first bridge
    topology.connect_components(ringcomponent,br1_component)
    # add ring to second bridge
    topology.connect_components(ringcomponent,br2_component)
