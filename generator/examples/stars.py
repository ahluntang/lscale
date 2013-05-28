from generator.topology.elements import NetworkComponent, IPComponent, UsedResources, SetupScripts
from generator.topology import gen_components
from generator.topology import quagga
from utilities import ContainerType, BridgeType, BackingStore


def create(last_host_id, last_container_id, last_link_id, starting_address):
    # create an IPComponent instance with the starting address
    addressing = IPComponent(starting_address)
    hosts = 15

     # set the starting number from where the topology module can generate new IDs
    # also add the IPComponent instance
    resources = UsedResources(last_host_id, last_container_id, last_link_id, addressing)

    # save the configuration in the generator.
    gen_components.set_resources(resources)

    # topology and components are saved in a dictionary
    topology_root = {}
    components = {}

    # Creating the cityflow specific topology.
    # 39 times: 10 per host, 9 on last host.

    # Adding a host to topology.
    host_id = gen_components.add_host(topology_root)
    host = topology_root[host_id]['id']

    # Retrieve the  IPComponent from the generator.
    addressing = gen_components.get_resources().addressing

    # Use the IPComponent to get an addressing scheme for a star component
    addressing_scheme = addressing.addressing_for_star_component(hosts)

    # Create a star component for topology
    star1_component = gen_components.create_star(host, hosts, addressing_scheme, ContainerType.LXCCLONE, "quagga")
    components[star1_component.component_id] = star1_component

    # Use the IPComponent to get an addressing scheme for a star component
    addressing_scheme = addressing.addressing_for_star_component(hosts)

    # Create a star component for topology
    star2_component = gen_components.create_star(host, hosts, addressing_scheme, ContainerType.LXCCLONE, "quagga")
    components[star2_component.component_id] = star2_component

    # connecting star components
    star1_center = star1_component.connection_points.pop()
    star2_center = star2_component.connection_points.pop()
    subnet = addressing.addressing_for_container_connection()
    gen_components.connect_containers(star1_center, star2_center, star1_component, star2_component, subnet)

    # # connecting third star component
    # addressing_scheme = addressing.addressing_for_star_component(hosts)
    # star3_component = gen_components.create_star(host, hosts, addressing_scheme, ContainerType.LXCCLONE, "quagga")
    # components[star3_component.component_id] = star3_component
    #
    # # connecting star components
    # star3_center = star3_component.connection_points.pop()
    # subnet = addressing.addressing_for_container_connection()
    # gen_components.connect_containers(star2_center, star3_center, star2_component, star3_component, subnet)

    # combine networklist for ospf
    networks = []
    for component_id, component in components.items():
        if component.type == "star":
            networks.extend(component.networks)

    # removing duplicates
    networks = list(set(networks))
    # make sure every component knows each network
    for component_id, component in components.items():
        if component.type == "star":
            component.networks = networks
    #
    # modify containers for quagga.
    #
    for component_id, component in components.items():
        if component.type == "star":
            componentsetup_quagga(component)

    # After every component has been created
    # merge components into one dictionary,
    for component_id, component in components.items():
        gen_components.add_component_to_topology(topology_root, component)

    # return the dictionary with the topology.
    return topology_root

def componentsetup_quagga(component):
    for container_id, container in component.topology['containers'].items():
        containersetup_quagga(component, container)

def containersetup_quagga(component, container):
    daemons = """
zebra=yes
bgpd=no
ospfd=yes
ospf6d=no
ripd=no
ripngd=no
isisd=no
"""  #lxc

    debian = """
vtysh_enable=yes
zebra_options=" --daemon -A 127.0.0.1"
bgpd_options="  --daemon -A 127.0.0.1"
ospfd_options=" --daemon -A 127.0.0.1"
ospf6d_options="--daemon -A ::1"
ripd_options="  --daemon -A 127.0.0.1"
ripngd_options="--daemon -A ::1"
isisd_options=" --daemon -A 127.0.0.1"
"""   #lxc
    # #adapting scripts
    networks = component.networks
    ospf_conf = quagga.ospf(networks, container)
    zebra_conf = quagga.zebra(container)
    container_scripts = SetupScripts()
    container_scripts.prerouting = "quagga_config.sh"  #lxc
    #container_scripts.prerouting = "ospf_config_unshared.sh"  #unshare
    container_scripts.add_parameter("prerouting", "ospf", ospf_conf)
    container_scripts.add_parameter("prerouting", "zebra", zebra_conf)
    container_scripts.add_parameter("prerouting", "daemons", daemons)  #lxc
    container_scripts.add_parameter("prerouting", "debian", debian)  #lxc
    #container_scripts.routing = "zebra_addressing.sh"
    container_scripts.postrouting = "quagga_lxc.sh"

    #setting new scripts in container
    container.scripts = container_scripts
