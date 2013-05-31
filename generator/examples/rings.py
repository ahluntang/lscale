#!/usr/bin/env python
# -*- coding: utf-8 -*-

from generator.topology.elements import NetworkComponent, IPComponent, UsedResources

from generator.topology import generate


def create(last_host_id, last_container_id, last_link_id, starting_address):
    return pre_aggregation(last_host_id, last_container_id, last_link_id, starting_address)


def pre_aggregation(last_host_id, last_container_id, last_link_id, starting_address):
    # create an IPComponent instance with the starting address
    addressing = IPComponent(starting_address)

    # Cityflow specific settings
    hosts_per_ring = 15
    rings = 5

    # set the starting number from where the topology module can generate new IDs
    # also add the IPComponent instance
    resources = UsedResources(last_host_id, last_container_id, last_link_id, addressing)

    # save the configuration in the generator.
    generate.set_resources(resources)

    # topology and components are saved in a dictionary
    topology_root = {}
    components = {}

    # Creating the cityflow specific topology.
    # 39 times: 10 per host, 9 on last host.

    # Adding a host to topology.
    host1_id = generate.add_host(topology_root)
    host1 = topology_root[host1_id]['id']
    # TODO: immediately retrieve reference to host object instead of host_id

    # Create pre aggregation rings connected to bridge
    for i in range(0, 10):
        pre_aggregation_rings(host1, components, hosts_per_ring, rings)

    # Adding a host to topology root for next batch of pre aggregation rings
    host2_id = generate.add_host(topology_root)
    host2 = topology_root[host2_id]['id']

    # Create pre aggregation rings connected to bridge
    for i in range(0, 10):
        pre_aggregation_rings(host2, components, hosts_per_ring, rings)

    # Adding a host to topology root for next batch of pre aggregation rings
    host3_id = generate.add_host(topology_root)
    host3 = topology_root[host3_id]['id']

    # Create pre aggregation rings connected to bridge
    for i in range(0, 10):
        pre_aggregation_rings(host3, components, hosts_per_ring, rings)

    # Adding a host to topology root
    host4_id = generate.add_host(topology_root)
    host4 = topology_root[host4_id]['id']

    # Create pre aggregation rings connected to bridge
    for i in range(0, 9):
        pre_aggregation_rings(host4, components, hosts_per_ring, rings)

    # After every component has been created
    # merge components into one dictionary,
    for component_id, component in components.items():
        generate.add_component_to_topology(topology_root, component)

    # return the dictionary with the topology.
    return topology_root


def pre_aggregation_rings(host, components, hosts_per_ring, rings):
    # The ring consists of a Line component
    # The line is closed into a ring using two bridges that are connected together.

    # Retrieve the  IPComponent from the generator.
    addressing = generate.get_resources().addressing

    # Use the IPComponent to get an addressing scheme for a line component
    addressing_scheme = addressing.addressing_for_line_component(hosts_per_ring, rings)

    # Create two bridge components, and connect them
    br1_component = generate.create_bridge(host)
    components[br1_component.component_id] = br1_component

    br2_component = generate.create_bridge(host)
    components[br2_component.component_id] = br2_component

    # Optional: create a management interface to bridge
    #generator.add_management_interface(host,br2_component, addressing_scheme)

    # Create link between bridges
    generate.connect_components(br1_component, br2_component, addressing_scheme)

    for i in range(0, rings):
        # Create ring and add it to bridges
        pre_aggregation_ring(host, components, br1_component, br2_component, hosts_per_ring, addressing_scheme)


def pre_aggregation_ring(host, components, br1_component, br2_component, hosts_per_ring, addressing_scheme):
    # Create a ring component for topology
    ring_component = generate.create_line(host, hosts_per_ring, addressing_scheme)
    components[ring_component.component_id] = ring_component

    # Add ring to first bridge
    generate.connect_components(ring_component, br1_component, addressing_scheme)

    # Add ring to second bridge
    generate.connect_components(ring_component, br2_component, addressing_scheme)
