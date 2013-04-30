#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import time
import logging
import argparse

import parser
import interaction
import elements
from jinja2 import Environment, FileSystemLoader

def set_logging(logging_level):
    """ set logging options.

    :param logging_level: minimal level that should be logged to file
    :raise: when path to logs is not a directory or directory could not be created.
    """
    logdir = 'logs'
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    # if log dir exists, configure the logging.
    if (os.path.exists(logdir) and os.path.isdir(logdir) ):

        # datetime format
        datetime_format = '%d/%m/%Y %H:%M:%S'
        datetime_format_file = '%d-%m-%Y_%H-%M-%S'

        # location for logfile.
        logfile = "%s/%s_lxc_creator.log" % (logdir, time.strftime(datetime_format_file, time.gmtime() ) )

        # logformat for each line
        logformat='%(asctime)s [%(levelname)s] %(message)s'

        # configure the logging framework.
        logging.basicConfig( filename=logfile, format=logformat, datefmt=datetime_format, level=logging_level)

        # Log INFO and higher to console as well.
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logformat='[%(levelname)s] %(message)s'
        console.setFormatter( logging.Formatter(logformat) )

        # add the handler to the root logger
        logging.getLogger('').addHandler(console)

    elif ( os.path.exists(logdir) ):
        raise IOError("Path to logs is not a directory!")

    else:
        raise IOError("Log directory not created!")

def parse_arguments():
    parser = argparse.ArgumentParser(description='LXC Creator.')
    parser.add_argument('-f', '--file', default='topology.xml', help='input file.', required=False)
    parser.add_argument('-i', '--id', default='h001', help='host id that should be used to parse and create containers for', required=False)
    return vars(parser.parse_args())


def emulate(filename, host_id, parsed_topology):

    template_environment = Environment(loader=FileSystemLoader('templates'))

    parser.parse(filename, template_environment, parsed_topology, host_id)
    interaction.interact(parsed_topology, host_id)
    elements.cleanup(template_environment)
