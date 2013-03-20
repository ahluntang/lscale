
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from topology.elements import NetworkComponent, IPComponent, UsedResources

from topology import generator
import random


def create(last_host_id, last_container_id, last_link_id, starting_address) :

    # create an IPComponent instance with the starting address
    addressing = IPComponent(starting_address)

    hosts_per_ring = 3
    rings = 2

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
    pre_aggregation_rings( host1, components, hosts_per_ring, rings )


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

    # create link between bridges
    #generator.connect_components( br1_component, br2_component, addressing_scheme )

    # alternative: connect the bridge elements
    # get bridges from the components
    br1 = br1_component.topology['bridges'][random.choice(br1_component.topology['bridges'].keys())]
    br2 = br2_component.topology['bridges'][random.choice(br2_component.topology['bridges'].keys())]
    generator.connect_bridges(br1, br2)

    ringcomp_ids = []
    for i in range( 0, rings ) :
        # create ring and add it to bridges
        comp_id = pre_aggregation_ring(host, components, br1_component, br2_component, hosts_per_ring, addressing_scheme)
        ringcomp_ids.append(comp_id)

    r1 = components[ringcomp_ids[0]]
    r2 = components[ringcomp_ids[1]]

    c1 = r1.topology['containers'][random.choice(r1.topology['containers'].keys())]
    c2 = r2.topology['containers'][random.choice(r2.topology['containers'].keys())]

    addressing_scheme = addressing.addressing_for_container_connection()
    generator.connect_containers(c1,c2,r1,r2,addressing_scheme)

def pre_aggregation_ring(host, components, br1_component, br2_component, hosts_per_ring, addressing_scheme) :
    # create a ring component for topology
    ring_component = generator.create_line( host, hosts_per_ring, addressing_scheme )
    components[ring_component.component_id] = ring_component

    # add ring to first bridge
    generator.connect_components( ring_component, br1_component, addressing_scheme )

    # add ring to second bridge
    generator.connect_components( ring_component, br2_component, addressing_scheme )

    return ring_component.component_id



