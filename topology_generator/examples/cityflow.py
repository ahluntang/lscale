#!/usr/bin/env python
from elements import NetworkComponent

import topology


def pre_aggregation(last_host_id, last_container_id, last_link_id) :
    # set the starting point from where the topology module can create new IDs
    resources = topology.UsedResources( last_host_id, last_container_id, last_link_id )
    topology.set_resources( resources )

    # topology and components are saved in a dictionary
    topology_root = { }
    components = { }

    # adding a host to topology root
    host1_id = topology.add_host( topology_root )

    # create pre aggregation rings connected to bridge
    for i in range( 0, 10 ) :
        pre_aggregation_rings( host1_id, components )

    # adding a host to topology root
    host2_id = topology.add_host( topology_root )

    # create pre aggregation rings connected to bridge
    for i in range( 0, 10 ) :
        pre_aggregation_rings( host2_id, components )

    # merge components into main network topology
    for component_id, component in components.items( ) :
        topology.add_component_to_topology( topology_root, component )

    return topology_root


def pre_aggregation_rings(host_id, components) :
    # create two bridge components, and connect them
    br1_component = NetworkComponent( )
    topology.create_bridge( host_id, br1_component )
    components[br1_component.component_id] = br1_component

    br2_component = NetworkComponent( )
    topology.create_bridge( host_id, br2_component )
    components[br2_component.component_id] = br2_component

    # create link between bridges
    topology.connect_components( br1_component, br2_component )

    for i in range( 0, 5 ) :
        # create ring and add it to bridges
        pre_aggregation_ring( host_id, components, br1_component, br2_component )


def pre_aggregation_ring(host_id, components, br1_component, br2_component) :
    # create a ring component for topology
    ring_component = NetworkComponent( )
    topology.create_ring( host_id, ring_component )
    components[ring_component.component_id] = ring_component

    # add ring to first bridge
    topology.connect_components( ring_component, br1_component )
    # add ring to second bridge
    topology.connect_components( ring_component, br2_component )
