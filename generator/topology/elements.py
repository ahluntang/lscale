#!/usr/bin/env python
# -*- coding: utf-8 -*-


import netaddr

from utilities import ContainerType, BridgeType, BackingStore


class Container(object):
    """ Represents a container or host.
    """

    def __init__(self, container_id, container_type=ContainerType.UNSHARED, template="base", username="root", password="root"):
        self.container_id = container_id
        self.container_type = container_type
        self.template = template
        self.interface_number = 0
        self.interfaces = []
        self.bridges = []
        self.scripts = SetupScripts()
        self.username = username
        self.password = password
        self.gateway = None
        self.storage = BackingStore.LVM
        self.networks = []

    def add_interface(self, interface):
        self.interfaces.append(interface)
        interface.is_free = False

    def add_bridge(self, bridge):
        self.bridges.append(bridge)

    def get_next_interface(self):
        self.interface_number += 1
        return self.interface_number


class Bridge(object):
    """ Represents a bridge or switch.
    """

    def __init__(self, bridge_id, address="0.0.0.0", bridge_type=BridgeType.BRIDGE):
        self.bridge_id = bridge_id
        self.container_id = None
        self.address = address
        self.interface_number = 0
        self.interfaces = []
        self.bridge_type = bridge_type
        self.controller = None
        self.controller_port = None
        self.datapath = None

    def add_interface(self, interface):
        self.interfaces.append(interface)

    def get_next_interface(self):
        self.interface_number += 1
        return self.interface_number



class NetworkInterface(object):
    """ Represents an interface.
    """

    def __init__(self, interface_id, link_id, address=None):
        self.interface_id = interface_id
        self.link_id = link_id
        self.address = address
        self.mac = None
        self.routes = []
        self.gateway = None
        self.summarizes = None

    def set_container(self, container_id):
        self.container_id = container_id

    def add_route(self, route):
        self.routes.append(route)

    def __lt__(self, other):
        return self.interface_id < other.interface_id

        # and so on for other comparators, as above, plus:
    def __hash__(self):
        return hash(self.interface_id)


class SetupScripts(object):

    def __init__(self):
        self.prerouting = None
        self.routing = None
        self.postrouting = None
        self.cleanup = None
        self.parameters = {
            'prerouting': {},
            'routing': {},
            'postrouting': {},
            'cleanup': {}
        }

    def add_parameter(self, script, key, value):
        if script not in self.parameters:
            self.parameters[script] = {}
        self.parameters[script][key] = value

class NetworkComponent(object):
    """Represents a part of the network.

    """
    new_id = 1

    def __init__(self):
        NetworkComponent.new_id += 1
        self.component_id = NetworkComponent.new_id
        self.host_id = None
        self.type = None
        #self.free_link_interfaces   = []
        self.connection_points = []
        self.addresses = []
        self.networks = []

        self.topology = {}

        self.topology['containers'] = {}
        self.topology['bridges'] = {}


class UsedResources(object):
    """ Saves amount of used resources.
    Class to track how many items have been created
    """

    def __init__(self, last_host=0, last_container_id=0, last_link_id=0, addressing=None):
        self.last_resource = {
            "h": last_host,
            "b": 0,
            "c": last_container_id,
            "l": last_link_id
        }
        self.addressing = addressing

    def get_new_host_id(self):
        self.last_resource['h'] += 1
        return "h%03d" % self.last_resource['h']

    def get_last_host_id(self):
        return "h%03d" % self.last_resource['h']

    def get_new_bridge_id(self):
        self.last_resource['b']  += 1
        return "b%03d" % self.last_resource['b']

    def get_last_bridge_id(self):
        return "b%03d" % self.last_resource['b']

    def get_new_container_id(self):
        self.last_resource['c'] += 1
        return "c%03d" % self.last_resource['c']

    def get_last_container_id(self):
        return "c%03d" % self.last_resource['c']

    def get_new_link_id(self):
        self.last_resource['l']  += 1
        return "l%03d" % self.last_resource['l']

    def get_last_link_id(self):
        return "l%03d" % self.last_resource['l']

    def get_new_id(self, prefix):
        if prefix not in self.last_resource:
            self.last_resource[prefix] = 0
        self.last_resource[prefix] += 1
        return "%s%03d" % (prefix, self.last_resource[prefix])

    def get_last_id(self, prefix):
        return "%s%03d" % (prefix, self.last_resource[prefix])


class IPComponent(object):
    """ Holds the next free address to use.

    Has methods to calculate the prefix based on how many hosts you need.
    Has methods to create addressing scheme for certain topology components.
    """

    def __init__(self, address="172.16.0.0"):
        self.address = netaddr.IPAddress(address)
        self.address -= 1


    def addressing_for_bus_component(self, hosts=5):
        addressing_scheme = {}

        host_prefix = self.calculate_prefix(hosts)

        addressing_scheme['host_prefix'] = host_prefix
        addressing_scheme['host_links'] = []

        network = netaddr.IPNetwork(self.address)
        network.prefixlen = host_prefix
        while network.network <= self.address:
            network = network.next()
        addressing_scheme['host_links'].append(network)

        network = network.next()
        self.address = network[0]

        return addressing_scheme


    def addressing_for_star_component(self, hosts=5):
        addressing_scheme = {}

        host_prefix = 30

        addressing_scheme['host_prefix'] = host_prefix
        addressing_scheme['host_links'] = []

        network = netaddr.IPNetwork(self.address)
        network.prefixlen = host_prefix
        while network.network <= self.address:
            network = network.next()
        addressing_scheme['host_links'].append(network)
        for i in range(1, hosts):
            network = network.next()
            addressing_scheme['host_links'].append(network)

        network = network.next()
        self.address = network[0]

        return addressing_scheme

    def addressing_for_mesh_component(self, hosts=5):
        addressing_scheme = {}

        amount_of_ips = hosts * (hosts - 1)
        host_prefix = self.calculate_prefix(amount_of_ips)

        addressing_scheme['host_prefix'] = host_prefix
        addressing_scheme['host_links'] = []

        network = netaddr.IPNetwork(self.address)
        network.prefixlen = host_prefix
        while network.network <= self.address:
            network = network.next()
        addressing_scheme['host_links'].append(network)

        network = network.next()
        self.address = network[0]

        return addressing_scheme

    def addressing_for_container_connection(self):
        """


        :return:
        """
        addressing_scheme = {}

        host_prefix = 30

        addressing_scheme['host_prefix'] = host_prefix
        addressing_scheme['host_links'] = []

        network = netaddr.IPNetwork(self.address)
        network.prefixlen = host_prefix
        while network.network <= self.address:
            network = network.next()
        addressing_scheme['host_links'].append(network)
        for i in range(1, 2):
            network = network.next()
            addressing_scheme['host_links'].append(network)

        network = network.next()
        self.address = network[0]

        return addressing_scheme

    def addressing_for_line_component(self, hosts_per_line=5, lines=5):
        return self.addressing_for_ring_component(hosts_per_line, lines, False)

    def addressing_for_ring_component(self, hosts_per_ring=5, rings=5, close_ring=True):
        """ Creates addressing scheme for a ring component.

        :param hosts_per_ring: the amount of hosts in a ring
        :param rings: the amount of rings in the ring component.
        """

        #links from ring to bridge: 2*rings
        #links between hosts on rings: (hosts_per_ring-1)*rings

        addressing_scheme = {}
        network = netaddr.IPNetwork(self.address)
        if not close_ring:
            # get subnet for bridge: 2*rings network addresses needed
            bridge_links = 4 * rings
            bridge_prefix = self.calculate_prefix(bridge_links)
            network.prefixlen = bridge_prefix

            #if prefix has changed, make sure the next network is not overlapping the previous
            while network.network <= self.address:
                network = network.next()

            addressing_scheme['bridge_prefix'] = bridge_prefix
            #addressing_scheme['bridge_links'] = network
            addressing_scheme['bridge_links'] = []
            for ip in network.iter_hosts():
                addressing_scheme['bridge_links'].append(ip)

            # set first address of next network as new networkaddress in instance
            network = network.next()
            self.address = network[0]

        # links between hosts on rings:
        if close_ring:
            host_links = hosts_per_ring * rings
        else:
            host_links = (hosts_per_ring - 1) * rings

        host_prefix = 30 # prefix between hosts on ring is always 30

        addressing_scheme['host_prefix'] = host_prefix
        addressing_scheme['host_links'] = []

        for host in range(1, host_links + 1):
            network = netaddr.IPNetwork(self.address)
            network.prefixlen = host_prefix

            addressing_scheme['host_links'].append(network)

            # set first address of next network as new networkaddress in instance
            network = network.next()
            self.address = network[0]

        return addressing_scheme

    def calculate_prefix(self, hosts):
        """ Calculates prefix based on how many hosts/ip addresses are needed.

        :param hosts: amount of hosts that are needed in the network
        :return: prefix/networkbits as decimal value
        """
        bits = 32
        host_bits = 0
        h = 1
        while h < hosts:
            h <<= 1  # multiply with 2
            host_bits += 1
        networkbits = bits - host_bits
        return networkbits

