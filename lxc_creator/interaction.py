#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, signal, fcntl, termios, struct
import traceback

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = "\033[1m"


def interact(configured_hosts, host_id) :
    escape_char = "%s^]%s" % (bcolors.WARNING, bcolors.ENDC )
    escape_char__ASCII = "%sASCII 29%s" % (bcolors.WARNING, bcolors.ENDC )
    exit_color = "%sexit%s" % (bcolors.FAIL, bcolors.WARNING)

    interact_warning = "  %s warning: if you type %s, you will close the container and all its subprocesses!!! %s" % (
        bcolors.WARNING, exit_color, bcolors.ENDC )

    while True :

        available_containers = sorted(configured_hosts[host_id]['containers'].keys())
        prompt = "\nYou are on '%s'\nAvailable containers:\n%s\nSelect container or type %s%s to stop the script: " % (
            host_id, available_containers, exit_color, bcolors.ENDC)
        response = raw_input( prompt ).rstrip( )
        if ( response != "exit" ) :
            try :

                shell = configured_hosts[host_id]['containers'][response]

                global global_pexpect_instance
                global_pexpect_instance = shell

                signal.signal( signal.SIGWINCH, sigwinch_passthrough )

                interact_message = "Interacting with %s. Type %s (%s) to escape." % ( shell.container_id, escape_char, escape_char__ASCII )
                print interact_message
                print interact_warning

                shell.shell.interact( chr( 29 ) )
                print "Exited shell."
            except Exception, e :
                print "Error! Are you using the correct container?"
                print str(e)
                traceback.print_exc()
        else :
            return 0


## sigwinch_passthrough function
# ---------------------
# Check for buggy platforms (see pexpect.setwinsize()).
# source: see pexpect examples: script.py
# ---------------------
def sigwinch_passthrough(sig, data) :
    if 'TIOCGWINSZ' in dir( termios ) :
        TIOCGWINSZ = termios.TIOCGWINSZ
    else:
        TIOCGWINSZ = 1074295912 # assume
    s = struct.pack( "HHHH", 0, 0, 0, 0 )
    a = struct.unpack( 'HHHH', fcntl.ioctl( sys.stdout.fileno( ), TIOCGWINSZ, s ) )
    global global_pexpect_instance
    global_pexpect_instance.setwinsize( a[0], a[1] )
