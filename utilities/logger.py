import os
import time
import logging


def set_logging(logging_level):
    """ set logging options

    :param logging_level: minimal level that should be logged to file
    :raise: when path to logs is not a directory or directory could not be created.
    """
    logdir = 'logs'
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    # if log dir exists, configure the logging.
    if os.path.exists(logdir) and os.path.isdir(logdir):


        # datetime format
        datetime_format = '%d/%m/%Y %H:%M:%S'
        datetime_format_file = '%d-%m-%Y_%H-%M-%S'

        # location for logfile.
        logfile = "%s/%s_lscale.log" % (logdir, time.strftime(datetime_format_file, time.gmtime()))

        # logformat for each line
        logformat = '%(asctime)s [%(levelname)s] %(message)s'

        # configure the logging framework.
        logging.basicConfig(filename=logfile, format=logformat, datefmt=datetime_format, level=logging_level)

        # Log INFO and higher to console as well.
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logformat='[%(levelname)s] %(message)s'
        console.setFormatter(logging.Formatter(logformat))

        # add the handler to the root logger
        logging.getLogger('').addHandler(console)

    elif os.path.exists(logdir):
        raise IOError("Path to logs is not a directory!")
        pass
    else:
        raise IOError("Log directory not created!")
        pass
