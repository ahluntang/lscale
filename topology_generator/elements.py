#!/usr/bin/env python
import itertools

import os, traceback, time, logging

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
