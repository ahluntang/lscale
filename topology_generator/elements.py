#!/usr/bin/env python

import os, traceback, time, logging

class Container(object):
    """ Represents a container or host.
    """

    def __init__(self, container_id):
        self.container_id   = container_id
        self.interfaces     = []
        self.bridges     = []

    def add_interface(self, interface):
        self.interfaces.append(interface)

    def add_bridge(self, bridge):
        self.bridges.append(bridge)

class Bridge(object):
    """ Represents a bridge or switch.
    """

    def __init__(self, bridge_id, address = "0.0.0.0"):
        self.bridge_id  = bridge_id
        self.address    = address
        self.interfaces = []

    def add_interface(self, interface):
        self.interfaces.append(interface)

class NetworkInterface(object):
    """ Represents an interface.
    """

    def __init__(self, interface_id, link_id, address = None):
        self.interface_id   = interface_id
        self.link_id        = link_id
        self.address        = address