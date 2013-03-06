#!/usr/bin/env python
# -*- coding: utf-8 -*-

from topology.elements import NetworkComponent, IPComponent, UsedResources

from topology import generator

def citybus(last_host_id, last_container_id, last_link_id, starting_address) :
    addressing = IPComponent(starting_address)


    # set the starting point from where the topology module can create new IDs
    resources = UsedResources(last_host_id, last_container_id, last_link_id, addressing)
    generator.set_resources(resources)

    # topology and components are saved in a dictionary
    topology_root = {}
    components = {}

    # adding a host to topology root
    host1_id = generator.add_host(topology_root)


    # create addressing scheme for star component
    addressing = generator.get_resources().addressing
    addressing_scheme = addressing.addressing_for_bus_component(5)

    # create a bus component in host
    bus_component = NetworkComponent()
    generator.create_bus(host1_id, bus_component, 5, addressing_scheme)
    components[bus_component.component_id] = bus_component

    # after every component has been created
    # merge components into main network topology
    for component_id, component in components.items() :
        generator.add_component_to_topology(topology_root, component)

    return topology_root
