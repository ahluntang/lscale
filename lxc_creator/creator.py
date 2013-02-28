#!/usr/bin/env python

import os, traceback, logging

##########
## Main ##
##########
def main():
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
