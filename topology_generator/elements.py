#!/usr/bin/env python
import itertools

import netaddr

class Container(object):
    """ Represents a container or host.
    """

    def __init__(self, container_id, is_host = False):
        self.container_id       = container_id
        self.is_host            = is_host
        self.interface_number   = 0
        self.interfaces         = []
        self.bridges            = []

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

    def __init__(self, bridge_id, address = "0.0.0.0"):
        self.bridge_id          = bridge_id
        self.container_id       = None
        self.address            = address
        self.interface_number   = 0
        self.interfaces         = []

    def add_interface(self, interface):
        self.interfaces.append(interface)

    
    def get_next_interface(self):
        self.interface_number += 1
        return self.interface_number

class NetworkInterface(object):
    """ Represents an interface.
    """

    def __init__(self, interface_id, link_id, address = None):
        self.interface_id   = interface_id
        self.link_id        = link_id
        self.address        = address

    def set_container(self, container_id):
        self.container_id = container_id


class NetworkComponent(object):
    """Represents a part of the network.

    """
    new_id = itertools.count().next

    def __init__(self):
        self.component_id           = NetworkComponent.new_id()
        self.host_id                = None
        self.type                   = None
        #self.free_link_interfaces   = []
        self.connection_points    = []

        self.topology   = {}

        self.topology['containers'] = {}
        self.topology['bridges']    = {}


class IPComponent( object ) :
    """ Holds the next free address to use.

    Has methods to calculate the prefix based on how many hosts you need.
    Has methods to create addressing scheme for certain topology components.
    """

    def __init__(self, address = "172.16.0.0") :
        self.address = netaddr.IPAddress( address )
        self.address -= 1

    def addressing_for_ring_component(self, hosts_per_ring = 5, rings = 5) :
        """ Creates addressing scheme for a ring component.

        :param hosts_per_ring: the amount of hosts in a ring
        :param rings: the amount of rings in the ring component.
        """

        #links from ring to bridge: 2*rings
        #links between hosts on rings: (hosts_per_ring-1)*rings

        addressing_scheme = { }

        # get subnet for bridge: 2*rings network addresses needed
        bridge_links = 2 * rings
        bridge_prefix = self.calculate_prefix( bridge_links )
        network = netaddr.IPNetwork( self.address )
        network.prefixlen = bridge_prefix
        while network.network <= self.address :
            network = network.next( )

        addressing_scheme['bridge_prefix'] = bridge_prefix
        addressing_scheme['bridge_links'] = []

        # Available ip's for bridges
        for ip in network :
            addressing_scheme['bridge_links'].append( ip )

        # set first address of next network as new networkaddress in instance
        network = network.next( )
        self.address = network[0]

        # links between hosts on rings:
        host_links = (hosts_per_ring - 1) * rings

        host_prefix = 30 # prefix between hosts is always 30

        addressing_scheme['host_prefix'] = host_prefix
        addressing_scheme['host_links'] = { }

        for host in range( 1, host_links + 1 ) :
            network = netaddr.IPNetwork( self.address )
            network.prefixlen = host_prefix

            addressing_scheme['host_links'][host] = []
            for ip in network :
                addressing_scheme['host_links'][host].append( ip )

            # set first address of next network as new networkaddress in instance
            network = network.next( )
            self.address = network[0]

        return addressing_scheme

    def calculate_prefix(self, hosts) :
        """ Calculates prefix based on how many hosts/ip addresses are needed.

        :param hosts: amount of hosts that are needed in the network
        :return: prefix/networkbits as decimal value
        """
        bits = 32
        host_bits = 0
        h = 1
        while h < hosts :
            h = h << 1 # multiply with 2
            host_bits += 1
        networkbits = bits - host_bits
        return networkbits
