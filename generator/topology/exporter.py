#!/usr/bin/env python
# -*- coding: utf-8 -*-


from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement, tostring
from collections import defaultdict


def write_topology_xml(topology_root, output):
    root_tree = Element('data')
    hosts_tree = SubElement(root_tree, 'hosts')
    for host_id, host in sorted(topology_root.items()):

        host_tree = SubElement(hosts_tree, 'host')
        hid_element = SubElement(host_tree, 'id')
        hid_element.text = host_id

        containers_tree = SubElement(host_tree, 'containers')
        links_tree = SubElement(host_tree, 'links')
        bridges_tree = SubElement(host_tree, 'bridges')

        links = defaultdict(list)
        #bridges  = defaultdict(list)

        for (container_id, container) in sorted(host['containers'].items()):

            container_tree = SubElement(containers_tree, 'container')
            cid_element = SubElement(container_tree, 'id')
            cid_element.text = container_id

            virtype_element = SubElement(container_tree, 'virtualizationtype')
            virtype_element.text = str(container.virtualization_type)

            # adding template scripts
            pre_element = SubElement(container_tree, 'prerouting')
            pre_element.text = container.preroutingscript
            routing_element = SubElement(container_tree, 'routing')
            routing_element.text = container.routingscript
            post_element = SubElement(container_tree, 'postrouting')
            post_element.text = container.postroutingscript
            clean_element = SubElement(container_tree, 'cleanup')
            clean_element.text = container.cleanupscript

            if container.is_host:
                host_element = SubElement(container_tree, 'is_host')

            # adding default gateway
            if container.gateway is not None:
                gw_element = SubElement(container_tree, 'gateway')
                gw_element.text = container.gateway

            # get interfaces
            for interface in container.interfaces:
                # append to links
                link_id = interface.link_id
                interface.set_container(container.container_id)
                links[link_id].append(interface)

        for bridge_id, bridge in sorted(host['bridges'].items()):
            bridge_element = SubElement(bridges_tree, 'bridge')

            bid_element = SubElement(bridge_element, 'id')
            bid_element.text = bridge.bridge_id

            cid_element = SubElement(bridge_element, 'container')
            cid_element.text = bridge.container_id

            if bridge.address != "0.0.0.0":
                address_element = SubElement(bridge_element, 'address')
                address_element.text = bridge.address

            interface_element = SubElement(bridge_element, 'interfaces')

            for interface in sorted(bridge.interfaces):
                if_element = SubElement(interface_element, 'interface')
                if_element.text = interface.interface_id

                # append to links
                link_id = interface.link_id
                interface.set_container(bridge.container_id)
                links[link_id].append(interface)

        for link_id, interfaces in sorted(links.items()):
            link_tree = None
            link_tree = SubElement(links_tree, 'link')
            lid_element = SubElement(link_tree, 'id')
            lid_element.text = link_id

            for interface in sorted(interfaces):
                if_element = SubElement(link_tree, 'vinterface')
                ifid_element = SubElement(if_element, 'id')
                ifid_element.text = interface.interface_id

                container_element = SubElement(if_element, 'container')
                container_element.text = interface.container_id

                if interface.address is not None:
                    address_element = SubElement(if_element, 'address')
                    address_element.text = interface.address

                sum_tree = SubElement(if_element, 'summarizes')
                if interface.summarizes is not None:
                    for ipnetwork in interface.summarizes:
                        sum_element = SubElement(sum_tree, 'summary')
                        print(str(ipnetwork))
                        sum_element.text = "%s/%s" % (ipnetwork.network, ipnetwork.prefixlen )

                if_routes_element = SubElement(if_element, 'routes')
                for route in interface.routes:
                    if_route_element = SubElement(if_routes_element, 'route')
                    if_route_element.text = route

    print("\n\nEXPORT:\n")
    #print(tostring(root_tree, pretty_print=True))
    print(tostring(root_tree))
    print("\nWriting to: %s\n" % output)

    #ElementTree(root_tree).write(output, pretty_print=True)

    ElementTree(root_tree).write(output)
