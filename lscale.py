#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import traceback
import argparse
import logging

from utilities import logger
from utilities import exceptions
import generator
import emulator
import configurator


def parse_arguments():
    parser = argparse.ArgumentParser(description='Large-Scale Framework.')
    subparsers = parser.add_subparsers(help='sub-command help', dest='subparser_name')

    #parser for generating topologies
    genparser = subparsers.add_parser('generate', help='help for generating topologies')
    genparser.add_argument('-f', '--file', default='output/topology.xml', help='output file to write to.',
                           required=False)
    genparser.add_argument('-e', '--example', default='smalltop', help='example to create topology for', required=False)

    # parser for emulating topologies
    emparser = subparsers.add_parser('emulate', help='help for emulating topologies')
    emparser.add_argument('-f', '--file', default='output/topology.xml', help='input file.', required=False)
    emparser.add_argument('-i', '--id', default='h001',
                          help='host id that should be used to parse and create containers for', required=False)

    # parser for configuring node
    confparser = subparsers.add_parser('configure', help='help for configuring node')
    subconfparsers = confparser.add_subparsers(help='sub-command help', dest='confparser_name')

    # subparser for creating container
    create_parser = subconfparsers.add_parser('create', help='help for creating container')
    create_parser.add_argument('-n', '--name', default='base', help='container name', required=False)
    create_parser.add_argument('-b', '--backingstore', default='lvm',
                               help='choose backing store (valid options: none, lvm, btrfs)', required=False)
    create_parser.add_argument('-t', '--template', default='ubuntu', help='template name (default: ubuntu)', required=False)

    # subparser for creating lvm volume group
    lvm_parser = subconfparsers.add_parser('lvm', help='help for configuring lvm on this system')
    lvm_parser.add_argument('-n', '--name', default='lxc', help='name of volume group', required=False)
    lvm_parser.add_argument('-d', '--device', default='/dev/sda', help='device name (default: /dev/sda)', required=False)
    lvm_parser.add_argument('-p', '--partition', default='4', help='partition (default: 4)', required=False)

    # subparser for creating clone
    lvm_parser = subconfparsers.add_parser('clone', help='help for cloning containers')
    lvm_parser.add_argument('-o', '--original', default='base', help='original container to clone', required=False)
    lvm_parser.add_argument('-n', '--name', help='new name for container', required=True)
    lvm_parser.add_argument('-s', '--snapshot', default='yes', help='use snapshotting (yes/no)', required=False)
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

    # run generator or emulator based on arguments
    if args['subparser_name'] == "generate":

        generator.generate(args['example'], args['file'])

    elif args['subparser_name'] == "emulate":
        parsed_topology = {}
        emulator.emulate(args['file'], args['id'], parsed_topology)
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

            configurator.create_lvm(name, device, partition)

        elif args['confparser_name'] == "clone":
            original = args['original']
            name = args['name']
            snapshot = args['snapshot']
            if snapshot == "on":
                s = True
            else:
                s = False

            configurator.clone_container(original, name, snapshot)

        else:
            pass
            #raise exceptions.IncorrectArgumentsException("Error: check your arguments.")
    else:
        raise exceptions.IncorrectArgumentsException("Error: check your arguments.")

    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.getLogger(__name__).exception(str(e))
        os._exit(1)
