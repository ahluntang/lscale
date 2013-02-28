#!/usr/bin/env python

import lxml.etree as etree
import time

from lxc_elements import Bridge, Container, VirtualLink

def parse(filename, parsed_topology):
    config_tree = etree.parse(filename)
    xml_root = config_tree.getroot()

    for host in xml_root.findall( "hosts/host" ) :
        h = parse_host( host )
        parsed_topology[h['host_id']] = h

def parse_host(host):
    containers  = {}    # Container objects
    bridges     = {}    # Bridge objects
    links       = {}    # VirtualLink objects
    mappings    = {}    # Mapping interfaces to containers
    mappings_ip = {}    # Mapping interfaces to ip

    host_id = host.find("id").text
    c = Container(host_id, True)
    containers[host_id] = c

    for container in host.findall('containers/container'):
        c = parse_container(container)
        containers[c.container_id] = c


    for link in host.findall('links/link'):
        l = parse_link(link, mappings, mappings_ip, containers)
        #link_id = "%s-%s" % (l.veth0, l.veth1)
        links[ l.veth0 ] = l
        links[ l.veth1 ] = l

    for bridge in host.findall('bridges/bridge'):
        b = parse_bridge(bridge)
        bridges[b.bridge_id] = b

    configured_host = {
        "host_id"       : host_id,
        "containers"    : containers,
        "bridges"       : bridges,
        "links"         : links,
        "mappings"      : mappings,
        "mappings_ip"   : mappings_ip
    }

    move_vinterfaces(configured_host)
    return configured_host


def move_vinterfaces(configured_host) :
    for vinterface, container_id in configured_host["mappings"].items( ) :
        # moving virtual interface to containers.
        c = configured_host['containers'][container_id]
        l = configured_host['links'][vinterface]
        l.setns( vinterface, c )

    time.sleep( 1 )

    for vinterface, ip in configured_host["mappings_ip"].items( ) :
        # setting IP addresses
        container_id = configured_host["mappings"][vinterface]
        c = configured_host['containers'][container_id]
        c.config_link( vinterface, ip )

def parse_container(container):
    container_id = container.find("id").text
    c = Container(container_id)
    return c


def parse_bridge(bridge):
    bridge_id = bridge.find("id").text
    address = bridge.find("address").text
    # creating the bridge
    b = Bridge(bridge_id,address)

    for interface in bridge.findall('interfaces/interface'):
        b.addif(interface.text)

    return b


def parse_link(link, mappings, mappings_ip, containers):
    veth0 = None
    veth1 = None
    veth0_ip = None
    veth1_ip = None
    addresses = {}
    count = 1
    for vinterface in link.findall('vinterface'):
        vinterface_id = vinterface.find("id").text
        container_id = vinterface.find("container").text
        address = vinterface.find("address")

        mappings[vinterface_id] = container_id

        if(count == 1):
            veth0 = vinterface_id
            if not address is None:
                veth0_ip = address.text
        else:
            veth1 = vinterface_id
            if not address is None:
                veth1_ip = address.text
        count += 1

    # creating the link
    l = VirtualLink(veth0, veth1)

    # moving virtual interface to containers.
    #c1 = containers[ mappings[veth0] ]

    #c2 = containers[ mappings[veth1] ]

    # setting ip addresses
    if not veth0_ip is None:
        mappings_ip[veth0] = veth0_ip
        #c1.config_link(veth0, veth0_ip)

    if not veth1_ip is None:
        mappings_ip[veth1] = veth1_ip
        #c2.config_link(veth1, veth1_ip)

    return l
