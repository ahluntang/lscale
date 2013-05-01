#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import logging
import argparse

from generator.topology import elements, exporter

from generator.examples import *

#
# def set_logging(logging_level):
#     """ set logging options
#
#     :param logging_level: minimal level that should be logged to file
#     :raise: when path to logs is not a directory or directory could not be created.
#     """
#     logdir = 'logs'
#     if not os.path.exists(logdir):
#         os.makedirs(logdir)
#
#     # if log dir exists, configure the logging.
#     if (os.path.exists(logdir) and os.path.isdir(logdir) ):
#
#         # datetime format
#         datetime_format = '%d/%m/%Y %H:%M:%S'
#         datetime_format_file = '%d-%m-%Y_%H-%M-%S'
#
#         # location for logfile.
#         logfile = "%s/%s_topology_generator.log" % (logdir, time.strftime(datetime_format_file, time.gmtime() ) )
#
#         # logformat for each line
#         logformat='%(asctime)s [%(levelname)s] %(message)s'
#
#         # configure the logging framework.
#         logging.basicConfig( filename=logfile, format=logformat, datefmt=datetime_format, level=logging_level)
#
#         # Log INFO and higher to console as well.
#         # define a Handler which writes INFO messages or higher to the sys.stderr
#         console = logging.StreamHandler()
#         console.setLevel(logging.INFO)
#         logformat='[%(levelname)s] %(message)s'
#         console.setFormatter( logging.Formatter(logformat) )
#
#         # add the handler to the root logger
#         logging.getLogger('').addHandler(console)
#
#     elif ( os.path.exists(logdir) ):
#         raise IOError("Path to logs is not a directory!")
#
#     else:
#         raise IOError("Log directory not created!")
#
#
# def parse_arguments():
#     parser = argparse.ArgumentParser(description='Topology Generator.')
#     parser.add_argument('-f', '--file', default='../../topology.xml', help='output file to write to.', required=False)
#     parser.add_argument('-e', '--example', default='smalltop', help='example to create topology for', required=False)
#     return vars(parser.parse_args())


def generate(example, filename, starting_address = "172.16.0.0", last_host_id = 0, last_container_id = 0, last_link_id = 0 ):

    if example == 'cityflow' :
        # create an example topology: cityflow preaggregation phase.
        # see examples package for more info
        created_topology = cityflow.create(last_host_id, last_container_id, last_link_id, starting_address)
    elif example == 'citybus' :
        created_topology = citybus.create(last_host_id, last_container_id, last_link_id, starting_address)
    elif example == 'citystar' :
        created_topology = citystar.create(last_host_id, last_container_id, last_link_id, starting_address)
    elif example == 'smalltop' :
        created_topology = smalltop.create(last_host_id, last_container_id, last_link_id, starting_address)
    else :
        created_topology = cityring.create(last_host_id, last_container_id, last_link_id, starting_address)
        # export topology to xml file
    exporter.write_topology_xml(created_topology, filename)
