#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import traceback
import argparse

from utilities import logger
import logging
import generator
import emulator



def parse_arguments():
    parser = argparse.ArgumentParser(description='Large-Scale Framework.')
    subparsers = parser.add_subparsers(help='sub-command help',dest='subparser_name')

    #parser for generating topologies
    genparser = subparsers.add_parser('generate', help='help for generating topologies')
    genparser.add_argument('-f', '--file', default = '../../topology.xml', help = 'output file to write to.', required = False)
    genparser.add_argument('-e', '--example', default = 'smalltop', help = 'example to create topology for', required = False)


    # parser for emulating topologies
    emparser = subparsers.add_parser('emulator', help='help for emulating topologies')
    emparser.add_argument('-f', '--file', default = 'topology.xml', help = 'input file.', required = False)
    emparser.add_argument('-i', '--id', default = 'h001', help = 'host id that should be used to parse and create containers for', required = False)

    return vars(parser.parse_args())


##########
## Main ##
##########
def main():

    # set logging
    try:
        logger.set_logging(logging.DEBUG)
    except Exception, e:
        print "Could not configure logging framework."
        raise e

    # parse arguments
    try:
        args = parse_arguments()
    except Exception, e:
        logging.getLogger(__name__).exception("Could not parse arguments.")
        raise e

    if args['subparser_name'] == "generate" :
        generator.generate(args['example'],args['file'])
    elif args['subparser_name'] == "emulator" :
        parsed_topology = {}
        emulator.emulate(args['file'],args['id'],parsed_topology)
    else:
        print "Error: check your arguments."

    # set output filename
    filename = args['file']
    logging.getLogger(__name__).info("Using %s as output file for the topology.", filename)

    return 0


if __name__ == "__main__":
    try:
        main()
    except SystemExit, e:
        raise e
    except Exception, e:
        print "ERROR"
        print str(e)
        logger = logging.getLogger(__name__)
        logger.exception(str(e))
        traceback.print_exc()
        os._exit(1)
