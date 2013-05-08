# -*- coding: utf-8 -*-

from generator.topology.elements import NetworkComponent, IPComponent, UsedResources
from generator.topology import gen_components
from utilities.lscale import ContainerType, BridgeType


def create(last_host_id, last_container_id, last_link_id, starting_address):
     # create an IPComponent instance with the starting address
    addressing = IPComponent(starting_address)

    # set the starting number from where the topology module can generate new IDs
    # also add the IPComponent instance
    resources = UsedResources(last_host_id, last_container_id, last_link_id, addressing)

    # save the configuration in the generator.
    gen_components.set_resources(resources)

    # topology and components are saved in a dictionary
    topology_root = {}
    components = {}

    # begin creating the topology

    # Adding a host to topology.
    host_id = gen_components.add_host(topology_root)
    host = topology_root[host_id]['id']

    bridge_component = gen_components.create_bridge(host, BridgeType.OPENVSWITCH)
    components[bridge_component.component_id] = bridge_component

    container_component = gen_components.create_container(host, ContainerType.LXC)
    components[container_component.component_id] = container_component

    bridge = bridge_component.topology['bridges'][resources.get_last_bridge_id()]
    container = container_component.topology['containers'][resources.get_last_container_id()]

    gen_components.connect_container_bridge(container, bridge)

    # add new container
    container2_component = gen_components.create_container(host, ContainerType.LXC)
    components[container2_component.component_id] = container2_component

    container2 = container2_component.topology['containers'][resources.get_last_container_id()]

    gen_components.connect_container_bridge(container2, bridge)

    # end creating the topology
    # After every component has been created
    # merge components into one dictionary,
    for component_id, component in components.items():
        gen_components.add_component_to_topology(topology_root, component)

    print(topology_root)
    # return the dictionary with the topology.
    return topology_root

