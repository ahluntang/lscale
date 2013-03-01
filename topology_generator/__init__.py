#!/usr/bin/env python

import os
import traceback
import time
import logging
import argparse

import elements
import topology_export
import examples


def set_logging(logging_level):
    """ set logging options

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
        logfile = "%s/%s_topology_generator.log" % (logdir, time.strftime(datetime_format_file, time.gmtime() ) )

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
    parser = argparse.ArgumentParser(description='Topology Generator.')
    parser.add_argument('-f', '--file', default='topology.xml', help='output file to write to.', required=False)
    return vars(parser.parse_args())


def set_filename(filename):
    prompt = "Output filename is currently set to %s. Do you want to change this (N)? " % filename
    response = raw_input(prompt).rstrip().lower()
    while True:
        if (response == 'y' or response == 'yes' ):
            prompt = 'Type the filename: '
            filename = raw_input(prompt).rstrip()
            return filename
        elif (response == 'n' or response == 'no' or response == '' ):
            return filename
        else:
            response = raw_input(prompt).rstrip().lower()

##########
## Main ##
##########
def main():

    # set logging
    try:
        set_logging(logging.DEBUG)
    except Exception, e:
        print "Could not configure logging framework."
        #logging.getLogger(__name__).exception("Could not configure logging framework.")
        raise e

    # parse arguments
    try:
        args = parse_arguments()
    except Exception, e:
        logging.getLogger(__name__).exception("Could not parse arguments.")
        raise e
    
    # set output filename
    filename = args['file']
    logging.getLogger(__name__).info("Using %s as output file for the topology.", filename)



    # defining details for the topology
    # setting base parameters
    last_host_id      = 0
    last_container_id = 0
    last_link_id      = 0
    starting_address  = "172.16.0.0"

    # create an example topology: cityflow preaggregation phase.
    # see examples package for more info
    created_topology = examples.cityflow.pre_aggregation(last_host_id, last_container_id, last_link_id, starting_address)

    # export topology to xml file
    topology_export.write_topology_xml(created_topology, filename)

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
