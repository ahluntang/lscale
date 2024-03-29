#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import netaddr
import logging
import threading
import collections
import pexpect

import lxml.etree as ET
import emulator.elements
from utilities import ContainerType, BridgeType, is_lxc, BackingStore, systemconfig


def parse(filename, template_environment, parsed_topology, host_id, destroy):
    """

    :param filename:
    :param template_environment:
    :param parsed_topology:
    :param host_id:
    """
    config_tree = ET.parse(filename)
    xml_root = config_tree.getroot()

    for host in xml_root.findall("hosts/host"):
        h = parse_host(template_environment, host, host_id, destroy)
        if h is not None:
            parsed_topology[h['host_id']] = h

    logging.getLogger(__name__).info("Done parsing file for %s", host_id)


def parse_host(template_environment, host, host_id, destroy):
    containers = {}             # Container objects
    bridges = {}                # Bridge objects
    links = {}                  # VirtualLink objects
    interfaces = {}             # Interface objects
    mappings_container = {}     # Mapping interfaces to containers
    mappings_interfaces = {}    # Mapping containers to interfaces
    mappings_gateways = {}      # Mapping interfaces to gateways
    mappings_ip = {}            # Mapping interfaces to ip
    mappings_summaries = {}     # Mapping summaries to ip
    ignored_interfaces = []

    current_host_id = host.find("id").text

    # only make containers for current host
    if current_host_id == host_id:
        #c = emulator.elements.Container(current_host_id, ContainerType.NONE)
        #c.destroy = destroy
        #containers[current_host_id] = c

        for container in host.findall('containers/container'):
            c = parse_container(container, host, ignored_interfaces)
            containers[c.container_id] = c

        logging.getLogger(__name__).info("Waiting until lxc-containers have successfully booted.")

        # boot_queue = []
        #
        # for container_id, container in containers.items():
        #     t = threading.Thread(target=container.set_pid)
        #     boot_queue.append(t)
        #
        # #[x.start() for x in boot_queue]
        # started = []
        # i = 0
        # for t in boot_queue:
        #     t.start()
        #     started.append(t)
        #     i += 1
        #     if i % 5 == 0:
        #         [x.join() for x in started]
        #         started = []
        for container_id, container in containers.items():
            container.set_pid()

        shell = pexpect.spawn("/bin/bash")
        for link in host.findall('links/link'):
            l = parse_link(link, interfaces, mappings_container, mappings_interfaces, mappings_gateways, mappings_ip,
                           mappings_summaries, containers, ignored_interfaces, shell)
            if l is not None:
                links[l.veth0.veth] = l
                links[l.veth1.veth] = l

        for bridge in host.findall('bridges/bridge'):
            b = parse_bridge(bridge, shell)
            bridges[b.bridge_id] = b

        configured_host = {
            "host_id": current_host_id,
            "containers": containers,
            "bridges": bridges,
            "links": links,
            "interfaces": interfaces,
            "mappings": mappings_container,
            "mappings_interfaces": mappings_interfaces,
            "mappings_gateways": mappings_gateways,
            "mappings_summaries": mappings_summaries,
            "mappings_ip": mappings_ip
        }

        #logging.getLogger(__name__).info("Waiting for containers to boot.")
        #[x.join() for x in boot_queue]

        move_vinterfaces(configured_host)
        set_summaries(configured_host)
        set_gateways(configured_host)

        lxcbr_macs = {}
        dp_interfaces = {}
        ## set lxcbr0 macs to host post routing variables
        for container_id, container in containers.items():
            if container.configuration is not None:
                lxcbr_macs[container.container_id] = container.configuration.mac
                dp_interfaces[container.container_id] = container.configuration.interfaces  # collections.OrderedDict(sorted(container.configuration.interfaces.items(), key=lambda t: t[0]))
        containers[current_host_id].postrouting['lxcbrmacs'] = lxcbr_macs

        containers[current_host_id].postrouting['dpinterfaces'] = dp_interfaces  #collections.OrderedDict(sorted(dp_interfaces.items(), key=lambda t: t[0]))
        print(containers[current_host_id].postrouting['dpinterfaces'])

        for interface_id, gateway in mappings_gateways.items():
            logging.getLogger(__name__).info("%s->%s", interface_id, gateway)

        for container_id, container in containers.items():
            #run pre routing script
            container.run_pre_routing(template_environment)

        for container_id, container in containers.items():
            #run routing script
            container.run_routing(template_environment)

        for container_id, container in containers.items():
            #run post routing script
            container.run_post_routing(template_environment)

        logging.getLogger(__name__).info("Set controllers to bridges.")
        for bridge_id, bridge in bridges.items():
            bridge.set_controller()

        return configured_host
    else:
        return None


def move_vinterfaces(configured_host):
    for vinterface, container_id in configured_host["mappings"].items():
        # moving virtual interface to containers.
        c = configured_host['containers'][container_id]
        l = configured_host['links'][vinterface]
        l.setns(vinterface, c)
    time.sleep(1)


def set_summaries(configured_host):
    logging.getLogger(__name__).info("Setting summaries")
    for interface_id, interface in configured_host['interfaces'].items():
        container_id = configured_host['mappings'][interface_id]
        container = configured_host['containers'][container_id]
        if interface.address is not None:
            logging.getLogger(__name__).info(interface_id)
            for summary, via in configured_host["mappings_summaries"].items():
                #print " checking for:  %s, via %s" % (summary, via)

                # via must be in same subnet as address in this interface
                same_subnet_via = (netaddr.IPNetwork(via) == netaddr.IPNetwork(interface.address))

                # check if summary is in same subnet or not
                existing_summaries = []
                for route in container.routing['routes']:
                    existing_summaries.append(netaddr.IPNetwork(route.address))
                existing_summaries = netaddr.cidr_merge(existing_summaries)
                route_exists = False
                for route in existing_summaries:
                    if route.network == netaddr.IPNetwork(summary).network:
                        route_exists = True

                if same_subnet_via and not route_exists:
                    network = netaddr.IPNetwork(summary)
                    address = "%s/%s" % (network.network, network.prefixlen)
                    summary_route = emulator.elements.Route(address, interface.veth)
                    summary_route.via = str(netaddr.IPNetwork(via).ip)
                    container.routing["routes"].append(summary_route)
                    logging.getLogger(__name__).info("Adding %s to %s", summary_route.address, container.container_id)


def set_gateways(configured_host):
    for container_id, container in configured_host['containers'].items():
        gw_interface = container.gateway
        if gw_interface is not None and gw_interface in configured_host['mappings_gateways']:
            gw_address = configured_host['mappings_gateways'][gw_interface]
            route = emulator.elements.Route(gw_address, gw_interface)
            container.routing['gateway'] = route
        elif gw_interface is not None:
            container.routing['gateway'] = emulator.elements.Route(gw_interface, "")
        else:
            container.routing['gateway'] = emulator.elements.Route("0.0.0.0", "")


def find_interfaces(container_id, host):
    # needed for config file
    interfaces = {}
    for link in host.findall('links/link'):
        link_id = link.find('id').text
        for vinterface in link.findall('vinterface'):
            if vinterface.find('container').text == container_id:
                interface_id = vinterface.find('id').text
                addr_node = vinterface.find('address')
                if addr_node is None:
                    address = ""
                else:
                    address = addr_node.text
                interfaces[interface_id] = {'linkid': link_id,
                                            'address': address}
    return interfaces


def parse_container(container, host, ignored_interfaces):

    container_id = container.find("id").text
    container_type = eval("ContainerType.%s" % container.find("type").text)

    if is_lxc(container_type):
        template = container.find("template").text
        storage = eval("BackingStore.%s" % container.find("storage").text)
    else:
        template = ""
        storage = BackingStore.NONE

    interfaces = find_interfaces(container_id, host)
    # if container_type == ContainerType.LXC or container_type == ContainerType.LXCCLONE:
    #     interfaces = find_interfaces(container_id, host)
    # else:
    #     interfaces = None

    c = emulator.elements.Container(container_id, container_type, template, storage, interfaces, ignored_interfaces)

    password = container.find("password")
    if password is not None:
        c.password = password.text

    username = container.find("username")
    if username is not None:
        c.username = username.text

    parse_script(container, c, "prerouting")
    parse_script(container, c, "routing")
    parse_script(container, c, "postrouting")
    parse_script(container, c, "cleanup")

    # if prerouting is not None:
    #     c.preroutingscript = prerouting.text
    #
    # routing = container.find("routing")
    # if prerouting is not None:
    #     c.routingscript = routing.text
    #
    # postrouting = container.find("postrouting")
    # if prerouting is not None:
    #     c.postroutingscript = postrouting.text
    #
    # cleanup = container.find("cleanup")
    # if cleanup is not None:
    #     c.cleanupscript = cleanup.text

    gateway = container.find("gateway")
    if gateway is not None:
        c.gateway = gateway.text

    return c


def parse_script(scriptnode, container, type):
    scriptnode = scriptnode.find(type)
    script = None
    parameters = {}
    if scriptnode is not None:
        scriptname = scriptnode.find("script")
        if scriptname is not None:
            script = scriptname.text
        parametersnode = scriptnode.find("parameters")
        if parametersnode is not None:
            for parameter in parametersnode:
                parameters[parameter.tag] = parameter.text
    if type == "prerouting":
        container.preroutingscript = script
        container.prerouting.update(parameters)
    elif type == "routing":
        container.routingscript = script
        container.routing.update(parameters)
    elif type == "postrouting":
        container.postroutingscript = script
        container.postrouting.update(parameters)
    elif type == "cleanup":
        container.cleanupscript = script
        container.cleanupsettings.update(parameters)


def parse_bridge(bridge, shell):
    bridge_id = bridge.find("id").text
    address = bridge.find("address")
    bridge_type = eval("BridgeType.%s" % bridge.find("type").text)

    if address is None:
        ip = "0.0.0.0"
    else:
        ip = address.text

    # creating the bridge
    b = emulator.elements.Bridge(bridge_id, ip, bridge_type, shell=shell)

    controller = bridge.find("controller")
    if controller is not None and controller.text in systemconfig.nodes:
        b.controller = systemconfig.nodes[controller.text]
        #b.controller = controller.text

    controller_port = bridge.find("controller_port")
    if controller_port is not None:
        b.controller_port = controller_port.text


    datapath = bridge.find("datapath")
    if datapath is not None:
        b.datapath = datapath.text

    for interface in bridge.findall('interfaces/interface'):
        b.addif(interface.text)

    return b


def parse_link(link, interfaces, mappings_container, mappings_interfaces, mappings_gateways, mappings_ip,
               mappings_summaries, containers, ignored_interfaces, linksshell):
    """

    :param link:
    :param interfaces:
    :param mappings_container:
    :param mappings_interfaces:
    :param mappings_gateways:
    :param mappings_ip:
    :param mappings_summaries:
    :param containers:
    :return:
    """
    veth0 = None
    veth1 = None
    veth0_ip = None
    veth1_ip = None
    addresses = {}
    count = 1
    routes0 = []
    routes1 = []
    ignore = False
    for vinterface in link.findall('vinterface'):
        if vinterface.find("id").text in ignored_interfaces:
                ignore = True
    for vinterface in link.findall('vinterface'):
        if not ignore:
            vinterface_id = vinterface.find("id").text
            container_id = vinterface.find("container").text
            address = vinterface.find("address")

            mappings_container[vinterface_id] = container_id

            routes_tree = vinterface.find("routes")
            veth = None
            if count == 1:
                veth0 = emulator.elements.VirtualInterface(vinterface_id)
                if not address is None:
                    veth0_ip = address.text
                    veth0.address = veth0_ip
                    #veth0.routes.extend(routes)
                    parse_summaries(vinterface, mappings_summaries, veth0_ip)
                    parse_routes(routes_tree, routes0, vinterface_id)
                    veth = veth0
            else:
                veth1 = emulator.elements.VirtualInterface(vinterface_id)
                if not address is None:
                    veth1_ip = address.text
                    veth1.address = address.text
                    parse_summaries(vinterface, mappings_summaries, veth1_ip)
                    #veth1.routes.extend(routes)
                    parse_routes(routes_tree, routes1, vinterface_id)
                    veth = veth1

            if container_id not in mappings_interfaces:
                mappings_interfaces[container_id] = []
            mappings_interfaces[container_id].append(veth)
            if veth is not None:
                interfaces[veth.veth] = veth

            count += 1
    if not ignore:
        # map gateways on interfaces
        if veth1_ip is not None:
            mappings_gateways[veth0.veth] = netaddr.IPNetwork(veth1_ip).ip
        if veth0_ip is not None:
            mappings_gateways[veth1.veth] = netaddr.IPNetwork(veth0_ip).ip
            # set routing via
        for route in routes0:
            route.via = netaddr.IPNetwork(veth1.address).ip
        for route in routes1:
            route.via = netaddr.IPNetwork(veth0.address).ip

        # creating the link
        l = emulator.elements.VirtualLink(veth0, veth1, shell=linksshell)

        # moving virtual interface to containers.
        c1 = containers[mappings_container[veth0.veth]]

        c2 = containers[mappings_container[veth1.veth]]

        # setting ip addresses and routing
        if not veth0_ip is None:
            mappings_ip[veth0.veth] = veth0_ip
            c1.config_link(veth0)
            if len(routes0) > 0:
                c1.routing['routes'].extend(routes0)

        if not veth1_ip is None:
            mappings_ip[veth1] = veth1_ip
            c2.config_link(veth1)
            if len(routes1) > 0:
                c2.routing['routes'].extend(routes1)

        return l
    else:
        return None


def parse_routes(routes_tree, routes, vinterface_id):
    for route_element in routes_tree.findall('route'):
        network = netaddr.IPNetwork(route_element.text)
        route_address = "%s/%s" % (network.network, network.prefixlen)
        route = emulator.elements.Route(route_address, vinterface_id)
        routes.append(route)


def parse_summaries(vinterface, mappings_summaries, address):
    summaries = vinterface.find("summarizes")
    for summary in summaries.findall('summary'):
        mappings_summaries[summary.text] = address
