#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.etree as etree
import time

from lxc_elements import Bridge, Container, VirtualLink, VirtualInterface, Route

def parse(filename, template_environment, parsed_topology, host_id):
    config_tree = etree.parse(filename)
    xml_root = config_tree.getroot()

    for host in xml_root.findall( "hosts/host" ) :
        h = parse_host( template_environment, host, host_id )
        if h is not None:
            parsed_topology[h['host_id']] = h

def parse_host(template_environment, host, host_id):
    containers  = {}    # Container objects
    bridges     = {}    # Bridge objects
    links       = {}    # VirtualLink objects
    mappings    = {}    # Mapping interfaces to containers
    mappings_ip = {}    # Mapping interfaces to ip

    current_host_id = host.find("id").text

    # only make containers for current host
    if current_host_id == host_id :
        c = Container(current_host_id, True)
        containers[current_host_id] = c

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
            "host_id"       : current_host_id,
            "containers"    : containers,
            "bridges"       : bridges,
            "links"         : links,
            "mappings"      : mappings,
            "mappings_ip"   : mappings_ip
        }

        move_vinterfaces(configured_host)

        for container_id, container in containers.items():
            #run pre routing script
            container.run_pre_routing(template_environment)

        for container_id, container in containers.items() :
            #run routing script
            container.run_routing(template_environment)

        for container_id, container in containers.items() :
            #run post routing script
            container.run_post_routing(template_environment)

        return configured_host
    else:
        return None


def move_vinterfaces(configured_host) :
    for vinterface, container_id in configured_host["mappings"].items( ) :
        # moving virtual interface to containers.
        c = configured_host['containers'][container_id]
        l = configured_host['links'][vinterface]
        l.setns( vinterface, c )

    time.sleep( 1 )

    # setting IP addresses
    #for vinterface, ip in configured_host["mappings_ip"].items( ) :
        # setting IP addresses
        #container_id = configured_host["mappings"][vinterface]
        #c = configured_host['containers'][container_id]
        #c.config_link( vinterface, ip )

def parse_container(container):
    container_id = container.find("id").text
    c = Container(container_id)

    prerouting = container.find("prerouting")
    if prerouting is not None:
        c.preroutingscript = prerouting.text

    routing = container.find("routing")
    if prerouting is not None :
        c.routingscript = routing.text

    postrouting = container.find("postrouting")
    if prerouting is not None :
        c.postroutingscript = postrouting.text

    gateway = container.find("gateway")
    if gateway is not None :
        c.routing['gateway'] = gateway.text

    return c


def parse_bridge(bridge):
    bridge_id = bridge.find("id").text
    address = bridge.find("address")

    if address is None :
        ip = "0.0.0.0"
    else:
        ip = address.text

    # creating the bridge
    b = Bridge(bridge_id,ip)

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
    routes0 = []
    routes1 = []
    for vinterface in link.findall('vinterface'):
        vinterface_id = vinterface.find("id").text
        container_id = vinterface.find("container").text
        address = vinterface.find("address")

        mappings[vinterface_id] = container_id

        summaries = vinterface.find("summarizes")


        if(count == 1):
            veth0 = VirtualInterface(vinterface_id)
            if not address is None:
                veth0_ip = address.text
                veth0.address = veth0_ip
                #veth0.routes.extend(routes)
                for summary in summaries.findall('summary') :
                    route = Route(summary.text, vinterface_id)
                    routes0.append(route)

        else:
            veth1 = VirtualInterface(vinterface_id)
            if not address is None:
                veth1_ip = address.text
                veth1.address = address.text
                #veth1.routes.extend(routes)
                for summary in summaries.findall('summary') :
                    route = Route(summary.text, vinterface_id)
                    routes1.append(route)

        count += 1

    # creating the link
    l = VirtualLink(veth0, veth1)

    # moving virtual interface to containers.
    c1 = containers[ mappings[veth0.veth] ]

    c2 = containers[ mappings[veth1.veth] ]

    # setting ip addresses
    if not veth0_ip is None:
        mappings_ip[veth0.veth] = veth0_ip
        c1.config_link(veth0)
        if(len(routes0) > 0):
            c1.routing['routes'].extend(routes0)


    if not veth1_ip is None:
        mappings_ip[veth1] = veth1_ip
        c2.config_link(veth1)
        if (len(routes1) > 0) :
            c2.routing['routes'].extend(routes1)

    return l
