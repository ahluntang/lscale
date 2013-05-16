#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import traceback
import argparse
import logging

from utilities import logger
from utilities import exceptions
from utilities import systemconfig

import generator
import emulator
import configurator
import monitor


def parse_arguments():
    parser = argparse.ArgumentParser(description='Large-Scale Framework.')
    sub_parsers = parser.add_subparsers(help='sub-command help', dest='subparser_name')

    #parser for generating topologies
    gen_parser = sub_parsers.add_parser('generate', help='help for generating topologies')
    gen_parser.add_argument('-f', '--file', default='output/topology.xml', help='output file to write to.',
                            required=False)
    gen_parser.add_argument('-e', '--example', default='smalltop', help='example to create topology for',
                            required=False)

    # parser for emulating topologies
    em_parser = sub_parsers.add_parser('emulate', help='help for emulating topologies')
    em_parser.add_argument('-f', '--file', default='output/topology.xml', help='input file.', required=False)
    em_parser.add_argument('-i', '--id', default='h001',
                           help='host id that should be used to parse and create containers for', required=False)
    em_parser.add_argument('-d', '--destroy', default='yes',
                           help='destroy created containers while clean up or leave them', required=False)

    # parser for configuring node
    conf_parser = sub_parsers.add_parser('configure', help='help for configuring node')
    sub_conf_parsers = conf_parser.add_subparsers(help='sub-command help', dest='confparser_name')

    # subparser for automatic configuration
    autoconf_parser = sub_conf_parsers.add_parser('autoconfigure', help='help for automatic config')

    # subparser for reading configuration
    readconf_parser = sub_conf_parsers.add_parser('read', help='help for reading config')
    readconf_parser.add_argument('-f', '--file', default='config.ini', help='config file', required=False)

    # subparser for installing the required packages
    install_parser = sub_conf_parsers.add_parser('install', help='help for installing')
    install_parser.add_argument('-p', '--package', default='all', help='select package group to install '
                                                                       '(all, lxc, openvswitch)', required=False)

    restart_parser = sub_conf_parsers.add_parser('restart', help='help for restarting services')
    restart_parser.add_argument('-s', '--service', help='select service to restart (openvswitch)', required=True)

    # subparser for creating container
    create_parser = sub_conf_parsers.add_parser('create', help='help for creating container')
    create_parser.add_argument('-n', '--name', default='base', help='container name', required=False)
    create_parser.add_argument('-b', '--backingstore', default='none',
                               help='choose backing store (valid options: none, lvm, btrfs)', required=False)
    create_parser.add_argument('-t', '--template', default='ubuntu', help='template name (default: ubuntu)',
                               required=False)

    # subparser for creating lvm volume group
    lvm_parser = sub_conf_parsers.add_parser('lvm', help='help for configuring lvm on this system')
    lvm_parser.add_argument('-n', '--name', default='lxc', help='name of volume group', required=False)
    lvm_parser.add_argument('-d', '--device', default='/dev/sda', help='device name (default: /dev/sda)',
                            required=False)
    lvm_parser.add_argument('-p', '--partition', default='4', help='partition (default: 4)', required=False)
    lvm_parser.add_argument('-c', '--cache', default='30', help='size for cache in G (default: 30, 0 for no cache)',
                            required=False)

    # subparser for creating clone
    lvm_parser = sub_conf_parsers.add_parser('clone', help='help for cloning containers')
    lvm_parser.add_argument('-o', '--original', default='base', help='original container to clone', required=False)
    lvm_parser.add_argument('-n', '--name', help='new name for container', required=True)
    lvm_parser.add_argument('-s', '--snapshot', default='yes', help='use snapshotting (yes/no)', required=False)

    #parser for monitoring
    mon_parser = sub_parsers.add_parser('monitor', help='help for monitoring topologies')

    return vars(parser.parse_args())


##########
## Main ##
##########
def main():
    # set logging
    try:
        logger.set_logging(logging.DEBUG)
    except:
        err_msg = "Could not configure logging framework."
        print(err_msg)
        raise exceptions.LoggingException(err_msg)

    # parse arguments
    try:
        args = parse_arguments()
    except:
        os._exit(1)
        #err_msg = "Could not parse arguments."
        #raise exceptions.ArgParseException(err_msg)

    systemconfig.read_config("config.ini")

    # run generator or emulator based on arguments
    if args['subparser_name'] == "generate":

        generator.generate(args['example'], args['file'])

    elif args['subparser_name'] == "emulate":
        parsed_topology = {}
        emulator.emulate(args['file'], args['id'], parsed_topology, args['destroy'])
    elif args['subparser_name'] == "configure":

        if args['confparser_name'] == "create":
            name = args['name']
            backingstore = args['backingstore']
            template = args['template']

            configurator.create_container(name, backingstore, template)

        elif args['confparser_name'] == "lvm":
            name = args['name']
            device = args['device']
            partition = args['partition']
            cachesize = args['cache']

            configurator.create_lvm(name, device, partition, cachesize)

        elif args['confparser_name'] == "clone":
            original = args['original']
            name = args['name']
            snapshot = args['snapshot']
            if snapshot == "yes":
                s = True
            else:
                s = False

            configurator.clone_container(name, original, snapshot)
        elif args['confparser_name'] == "autoconfigure":
            configurator.auto_configure()
        elif args['confparser_name'] == "read":
            file = args['file']
            systemconfig.read_config(file)
            systemconfig.print_all()
        elif args['confparser_name'] == "install":
            package = args['package']
            configurator.install(package)
            systemconfig.print_all()
        elif args['confparser_name'] == "restart":
            service = args['service']
            configurator.restart(service)
        else:
            pass
            #raise exceptions.IncorrectArgumentsException("Error: check your arguments.")
    elif args['subparser_name'] == "monitor":
        print("Use following commands to monitor lxc containers.\n")
        monitor.print_all()
    else:
        raise exceptions.IncorrectArgumentsException("Error: check your arguments.")

    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.getLogger(__name__).exception(str(e))
        os._exit(1)
