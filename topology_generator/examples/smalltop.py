#!/usr/bin/env python
# -*- coding: utf-8 -*-

from topology.elements import NetworkComponent, IPComponent, UsedResources

from topology import generator


#!/usr/bin/env python
# -*- coding: utf-8 -*-

from topology.elements import NetworkComponent, IPComponent, UsedResources

from topology import generator


def create(last_host_id, last_container_id, last_link_id, starting_address) :
    addressing = IPComponent(starting_address)

    hosts_per_ring = 2
    rings = 1

    # set the starting point from where the topology module can create new IDs
    resources = UsedResources( last_host_id, last_container_id, last_link_id, addressing)
    generator.set_resources( resources )

    # topology and components are saved in a dictionary
    topology_root = { }
    components = { }

    # adding a host to topology root
    host_id = generator.add_host( topology_root )
    host = topology_root[host_id]['id']


    # create pre aggregation rings connected to bridge
    pre_aggregation_rings( host, components, hosts_per_ring, rings )

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


def pre_aggregation_rings(host, components, hosts_per_ring, rings) :

    addressing = generator.get_resources().addressing

    addressing_scheme = None #addressing.addressing_for_line_component(hosts_per_ring, rings)

    # create  bridge component
    br1_component = generator.create_bridge( host )
    components[br1_component.component_id] = br1_component

    pre_aggregation_line(host, components, br1_component, hosts_per_ring, addressing_scheme)


def pre_aggregation_line(host, components, br1_component, hosts_per_ring, addressing_scheme) :
    # create a ring component for topology
    ring_component = generator.create_line( host, hosts_per_ring, addressing_scheme )
    components[ring_component.component_id] = ring_component

    # add ring to bridge
    generator.connect_components( ring_component, br1_component, addressing_scheme )

