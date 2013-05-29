#!/usr/bin/env python
# -*- coding: utf-8 -*-

from generator.topology.elements import NetworkComponent, IPComponent, UsedResources

from generator.topology import generate


def create(last_host_id, last_container_id, last_link_id, starting_address) :
    addressing = IPComponent(starting_address)

    # set the starting point from where the topology module can create new IDs
    resources = UsedResources(last_host_id, last_container_id, last_link_id, addressing)
    generate.set_resources(resources)

    # topology and components are saved in a dictionary
    topology_root = {}
    components = {}

    # adding a host to topology root
    host1_id = generate.add_host(topology_root)
    host = topology_root[host1_id]['id']


    # create addressing scheme for star component
    addressing = generate.get_resources().addressing
    addressing_scheme = addressing.addressing_for_bus_component(5)

    # create a bus component in host
    bus_component = generate.create_bus(host, 5, addressing_scheme)
    components[bus_component.component_id] = bus_component

    # after every component has been created
    # merge components into main network topology
    for component_id, component in components.items() :
        generate.add_component_to_topology(topology_root, component)

    return topology_root
