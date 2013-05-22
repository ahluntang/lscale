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

    controller = "h002"
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

    host2_id = gen_components.add_host(topology_root)
    host2 = topology_root[host2_id]['id']

    rfvmA_scripts = SetupScripts()
    rfvmA_scripts.prerouting = "quagga_config.sh"
    rfvmA_scripts.routing = "routing.sh"
    rfvmA_scripts.postrouting = "run_rfclient.sh"
    rfvmA_scripts.add_parameter("prerouting", "daemons", quagga_daemons())
    rfvmA_scripts.add_parameter("prerouting", "debian", quagga_debian())
    rfvmA_scripts.add_parameter("prerouting", "ospf", quagga_ospf("rfvmA"))
    rfvmA_scripts.add_parameter("prerouting", "zebra", quagga_zebra("rfvmA"))

    rfvmB_scripts = SetupScripts()
    rfvmB_scripts.prerouting = "quagga_config.sh"
    rfvmB_scripts.routing = "routing.sh"
    rfvmB_scripts.postrouting = "run_rfclient.sh"
    rfvmB_scripts.add_parameter("prerouting", "daemons", quagga_daemons())
    rfvmB_scripts.add_parameter("prerouting", "debian", quagga_debian())
    rfvmB_scripts.add_parameter("prerouting", "ospf", quagga_ospf("rfvmB"))
    rfvmB_scripts.add_parameter("prerouting", "zebra", quagga_zebra("rfvmB"))

    rfvmC_scripts = SetupScripts()
    rfvmC_scripts.prerouting = "quagga_config.sh"
    rfvmC_scripts.routing = "routing.sh"
    rfvmC_scripts.postrouting = "run_rfclient.sh"
    rfvmC_scripts.add_parameter("prerouting", "daemons", quagga_daemons())
    rfvmC_scripts.add_parameter("prerouting", "debian", quagga_debian())
    rfvmC_scripts.add_parameter("prerouting", "ospf", quagga_ospf("rfvmC"))
    rfvmC_scripts.add_parameter("prerouting", "zebra", quagga_zebra("rfvmC"))

    rfvmD_scripts = SetupScripts()
    rfvmD_scripts.prerouting = "quagga_config.sh"
    rfvmD_scripts.routing = "routing.sh"
    rfvmD_scripts.postrouting = "run_rfclient.sh"
    rfvmD_scripts.add_parameter("prerouting", "daemons", quagga_daemons())
    rfvmD_scripts.add_parameter("prerouting", "debian", quagga_debian())
    rfvmD_scripts.add_parameter("prerouting", "ospf", quagga_ospf("rfvmD"))
    rfvmD_scripts.add_parameter("prerouting", "zebra", quagga_zebra("rfvmD"))


    routeflow1_component = gen_components.create_container(host1, "rfvm", ContainerType.LXC, "rfvm", BackingStore.LVM,
                                                           rfvmA_scripts, "root", "root")
    routeflow1_id = resources.get_last_id("rfvm")
    components[routeflow1_component.component_id] = routeflow1_component

    routeflow2_component = gen_components.create_container(host1, "rfvm", ContainerType.LXC, "rfvm", BackingStore.LVM,
                                                           rfvmB_scripts, "root", "root")
    routeflow2_id = resources.get_last_id("rfvm")
    components[routeflow2_component.component_id] = routeflow2_component

    routeflow3_component = gen_components.create_container(host1, "rfvm", ContainerType.LXC, "rfvm", BackingStore.LVM,
                                                           rfvmC_scripts, "root", "root")
    routeflow3_id = resources.get_last_id("rfvm")
    components[routeflow3_component.component_id] = routeflow3_component

    routeflow4_component = gen_components.create_container(host1, "rfvm", ContainerType.LXC, "rfvm", BackingStore.LVM,
                                                           rfvmD_scripts, "root", "root")
    routeflow4_id = resources.get_last_id("rfvm")
    components[routeflow4_component.component_id] = routeflow4_component

    switch1dp = "0000000000000005"
    switch2dp = "0000000000000006"
    switch3dp = "0000000000000007"
    switch4dp = "0000000000000008"

    bridge1_component = gen_components.create_bridge(host2, BridgeType.OPENVSWITCH, controller,
                                                     controller_port, switch1dp)
    components[bridge1_component.component_id] = bridge1_component
    br1_id = resources.get_last_id("b")

    bridge2_component = gen_components.create_bridge(host2, BridgeType.OPENVSWITCH, controller,
                                                     controller_port, switch2dp)
    components[bridge2_component.component_id] = bridge2_component
    br2_id = resources.get_last_id("b")

    bridge3_component = gen_components.create_bridge(host2, BridgeType.OPENVSWITCH, controller,
                                                     controller_port, switch3dp)
    components[bridge3_component.component_id] = bridge3_component
    br3_id = resources.get_last_id("b")

    bridge4_component = gen_components.create_bridge(host2, BridgeType.OPENVSWITCH, controller,
                                                     controller_port, switch4dp)
    components[bridge4_component.component_id] = bridge4_component
    br4_id = resources.get_last_id("b")

    clientscripts = SetupScripts()
    clientscripts.routing = "routing.sh"

    client1_component = gen_components.create_container(host2, "rfc", ContainerType.UNSHARED,
                                                        scripts=clientscripts)
    components[client1_component.component_id] = client1_component
    client1_id = resources.get_last_id("rfc")

    client2_component = gen_components.create_container(host2, "rfc", ContainerType.UNSHARED,
                                                        scripts=clientscripts)
    components[client2_component.component_id] = client2_component
    client2_id = resources.get_last_id("rfc")

    client3_component = gen_components.create_container(host2, "rfc", ContainerType.UNSHARED,
                                                        scripts=clientscripts)
    components[client3_component.component_id] = client3_component
    client3_id = resources.get_last_id("rfc")

    client4_component = gen_components.create_container(host2, "rfc", ContainerType.UNSHARED,
                                                        scripts=clientscripts)
    components[client4_component.component_id] = client4_component
    client4_id = resources.get_last_id("rfc")

    # adding hosts to bridges
    gen_components.connect_container_bridge(client1_component.topology['containers'][client1_id],
                                            bridge1_component.topology['bridges'][br1_id],
                                            container_ip="172.31.1.100/24")
    gen_components.connect_container_bridge(client2_component.topology['containers'][client2_id],
                                            bridge2_component.topology['bridges'][br2_id],
                                            container_ip="172.31.2.100/24")
    gen_components.connect_container_bridge(client3_component.topology['containers'][client3_id],
                                            bridge3_component.topology['bridges'][br3_id],
                                            container_ip="172.31.3.100/24")
    gen_components.connect_container_bridge(client4_component.topology['containers'][client4_id],
                                            bridge4_component.topology['bridges'][br4_id],
                                            container_ip="172.31.4.100/24")

    # connecting bridges
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

    dataplane_component = gen_components.create_bridge(host1, BridgeType.OPENVSWITCH,
                                                       controller, controller_port, "7266767372667673")
    dp_id = resources.get_last_id("b")
    components[dataplane_component.component_id] = dataplane_component
    # changing id for dataplane bridge.
    dataplane_component.topology['bridges'][dp_id].bridge_id = "dp0"
    dataplane_component.topology['bridges'][dp_id].address = mongodb_address

    gen_components.connect_container_bridge(routeflow1_component.topology['containers'][routeflow1_id],
                                            dataplane_component.topology['bridges'][dp_id])
    gen_components.connect_container_bridge(routeflow1_component.topology['containers'][routeflow1_id],
                                            dataplane_component.topology['bridges'][dp_id])
    gen_components.connect_container_bridge(routeflow1_component.topology['containers'][routeflow1_id],
                                            dataplane_component.topology['bridges'][dp_id])
    gen_components.connect_container_bridge(routeflow1_component.topology['containers'][routeflow1_id],
                                            dataplane_component.topology['bridges'][dp_id])

    gen_components.connect_container_bridge(routeflow2_component.topology['containers'][routeflow2_id],
                                            dataplane_component.topology['bridges'][dp_id])
    gen_components.connect_container_bridge(routeflow2_component.topology['containers'][routeflow2_id],
                                            dataplane_component.topology['bridges'][dp_id])
    gen_components.connect_container_bridge(routeflow2_component.topology['containers'][routeflow2_id],
                                            dataplane_component.topology['bridges'][dp_id])

    gen_components.connect_container_bridge(routeflow3_component.topology['containers'][routeflow3_id],
                                            dataplane_component.topology['bridges'][dp_id])
    gen_components.connect_container_bridge(routeflow3_component.topology['containers'][routeflow3_id],
                                            dataplane_component.topology['bridges'][dp_id])
    gen_components.connect_container_bridge(routeflow3_component.topology['containers'][routeflow3_id],
                                            dataplane_component.topology['bridges'][dp_id])

    gen_components.connect_container_bridge(routeflow4_component.topology['containers'][routeflow4_id],
                                            dataplane_component.topology['bridges'][dp_id])
    gen_components.connect_container_bridge(routeflow4_component.topology['containers'][routeflow4_id],
                                            dataplane_component.topology['bridges'][dp_id])
    gen_components.connect_container_bridge(routeflow4_component.topology['containers'][routeflow4_id],
                                            dataplane_component.topology['bridges'][dp_id])
    gen_components.connect_container_bridge(routeflow4_component.topology['containers'][routeflow4_id],
                                            dataplane_component.topology['bridges'][dp_id])



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
ospfd=yes
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
    if rfvm == "rfvmA":
        return """
password routeflow
enable password routeflow
!
router ospf
    network 172.16.0.0/12 area 0
    network 10.0.0.0/8 area 0
    network 20.0.0.0/8 area 0
    network 30.0.0.0/8 area 0
    network 40.0.0.0/8 area 0
    network 50.0.0.0/8 area 0
!
log file /var/log/quagga/ospfd.log
!
interface eth0
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
interface eth1
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
interface eth2
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
interface eth3
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
interface eth4
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
"""
    if rfvm == "rfvmB":
        return """
password routeflow
enable password routeflow
!
router ospf
    network 172.16.0.0/12 area 0
    network 10.0.0.0/8 area 0
    network 20.0.0.0/8 area 0
    network 30.0.0.0/8 area 0
    network 40.0.0.0/8 area 0
    network 50.0.0.0/8 area 0
!
log file /var/log/quagga/ospfd.log
!
interface eth0
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
interface eth1
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
interface eth2
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
interface eth3
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
interface eth4
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
"""

    if rfvm == "rfvmC":
        return """
password routeflow
enable password routeflow
!
router ospf
    network 172.16.0.0/12 area 0
    network 10.0.0.0/8 area 0
    network 20.0.0.0/8 area 0
    network 30.0.0.0/8 area 0
    network 40.0.0.0/8 area 0
    network 50.0.0.0/8 area 0
    network 60.0.0.0/8 area 0
    network 70.0.0.0/8 area 0
    network 80.0.0.0/8 area 0
    network 90.0.0.0/8 area 0
    network 100.0.0.0/8 area 0
!
log file /var/log/quagga/ospfd.log
!
interface eth0
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
interface eth1
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
interface eth2
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
interface eth3
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
interface eth4
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
"""

    if rfvm == "rfvmD":
        return """
password routeflow
enable password routeflow
!
router ospf
    network 172.16.0.0/12 area 0
    network 10.0.0.0/8 area 0
    network 20.0.0.0/8 area 0
    network 30.0.0.0/8 area 0
    network 40.0.0.0/8 area 0
    network 50.0.0.0/8 area 0
!
log file /var/log/quagga/ospfd.log
!
interface eth0
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
interface eth1
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
interface eth2
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
interface eth3
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
interface eth4
    ip ospf hello-interval 1
    ip ospf dead-interval 4
!
"""


def quagga_zebra(rfvm):
    if rfvm == "rfvmA":
        return """
password routeflow
enable password routeflow
!
log file /var/log/quagga/zebra.log
password 123
enable password 123
!
interface eth1
    ip address 172.31.1.1/24
!
interface eth2
    ip address 10.0.0.1/24
!
interface eth3
    ip address 30.0.0.1/24
!
interface eth4
    ip address 50.0.0.1/24
!
"""
    if rfvm == "rfvmB":
        return """
password routeflow
enable password routeflow
!
log file /var/log/quagga/zebra.log
password 123
enable password 123
!
interface eth1
        ip address 172.31.2.1/24
!
interface eth2
        ip address 10.0.0.2/24
!
interface eth3
        ip address 40.0.0.2/24
!
"""

    if rfvm == "rfvmC":
        return """
password routeflow
enable password routeflow
!
log file /var/log/quagga/zebra.log
password 123
enable password 123
!
interface eth1
        ip address 172.31.3.1/24
!
interface eth2
        ip address 20.0.0.3/24
!
interface eth3
        ip address 30.0.0.3/24
!
"""

    if rfvm == "rfvmD":
        return """
password routeflow
enable password routeflow
!
log file /var/log/quagga/zebra.log
password 123
enable password 123
!
interface eth1
        ip address 172.31.4.1/24
!
interface eth2
        ip address 40.0.0.4/24
!
interface eth3
        ip address 20.0.0.4/24
!
interface eth4
        ip address 50.0.0.4/24
!
"""
