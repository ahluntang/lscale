#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.etree as ET
#from xml.etree import cElementTree
#from xml.etree.cElementTree import Element, SubElement, tostring
from collections import defaultdict
from utilities import ContainerType, BridgeType, is_lxc


def write_topology_xml(topology_root, output):
    root_tree = ET.Element('data')

    hosts_tree = ET.SubElement(root_tree, 'hosts')
    for host_id, host in sorted(topology_root.items()):

        host_tree = ET.SubElement(hosts_tree, 'host')
        hid_element = ET.SubElement(host_tree, 'id')
        hid_element.text = host_id

        containers_tree = ET.SubElement(host_tree, 'containers')
        links_tree = ET.SubElement(host_tree, 'links')
        bridges_tree = ET.SubElement(host_tree, 'bridges')

        links = defaultdict(list)
        #bridges  = defaultdict(list)

        for (container_id, container) in sorted(host['containers'].items()):
            container_tree = ET.SubElement(containers_tree, 'container')
            cid_element = ET.SubElement(container_tree, 'id')
            cid_element.text = container_id

            contype_element = ET.SubElement(container_tree, 'type')
            contype_element.text = str(container.container_type.name)

            # adding username and password
            if container.username is not None:
                uname_element = ET.SubElement(container_tree, 'username')
                uname_element.text = container.username
            if container.password is not None:
                pw_element = ET.SubElement(container_tree, 'password')
                pw_element.text = container.password

            if is_lxc(container.container_type):
                template_element = ET.SubElement(container_tree, 'template')
                template_element.text = container.template

                storage_element = ET.SubElement(container_tree, 'storage')
                storage_element.text = str(container.storage.name)

            # adding template scripts
            pre_element = ET.SubElement(container_tree, 'prerouting')

            pre_script_element = ET.SubElement(pre_element, 'script')
            pre_script_element.text = container.scripts.prerouting

            pre_par_element = ET.SubElement(pre_element, 'parameters')
            for key, value in container.scripts.parameters['prerouting'].items():
                par_element = ET.SubElement(pre_par_element, key)
                par_element.text = value

            routing_element = ET.SubElement(container_tree, 'routing')

            routing_script_element = ET.SubElement(routing_element, 'script')
            routing_script_element.text = container.scripts.routing

            _par_element = ET.SubElement(routing_element, 'parameters')
            for key, value in container.scripts.parameters['routing'].items():
                par_element = ET.SubElement(_par_element, key)
                par_element.text = value

            post_element = ET.SubElement(container_tree, 'postrouting')

            post_script_element = ET.SubElement(post_element, 'script')
            post_script_element.text = container.scripts.postrouting

            post_par_element = ET.SubElement(post_element, 'parameters')
            for key, value in container.scripts.parameters['postrouting'].items():
                par_element = ET.SubElement(post_par_element, key)
                par_element.text = value

            clean_element = ET.SubElement(container_tree, 'cleanup')

            clean_script_element = ET.SubElement(clean_element, 'script')
            clean_script_element.text = container.scripts.cleanup

            clean_par_element = ET.SubElement(clean_element, 'parameters')
            for key, value in container.scripts.parameters['cleanup'].items():
                par_element = ET.SubElement(clean_par_element, key)
                par_element.text = value

            #if container.is_host:
            #    host_element = ET.SubElement(container_tree, 'is_host')

            # adding default gateway
            if container.gateway is not None:
                gw_element = ET.SubElement(container_tree, 'gateway')
                gw_element.text = container.gateway


            # get interfaces
            for interface in container.interfaces:
                # append to links
                link_id = interface.link_id
                interface.set_container(container_id)
                links[link_id].append(interface)

        for bridge_id, bridge in sorted(host['bridges'].items()):
            bridge_element = ET.SubElement(bridges_tree, 'bridge')

            bid_element = ET.SubElement(bridge_element, 'id')
            bid_element.text = bridge.bridge_id

            cid_element = ET.SubElement(bridge_element, 'container')
            cid_element.text = bridge.container_id

            if bridge.address != "0.0.0.0":
                address_element = ET.SubElement(bridge_element, 'address')
                address_element.text = bridge.address

            bridge_type_element = ET.SubElement(bridge_element, 'type')
            bridge_type_element.text = str(bridge.bridge_type.name)

            bridge_controller_element = ET.SubElement(bridge_element, 'controller')
            bridge_controller_element.text = bridge.controller

            bridge_controller_port_element = ET.SubElement(bridge_element, 'controller_port')
            bridge_controller_port_element.text = bridge.controller_port

            bridge_datapath_element = ET.SubElement(bridge_element, 'datapath')
            bridge_datapath_element.text = bridge.datapath

            interface_element = ET.SubElement(bridge_element, 'interfaces')
            for interface in sorted(bridge.interfaces):
                if_element = ET.SubElement(interface_element, 'interface')
                if_element.text = interface.interface_id

                # append to links
                link_id = interface.link_id
                interface.set_container(bridge.container_id)
                links[link_id].append(interface)

        for link_id, interfaces in sorted(links.items()):
            link_tree = None
            link_tree = ET.SubElement(links_tree, 'link')
            lid_element = ET.SubElement(link_tree, 'id')
            lid_element.text = link_id

            for interface in sorted(interfaces):
                if_element = ET.SubElement(link_tree, 'vinterface')
                ifid_element = ET.SubElement(if_element, 'id')
                ifid_element.text = interface.interface_id

                container_element = ET.SubElement(if_element, 'container')
                container_element.text = interface.container_id

                if interface.address is not None:
                    address_element = ET.SubElement(if_element, 'address')
                    address_element.text = interface.address

                sum_tree = ET.SubElement(if_element, 'summarizes')
                if interface.summarizes is not None:
                    for ipnetwork in interface.summarizes:
                        sum_element = ET.SubElement(sum_tree, 'summary')
                        print(str(ipnetwork))
                        sum_element.text = "%s/%s" % (ipnetwork.network, ipnetwork.prefixlen )

                if_routes_element = ET.SubElement(if_element, 'routes')
                for route in interface.routes:
                    if_route_element = ET.SubElement(if_routes_element, 'route')
                    if_route_element.text = route

    print("\n\nEXPORT:\n")
    xml_bytestring = ET.tostring(root_tree, pretty_print=True)
    print(xml_bytestring.decode('utf-8'))

    print("\nWriting to: %s\n" % output)
    with open(output, 'wb+') as f:
        f.write(xml_bytestring)
