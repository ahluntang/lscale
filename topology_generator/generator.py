#!/usr/bin/env python

import os, traceback, time, logging, argparse



def setlogging(logginglevel):
    logdir = 'logs'
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    if (os.path.exists(logdir) and os.path.isdir(logdir) ):
        date_time_format = '%d-%m-%Y_%H-%M-%S' 
        logfile = "%s/%s_topology_generator.log" % (logdir, time.strftime(date_time_format, time.gmtime() ) )
        logging.basicConfig( filename=logfile, format='%(asctime)s [%(levelname)s] - %(message)s', datefmt=date_time_format, level=logginglevel)
    elif ( os.path.exists(logdir) ):
        print "Path to logs is not a directory!"
    else:
        print "Log directory not created!"

def parse_arguments():
    parser = argparse.ArgumentParser(description='Topology Generator.')
    parser.add_argument('-f', '--file', default='topology.xml', help='output file to write to.', required=False)
    return vars(parser.parse_args())

##########
## Main ##
##########
def main():
    setlogging(logging.DEBUG)
    args = parse_arguments()

    filename = args['file']

    
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
