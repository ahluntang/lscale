# -*- coding: utf-8 -*-

from generator.topology.elements import NetworkComponent, IPComponent, UsedResources, SetupScripts
from generator.topology import gen_components
from utilities import ContainerType, BridgeType, BackingStore


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

    mongodb_address = "192.169.1.1"
    mongodb_port = "27017"

    controller = "localhost"
    controller_port = "6633"

    # Adding two hosts to topology.
    host1_id = gen_components.add_host(topology_root)
    host1 = topology_root[host1_id]['id']

    host1_scripts = SetupScripts()
    host1_scripts.prerouting = "mongodb.sh"
    host1_scripts.add_parameter("prerouting", "mongodb_address", mongodb_address)
    host1_scripts.postrouting = "start_controller.sh"
    host1_scripts.add_parameter("postrouting", "mongodb_address", mongodb_address)
    host1_scripts.add_parameter("postrouting", "mongodb_port", mongodb_port)
    host1_scripts.add_parameter("postrouting", "controller_port", controller_port)
    host1_scripts.cleanup = "mongo_cleanup.sh"

    host1.scripts = host1_scripts

    rfvm1_scripts = SetupScripts()
    rfvm1_scripts.prerouting = "quagga_config.sh"
    rfvm1_scripts.routing = "routing.sh"
    rfvm1_scripts.postrouting = "run_rfclient.sh"
    rfvm1_scripts.add_parameter("prerouting", "daemons", quagga_daemons())
    rfvm1_scripts.add_parameter("prerouting", "debian", quagga_debian())
    rfvm1_scripts.add_parameter("prerouting", "ospf", quagga_ospf("rfvm1"))
    rfvm1_scripts.add_parameter("prerouting", "zebra", quagga_zebra("rfvm1"))

    routeflow1_component = gen_components.create_container(host1, "rfvm", ContainerType.LXC, "rfvm",
                                                           BackingStore.LVM, rfvm1_scripts, "root", "root")
    components[routeflow1_component.component_id] = routeflow1_component
    routeflow1_id = resources.get_last_id("rfvm")

    switch1dp = "0000000000000099"

    bridge1_component = gen_components.create_bridge(host1, BridgeType.OPENVSWITCH, controller,
                                                     controller_port, switch1dp)
    components[bridge1_component.component_id] = bridge1_component
    br1_id = resources.get_last_id("b")

    clientscripts = SetupScripts()
    clientscripts.routing = "routing.sh"

    client1_component = gen_components.create_container(host1, "rfc", ContainerType.UNSHARED,
                                                        scripts=clientscripts)
    components[client1_component.component_id] = client1_component
    client1_id = resources.get_last_id("rfc")

    client2_component = gen_components.create_container(host1, "rfc", ContainerType.UNSHARED,
                                                        scripts=clientscripts)
    components[client2_component.component_id] = client2_component
    client2_id = resources.get_last_id("rfc")

    # adding hosts to bridges
    gen_components.connect_container_bridge(client1_component.topology['containers'][client1_id],
                                            bridge1_component.topology['bridges'][br1_id],
                                            container_ip="172.31.1.2/24")
    gen_components.connect_container_bridge(client2_component.topology['containers'][client2_id],
                                            bridge1_component.topology['bridges'][br1_id],
                                            container_ip="172.31.2.2/24")

    dataplane_component = gen_components.create_bridge(host1, BridgeType.OPENVSWITCH,
                                                       controller, controller_port, "7266767372667673")
    dp_id = resources.get_last_id("b")
    components[dataplane_component.component_id] = dataplane_component

    # changing id for dataplane bridge.
    dataplane_component.topology['bridges'][dp_id].bridge_id = "dp0"
    dataplane_component.topology['bridges'][dp_id].address = mongodb_address

    gen_components.connect_container_bridge(routeflow1_component.topology['containers'][routeflow1_id],
                                            dataplane_component.topology['bridges'][dp_id], routeflow=True)
    gen_components.connect_container_bridge(routeflow1_component.topology['containers'][routeflow1_id],
                                            dataplane_component.topology['bridges'][dp_id], routeflow=True)

    # end creating the topology
    # After every component has been created
    # merge components into one dictionary,
    for component_id, component in components.items():
        gen_components.add_component_to_topology(topology_root, component)

    # return the dictionary with the topology.
    return topology_root


def quagga_daemons():

    return """
zebra=yes
bgpd=no
ospfd=no
ospf6d=no
ripd=no
ripngd=no
isisd=no
"""

def quagga_debian():
    return """
vtysh_enable=yes
zebra_options=" --daemon -A 127.0.0.1"
bgpd_options="  --daemon -A 127.0.0.1"
ospfd_options=" --daemon -A 127.0.0.1"
ospf6d_options="--daemon -A ::1"
ripd_options="  --daemon -A 127.0.0.1"
ripngd_options="--daemon -A ::1"
isisd_options=" --daemon -A 127.0.0.1"
"""

def quagga_ospf(rfvm):
    if rfvm == "rfvm1":
        return """

"""


def quagga_zebra(rfvm):
    if rfvm == "rfvm1":
        return """
password routeflow
enable password routeflow
!
log file /var/log/quagga/zebra.log
password 123
enable password 123
!
interface eth0
    ip address 192.169.1.101/24
!
interface eth1
    ip address 172.31.1.1/24
!
interface eth2
    ip address 172.31.2.1/24
!
"""
