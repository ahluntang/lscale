from generator.topology.elements import NetworkComponent, IPComponent, UsedResources, SetupScripts
from generator.topology import gen_components
from generator.topology import quagga
from utilities import ContainerType, BridgeType, BackingStore


def create(last_host_id, last_container_id, last_link_id, starting_address):
    # create an IPComponent instance with the starting address
    addressing = IPComponent(starting_address)
    hosts = 3

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

    # Use the IPComponent to get an addressing scheme for a line component
    addressing_scheme = addressing.addressing_for_line_component(hosts, 1)

    # Create a ring component for topology
    ring_component = gen_components.create_line(host, hosts, addressing_scheme)
    components[ring_component.component_id] = ring_component

    print("ospf: {}".format(ring_component.addresses))

    for container in ring_component.topology['containers']:
        quagga_conf = quagga.ospf(container)

    # After every component has been created
    # merge components into one dictionary,
    for component_id, component in components.items():
        gen_components.add_component_to_topology(topology_root, component)

    # return the dictionary with the topology.
    return topology_root
