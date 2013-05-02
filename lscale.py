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
        err_msg = "Could not configure logging framework."
        logging.getLogger(__name__).exception(err_msg)
        raise exceptions.ArgParseException(err_msg)

    # run generator or emulator based on arguments
    if args['subparser_name'] == "generate":
        try:
            generator.generate(args['example'], args['file'])
        except exceptions.GeneratorException as e:
            err_msg = "Could not generate topology."
            logging.getLogger(__name__).exception(err_msg)
            raise e

    elif args['subparser_name'] == "emulate":
        parsed_topology = {}
        try:
            emulator.emulate(args['file'], args['id'], parsed_topology)
        except exceptions.InsufficientRightsException as e:
            err_msg = "Could not emulate topology. %s" % str(e)
            logging.getLogger(__name__).exception(err_msg)
            os._exit(1)
        except exceptions.GeneratorException as e:
            err_msg = "Could not emulate topology. %s" % str(e)
            logging.getLogger(__name__).exception(err_msg)
            raise e
    else:
        raise exceptions.IncorrectArgumentsException("Error: check your arguments.")

    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.getLogger(__name__).exception(str(e))
        logging.getLogger(__name__).exception(traceback.print_exc())
        traceback.print_exc()
        os._exit(1)
