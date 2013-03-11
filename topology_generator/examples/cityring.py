
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from topology.elements import NetworkComponent, IPComponent, UsedResources

from topology import generator


def create(last_host_id, last_container_id, last_link_id, starting_address) :
    addressing = IPComponent(starting_address)

    hosts_per_ring = 5
    rings = 2

    # set the starting point from where the topology module can create new IDs
    resources = UsedResources( last_host_id, last_container_id, last_link_id, addressing)
    generator.set_resources( resources )

    # topology and components are saved in a dictionary
    topology_root = { }
    components = { }

    # adding a host to topology root
    host1_id = generator.add_host( topology_root )

    # create pre aggregation rings connected to bridge
    pre_aggregation_rings( host1_id, components, hosts_per_ring, rings )

    # create a ring component for topology
    #addressing_scheme = addressing.addressing_for_ring_component(hosts_per_ring, rings)
    #ring_component = NetworkComponent()
    #generator.create_ring( host1_id, ring_component, hosts_per_ring, addressing_scheme, True )
    #components[ring_component.component_id] = ring_component

    # after every component has been created
    # merge components into main network topology
    for component_id, component in components.items( ) :
      generator.add_component_to_topology( topology_root, component )

    return topology_root


def pre_aggregation_rings(host_id, components, hosts_per_ring, rings) :

    addressing = generator.get_resources().addressing

    addressing_scheme = addressing.addressing_for_line_component(hosts_per_ring, rings)

    # create two bridge components, and connect them
    br1_component = NetworkComponent( )
    generator.create_bridge( host_id, br1_component )
    components[br1_component.component_id] = br1_component

    br2_component = NetworkComponent( )
    generator.create_bridge( host_id, br2_component )
    components[br2_component.component_id] = br2_component

    # create link between bridges
    generator.connect_components( br1_component, br2_component, addressing_scheme )

    for i in range( 0, rings ) :
        # create ring and add it to bridges
        pre_aggregation_ring(host_id, components, br1_component, br2_component, hosts_per_ring, addressing_scheme)


def pre_aggregation_ring(host_id, components, br1_component, br2_component, hosts_per_ring, addressing_scheme) :
    # create a ring component for topology
    ring_component = NetworkComponent()
    generator.create_line( host_id, ring_component, hosts_per_ring, addressing_scheme )
    components[ring_component.component_id] = ring_component

    # add ring to first bridge
    generator.connect_components( ring_component, br1_component, addressing_scheme )

    # add ring to second bridge
    generator.connect_components( ring_component, br2_component, addressing_scheme )
