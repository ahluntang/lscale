#!/usr/bin/env python

import os, traceback, time, logging

from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment, tostring
from collections import defaultdict

from elements import Container, Bridge, NetworkInterface


def write_topology_xml(topology, output):
    root_tree = Element('data')
    hosts_tree = SubElement(root_tree,'hosts')
    for host_id, host in topology.items():

        host_tree        = SubElement(hosts_tree, 'host')
        hid_element      = SubElement(host_tree, 'id')
        hid_element.text = host_id

        containers_tree  = SubElement(host_tree, 'containers')
        links_tree       = SubElement(host_tree, 'links')
        bridges_tree     = SubElement(host_tree, 'bridges')


        links    = defaultdict(list)
        bridges  = defaultdict(list)
        
        for (container_id, container) in host['containers'].items():

            container_tree   = SubElement(containers_tree, 'container')
            cid_element      = SubElement(container_tree, 'id')
            cid_element.text = container_id

            # get interfaces
            for interface in container.interfaces:
                link_id = interface.link_id
                interface.set_container(container.container_id)
                links[link_id].append(interface)
        
        link_trees = {}

        for link_id, interfaces in links.items():
            link_tree = None
            link_tree        = SubElement(links_tree, 'link')
            lid_element      = SubElement(link_tree, 'id')
            lid_element.text = link_id

            for interface in interfaces:
                if_element              = SubElement(link_tree, 'vinterface')
                ifid_element            = SubElement(if_element, 'id')
                ifid_element.text       = interface.interface_id
                container_element       = SubElement(if_element, 'container')
                container_element.text  = interface.container_id
                if(interface.address is not None):
                    address_element     = SubElement(if_element, 'address')
                    address_element.text= interface.address


    print tostring(root_tree)
    ElementTree(root_tree).write(output)
