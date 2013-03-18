#!/usr/bin/env python
# -*- coding: utf-8 -*-

from topology.elements import NetworkComponent, IPComponent, UsedResources

from topology import generator

def create(last_host_id, last_container_id, last_link_id, starting_address) :
    return pre_aggregation(last_host_id, last_container_id, last_link_id, starting_address)

def pre_aggregation(last_host_id, last_container_id, last_link_id, starting_address) :
    addressing = IPComponent(starting_address)

    hosts_per_ring = 5
    rings = 5

    # set the starting point from where the topology module can create new IDs
    resources = UsedResources( last_host_id, last_container_id, last_link_id, addressing)
    generator.set_resources( resources )

    # topology and components are saved in a dictionary
    topology_root = { }
    components = { }

    # adding a host to topology root
    host1_id = generator.add_host( topology_root )
    host1 = topology_root[host1_id]['id']

    # create pre aggregation rings connected to bridge
    for i in range( 0, 10 ) :
        pre_aggregation_rings( host1, components, hosts_per_ring, rings )

    # adding a host to topology root
    host2_id = generator.add_host( topology_root )
    host2 = topology_root[host2_id]['id']

    # create pre aggregation rings connected to bridge
    for i in range( 0, 10 ) :
        pre_aggregation_rings( host2, components, hosts_per_ring, rings )

    # adding a host to topology root
    host3_id = generator.add_host( topology_root )
    host3 = topology_root[host3_id]['id']

    # create pre aggregation rings connected to bridge
    for i in range( 0, 10 ) :
        pre_aggregation_rings( host3, components, hosts_per_ring, rings )

    # adding a host to topology root
    host4_id = generator.add_host( topology_root )
    host4 = topology_root[host4_id]['id']

    # create pre aggregation rings connected to bridge
    for i in range( 0, 9 ) :
        pre_aggregation_rings( host4, components, hosts_per_ring, rings )


    # after every component has been created
    # merge components into main network topology
    for component_id, component in components.items( ) :
      generator.add_component_to_topology( topology_root, component )

    return topology_root


def pre_aggregation_rings(host, components, hosts_per_ring, rings) :

    addressing = generator.get_resources().addressing

    addressing_scheme = addressing.addressing_for_line_component(hosts_per_ring, rings)

    # create two bridge components, and connect them
    br1_component = generator.create_bridge( host )
    components[br1_component.component_id] = br1_component

    br2_component = generator.create_bridge( host )
    components[br2_component.component_id] = br2_component

    # create a management interface to bridge
    generator.add_management_interface(host,br2_component, addressing_scheme)

    # create link between bridges
    generator.connect_components( br1_component, br2_component, addressing_scheme )

    for i in range( 0, rings ) :
        # create ring and add it to bridges
        pre_aggregation_ring(host, components, br1_component, br2_component, hosts_per_ring, addressing_scheme)


def pre_aggregation_ring(host, components, br1_component, br2_component, hosts_per_ring, addressing_scheme) :
    # create a ring component for topology
    ring_component = generator.create_line( host, hosts_per_ring, addressing_scheme )
    components[ring_component.component_id] = ring_component

    # add ring to first bridge
    generator.connect_components( ring_component, br1_component, addressing_scheme )

    # add ring to second bridge
    generator.connect_components( ring_component, br2_component, addressing_scheme )
