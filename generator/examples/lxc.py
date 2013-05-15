# -*- coding: utf-8 -*-

from generator.topology.elements import NetworkComponent, IPComponent, UsedResources, SetupScripts
from generator.topology import gen_components
from utilities import ContainerType, BridgeType


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

    # Adding two hosts to topology.
    host1_id = gen_components.add_host(topology_root)
    host1 = topology_root[host1_id]['id']

    host1_scripts = SetupScripts()
    host1_scripts.postrouting = "start_controller.sh"

    host1.scripts = host1_scripts

    host2_id = gen_components.add_host(topology_root)
    host2 = topology_root[host2_id]['id']

    controller = "h001"
    controller_port = "6633"

    rfvm_scripts = SetupScripts()
    rfvm_scripts.routing = "routing.sh"

    routeflow1_component = gen_components.create_container(host1, "rfvm", ContainerType.LXCLVM,
                                                           "base_no_backingstore", rfvm_scripts)
    components[routeflow1_component.component_id] = routeflow1_component

    routeflow2_component = gen_components.create_container(host1, "rfvm", ContainerType.LXCLVM,
                                                           "base_no_backingstore", rfvm_scripts)
    components[routeflow2_component.component_id] = routeflow2_component

    routeflow3_component = gen_components.create_container(host1, "rfvm", ContainerType.LXCLVM,
                                                           "base_no_backingstore", rfvm_scripts)
    components[routeflow3_component.component_id] = routeflow3_component

    routeflow4_component = gen_components.create_container(host1, "rfvm", ContainerType.LXCLVM,
                                                           "base_no_backingstore", rfvm_scripts)
    components[routeflow4_component.component_id] = routeflow4_component

    switch1dp = "0000000000000005"
    switch2dp = "0000000000000006"
    switch3dp = "0000000000000007"
    switch4dp = "0000000000000008"


    rfclient_scripts = SetupScripts()
    rfclient_scripts.postrouting = "run_rfclient.sh"

    bridge1_component = gen_components.create_bridge(host2, BridgeType.OPENVSWITCH, controller, controller_port, switch1dp)
    components[bridge1_component.component_id] = bridge1_component
    br1_id = resources.get_last_id("b")

    bridge2_component = gen_components.create_bridge(host2, BridgeType.OPENVSWITCH, controller, controller_port, switch2dp)
    components[bridge2_component.component_id] = bridge2_component
    br2_id = resources.get_last_id("b")

    bridge3_component = gen_components.create_bridge(host2, BridgeType.OPENVSWITCH, controller, controller_port, switch3dp)
    components[bridge3_component.component_id] = bridge3_component
    br3_id = resources.get_last_id("b")

    bridge4_component = gen_components.create_bridge(host2, BridgeType.OPENVSWITCH, controller, controller_port, switch4dp)
    components[bridge4_component.component_id] = bridge4_component
    br4_id = resources.get_last_id("b")

    client1_component = gen_components.create_container(host2, "rfc", ContainerType.UNSHARED, scripts=rfclient_scripts)
    components[client1_component.component_id] = client1_component
    client1_id = resources.get_last_id("rfc")

    client2_component = gen_components.create_container(host2, "rfc", ContainerType.UNSHARED, scripts=rfclient_scripts)
    components[client2_component.component_id] = client2_component
    client2_id = resources.get_last_id("rfc")

    client3_component = gen_components.create_container(host2, "rfc", ContainerType.UNSHARED, scripts=rfclient_scripts)
    components[client3_component.component_id] = client3_component
    client3_id = resources.get_last_id("rfc")

    client4_component = gen_components.create_container(host2, "rfc", ContainerType.UNSHARED, scripts=rfclient_scripts)
    components[client4_component.component_id] = client4_component
    client4_id = resources.get_last_id("rfc")

    gen_components.connect_container_bridge(client1_component.topology['containers'][client1_id],
                                            bridge1_component.topology['bridges'][br1_id])
    gen_components.connect_container_bridge(client2_component.topology['containers'][client2_id],
                                            bridge2_component.topology['bridges'][br2_id])
    gen_components.connect_container_bridge(client3_component.topology['containers'][client3_id],
                                            bridge3_component.topology['bridges'][br3_id])
    gen_components.connect_container_bridge(client4_component.topology['containers'][client4_id],
                                            bridge4_component.topology['bridges'][br4_id])

    gen_components.connect_bridges(bridge1_component.topology['bridges'][br1_id],
                                   bridge2_component.topology['bridges'][br2_id])
    gen_components.connect_bridges(bridge2_component.topology['bridges'][br2_id],
                                   bridge4_component.topology['bridges'][br4_id])
    gen_components.connect_bridges(bridge4_component.topology['bridges'][br4_id],
                                   bridge3_component.topology['bridges'][br3_id])
    gen_components.connect_bridges(bridge3_component.topology['bridges'][br3_id],
                                   bridge1_component.topology['bridges'][br1_id])
    gen_components.connect_bridges(bridge1_component.topology['bridges'][br1_id],
                                   bridge4_component.topology['bridges'][br4_id])
    # end creating the topology
    # After every component has been created
    # merge components into one dictionary,
    for component_id, component in components.items():
        gen_components.add_component_to_topology(topology_root, component)

    # return the dictionary with the topology.
    return topology_root

