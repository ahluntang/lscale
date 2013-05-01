#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import traceback
import argparse

from utilities import logger
from utilities import exceptions
import logging
import generator
import emulator

def parse_arguments():
    parser = argparse.ArgumentParser(description='Large-Scale Framework.')
    subparsers = parser.add_subparsers(help='sub-command help',dest='subparser_name')

    #parser for generating topologies
    genparser = subparsers.add_parser('generate', help='help for generating topologies')
    genparser.add_argument('-f', '--file', default = 'output/topology.xml', help = 'output file to write to.', required = False)
    genparser.add_argument('-e', '--example', default = 'smalltop', help = 'example to create topology for', required = False)


    # parser for emulating topologies
    emparser = subparsers.add_parser('emulate', help='help for emulating topologies')
    emparser.add_argument('-f', '--file', default = 'output/topology.xml', help = 'input file.', required = False)
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


    # run generator or emulator based on arguments
    if args['subparser_name'] == "generate" :
        try:
            generator.generate(args['example'],args['file'])
        except Exception, e :
            logging.getLogger(__name__).exception("Could not generate topology.")

    elif args['subparser_name'] == "emulate" :
        parsed_topology = {}
        try:
            emulator.emulate(args['file'], args['id'], parsed_topology)
        except exceptions.InsufficientRightsException :
            logging.getLogger(__name__).exception("Could not emulate topology.")
            os._exit(1)
        except Exception, e:
            logging.getLogger(__name__).exception("Could not emulate topology.")
            raise e
    else:
        raise exceptions.IncorrectArgumentsException("Error: check your arguments.")
        os._exit(1)

    return 0


if __name__ == "__main__":
    try:

        main()

    except SystemExit, e:
        raise e
        os._exit(1)

    except Exception, e:
        logger = logging.getLogger(__name__)
        logger.exception(str(e))
        logger.exception(traceback.print_exc())
        traceback.print_exc()
        os._exit(1)
