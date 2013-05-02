#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, signal, fcntl, termios, struct, netaddr
import logging

from emulator.elements import VirtualInterface, VirtualLink
from utilities.compability import read_input
from pexpect import ExceptionPexpect
from utilities import exceptions


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = "\033[1m"


escape_char = "%s^]%s" % (bcolors.WARNING, bcolors.ENDC )
escape_char__ASCII = "%sASCII 29%s" % (bcolors.WARNING, bcolors.ENDC )
exit_color = "%sexit%s" % (bcolors.FAIL, bcolors.WARNING)


def interact(configured_hosts, host_id):
    # set starting network for ssh management
    configured_hosts[host_id]['containers'][host_id].management_address = netaddr.IPNetwork("192.168.0.0/30")
    
    prompt = "Available commands: connect, addssh, %s%s: " % (exit_color, bcolors.ENDC)
    response = read_input(prompt).rstrip()
    while True:
        if ( response == "connect" ):
            connect_container(configured_hosts, host_id)
            response = read_input(prompt).rstrip()
        elif (response == "addssh"):
            add_ssh(configured_hosts, host_id)
            response = read_input(prompt).rstrip()
        elif (response == "exit"):
            return 0
        else:
            print("Sorry, I could not recognise that command.")
            response = read_input(prompt).rstrip()


def add_ssh(configured_hosts, host_id):
    available_containers = sorted(configured_hosts[host_id]['containers'].keys())
    prompt = "\nYou are on '%s'\nAvailable containers:\n%s\nSelect container to add ssh connection to: " % (
        host_id, available_containers)
    response = read_input(prompt).rstrip()
    try:

        container = configured_hosts[host_id]['containers'][response]
        if container.is_host:
            print("This is the host, there's no point in adding an additional management interface to the host...")
        else:
            host = configured_hosts[host_id]['containers'][host_id]

            # create interface on host
            # move endpoint to container
            # start ssh

            #network:
            network = host.management_address

            host_address = network[1]
            container_address = network[2]

            container.is_managed = True
            management_interface_id = "m.%s" % container.container_id
            container.management_address = container_address

            # create interface
            hif = VirtualInterface(management_interface_id)
            hif.address = host_address
            cif = VirtualInterface(container.management_interface)
            cif.address = container_address

            # create link
            link = VirtualLink(hif, cif)

            link.setns(cif.veth, container)
            cmd = "ip address add %s/30 brd + dev %s" % (hif.address, hif.veth )
            host.shell.sendline(cmd)
            cmd = "ip link set %s up" % hif.veth
            host.shell.sendline(cmd)
            cmd = "ip address add %s/30 brd + dev %s" % (cif.address, cif.veth )
            container.shell.sendline(cmd)
            cmd = "ip link set %s up" % cif.veth
            container.shell.sendline(cmd)
            container.shell.sendline("/usr/sbin/sshd -f /etc/ssh/sshd_config &")

            container.shell.sendline("SSHPID=$!")
            container.shell.sendline("((SSHPID++))") # daemon in next pid

            print("Created link to %s, reachable through %s" % (container.container_id, container_address))

            host.management_address = host.management_address.next()
    except ExceptionPexpect as e:
        print(" %s Error! Could not create ssh connection. Have you selected the correct container id? %s" % (
        bcolors.WARNING, bcolors.ENDC ))
        raise exceptions.SSHLinkException(e)
    finally:
        return 0


def connect_container(configured_hosts, host_id):
    interact_warning = "  %s warning: if you type %s, you will close the container and all its subprocesses!!! %s" % (
        bcolors.WARNING, exit_color, bcolors.ENDC )

    while True:

        available_containers = sorted(configured_hosts[host_id]['containers'].keys())
        prompt = "\nYou are on '%s'\nAvailable containers:\n%s\nSelect container or type %s%s to go back to main options: " % (
            host_id, available_containers, exit_color, bcolors.ENDC)
        response = read_input(prompt).rstrip()
        if (response != "exit"):
            try:

                container = configured_hosts[host_id]['containers'][response]
                print("length: %s" % len(configured_hosts[host_id]['containers']))
                if container is None:
                    raise exceptions.ContainerNotFoundException("Container %s not found!" % response)

                global global_pexpect_instance
                global_pexpect_instance = container.shell

                signal.signal(signal.SIGWINCH, sigwinch_passthrough)

                interact_message = "Interacting with %s. Type %s (%s) to escape." % (
                container.container_id, escape_char, escape_char__ASCII )
                print(interact_message)
                print(interact_warning)

                container.shell.interact()
                print("Shell sent to background.")
            except KeyError as e:
                print(" %s Error! Have you selected the correct container id? %s" % ( bcolors.WARNING, bcolors.ENDC ))
                #
                # raise e
            except TypeError as e:
                logging.getLogger(__name__).info("Closing interactive mode")

        else:
            return 0


## sigwinch_passthrough function
# ---------------------
# Check for buggy platforms (see pexpect.setwinsize()).
# source: see pexpect examples: script.py
# ---------------------
def sigwinch_passthrough(sig, data):
    if 'TIOCGWINSZ' in dir(termios):
        TIOCGWINSZ = termios.TIOCGWINSZ
    else:
        TIOCGWINSZ = 1074295912 # assume
    s = struct.pack("HHHH", 0, 0, 0, 0)
    a = struct.unpack('HHHH', fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ, s))
    global global_pexpect_instance
    global_pexpect_instance.setwinsize(a[0], a[1])
