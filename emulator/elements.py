#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import pexpect
import os
from jinja2 import Environment
from utilities import exceptions

# list of objects that might need cleanup
cleanup_containers = []
cleanup_links = []
cleanup_bridges = []

#############
## CLASSES ##
#############

class ContainerType:
    UNSHARED, LXC, LXCLVM = range(3)

class Container( object ):
    """Container representation.

    Instances of this class represent a container or host.
    For host: set self.host to true or construct with is_host=True
    A container will initialise a bash shell that has it's own
    networking namespace in the kernel.

    Instance variables:
        self.container_id -- identification for container
        self.is_host -- boolean whether this object represents a host (in init space) or container
        self.shell -- holds the pexpect shell object for this instance
        self.pid -- pid of the container (can also be accessed through self.shell.pid)
        self.preroutingscript --  pre routing script for template
        self.routingscript -- routing script for template
        self.postroutingscript -- post routing script for template
        self.prerouting -- template dictionary variable for pre routing script
        self.routing -- template dictionary variable for routing script
        self.postrouting -- template dictionary variable for post routing script
        self.interfaces -- used for routing
    """

    def __init__(self, container_id, is_host= False, virtualization_type = ContainerType.UNSHARED) :
        """Constructs a new Container instance.

        Argument is identification for the container.
        Optional argument is a boolean whether it is a container or host.
        """

        print("Creating container %8s" % container_id,)
        self.container_id = container_id
        self.is_host = is_host

        logdir = "logs/container_logs"
        if not os.path.exists(logdir):
            os.makedirs(logdir)

        self.loglocation = "%s/%s.log" % (logdir, container_id)
        self.logfile = open(self.loglocation, 'wb+')

        # containers must be cleaned after class destruction
        cleanup_containers.append( self )

        if self.is_host:
            cmd = "/bin/bash"
        elif virtualization_type == ContainerType.LXC :
            cmd = "lxc-create -t ubuntu -n %s" % container_id
        elif virtualization_type == ContainerType.LXCLVM :
            #cmd = "lxc-create -t ubuntu -B lvm -n %s" % container_id
            cmd = "lxc-create -t ubuntu -B lvm -n base\nlxc-clone -s -o base -n %s" % container_id
        else: # elif virtualization_type == ContainerType.UNSHARED :
            cmd = "unshare --net /bin/bash"

        # create the shell
        self.shell = pexpect.spawn( cmd, logfile=self.logfile )

        # get pid of container
        if virtualization_type == ContainerType.UNSHARED :
            self.pid = self.shell.pid
            print(" (pid: %8s)" % self.pid)
        else:
            cmd = "sudo lxc-info -n c002 | awk 'END{print $NF}'" % container_id
            readpid = pexpect.spawn( cmd )
            self.pid = readpid.readline()

            # log into the lxc shell
            self.shell.sendline("ubuntu")
            self.shell.sendline("ubuntu")

        #set prompt
        prompt = "export PS1='%s> '" % container_id
        self.shell.sendline( prompt )

        #setting instance variables
        self.preroutingscript     = None
        self.routingscript        = None
        self.postroutingscript    = None
        self.cleanupscript        = None
        self.prerouting           = { 'container_id' : self.container_id }
        self.routing              = { 'container_id' : self.container_id }
        self.routing['routes']    = []
        self.routing['addresses'] = []
        self.postrouting          = { 'container_id' : self.container_id }
        self.cleanupsettings      = { 'container_id' : self.container_id }
        self.gateway              = None
        self.is_managed           = False
        self.management_interface = "%s.m" % self.container_id
        self.management_address   = None

        logger = logging.getLogger( __name__ )
        logger.info( "Created container %8s with pid %8s", container_id, self.pid )

    def __del__(self) :
        self.cleanup( )

    def cleanup(self, template_environment = None) :
        """Cleans up resources on destruction.

        Containers will open a new shell, cleanup will exit this shell.
        """
        if template_environment is not None:
            self.run_cleanup(template_environment)
        try:
            self.shell.write("exit\n")
            sys.stdout.write(".")
            sys.stdout.flush()
        except pexpect.ExceptionPexpect as e:
            raise exceptions.CleanupException(e)
        return True

    def config_link(self, virtualinterface) :
        address = Route(virtualinterface.address, virtualinterface.veth)
        self.routing['addresses'].append(address)

    def run_pre_routing(self, template_environment):
        if self.preroutingscript is not None:
            logging.getLogger( __name__ ).info("# Running prerouting script for %s", self.container_id)

            template = template_environment.get_template(self.preroutingscript)
            cmd = template.render(self.prerouting)
            self.shell.sendline( cmd )
        else:
            logging.getLogger( __name__ ).info("# No prerouting script defined for %s", self.container_id)

    def run_routing(self, template_environment):
        if self.routingscript is not None:
            logging.getLogger( __name__ ).info("# Running routing script for %s", self.container_id)

            template = template_environment.get_template(self.routingscript)
            cmd = template.render(self.routing)
            self.shell.sendline( cmd )

        else:
            logging.getLogger( __name__ ).info("# No routing script defined for %s", self.container_id)

    def run_post_routing(self, template_environment):
        if self.postroutingscript is not None:
            logging.getLogger( __name__ ).info("# Running postrouting script for %s", self.container_id)

            template = template_environment.get_template(self.postroutingscript)
            cmd = template.render(self.postrouting)
            self.shell.sendline( cmd )
            logging.getLogger( __name__ ).info("# Done postrouting for %s", self.container_id)
        else:
            logging.getLogger( __name__ ).info("# No postrouting script defined for %s", self.container_id)


    def run_cleanup(self, template_environment) :
        if self.postroutingscript is not None and not self.is_host:
            cleanup_msg = "# Running cleanup script for %s", self.container_id
            logging.getLogger(__name__).info(cleanup_msg)

            template = template_environment.get_template(self.cleanupscript)
            cmd = template.render(self.cleanupsettings)
            self.shell.sendline(cleanup_msg)
            self.shell.sendline(cmd)
        else :
            logging.getLogger(__name__).info("# No cleanup script defined for %s", self.container_id)



class Bridge( object ) :
    """Bridge representation

    Instances of this class represent a bridge on the system.

    Instance variables:
        self.bridge_id -- identification for bridge
        self.address -- ip address for bridge
        self.interfaces -- list of interfaces for bridge
        self.shell -- holds the pexpect shell object for this instance
    """

    def __init__(self, bridge_id, address = '0.0.0.0') :
        """Constructs a new bridge instance.

        Argument is the identification of the bridge.
        Optional argument is the address (prefix notation) of the bridge.
            Default value: 0.0.0.0
        """

        print("Creating bridge %8s" % bridge_id)
        self.bridge_id = bridge_id
        self.address = address
        self.interfaces = []

        # bridges must be cleaned after class destruction
        cleanup_bridges.append( self )

        self.shell = pexpect.spawn( "/bin/bash" )

        # creating bridge
        create_bridge_cmd = "brctl addbr %s" % bridge_id
        self.shell.sendline( create_bridge_cmd )

        cmd = "ifconfig %s %s up" % (bridge_id, self.address)
        self.shell.sendline( cmd )

        cmd = "brctl stp %s on" % bridge_id
        self.shell.sendline(cmd)

        logger = logging.getLogger( __name__ )
        logger.info( "Added bridge %8s with address %8s", self.bridge_id, self.address )

        # setting bridges may take a while
        #time.sleep(0.5)


    def __del__(self) :
        self.cleanup( )

    def cleanup(self) :
        """Cleans up resources on destruction.

        Bridges will create bridges on the system, cleanup will attempt to
        shut down the bridge and remove them.
        """

        try :
            cmd = "ifconfig %s down" % self.bridge_id
            self.shell.sendline( cmd )

            cmd = "brctl delbr %s\n" % self.bridge_id
            self.shell.write( cmd )
            sys.stdout.write( "." )
            sys.stdout.flush( )
        except pexpect.ExceptionPexpect as e:
            raise exceptions.CleanupException(e)

        return True

    def addif(self, endpoint) :
        self.interfaces.append( endpoint )
        cmd = "brctl addif %s %s" % (self.bridge_id, endpoint)
        print("Adding interface %8s to bridge %8s: %s" % (endpoint, self.bridge_id, cmd))

        logger = logging.getLogger( __name__ )
        logger.info( "Adding interface %8s to bridge %8s", endpoint, self.bridge_id )

        self.shell.sendline( cmd )


class VirtualLink( object ) :
    """Link representation.

    Instances of this class represent virtual links on the system.

    Instance variables:
        self.veth0 -- first endpoint of the virtual link
        self.veth1 -- second endpoint of the virtual link
        self.shell -- holds the pexpect shell object for this instance
        self.veth0shell -- holds the pexpect shell object for the first endpoint of the virtual link.
            Changes when interface is moved to a different network namespace
        self.veth1shell -- holds the pexpect shell object for the first endpoint of the virtual link.
            Changes when interface is moved to a different network namespace
    """

    def __init__(self, veth0, veth1) :
        """Constructs a new VirtualLink instance.

        Arguments are the identification of the virtual interfaces veth0 and veth1
        """

        print("Creating virtual link %8s - %8s" % (veth0.veth, veth1.veth))
        self.veth0 = veth0
        self.veth1 = veth1

        # links must be cleaned after class destruction
        cleanup_links.append( self )

        self.shell = pexpect.spawn( "/bin/bash" )

        # create the link
        create_link_cmd = "ip link add name %s type veth peer name  %s" % (self.veth0.veth, self.veth1.veth)
        self.shell.sendline( create_link_cmd )
        # set virtual interfaces from link to up
        cmd = "ifconfig %s up" % self.veth0.veth
        self.shell.sendline( cmd )
        cmd = "ifconfig %s up" % self.veth1.veth
        self.shell.sendline( cmd )

        self.veth0.shell = self.shell
        self.veth1.shell = self.shell

        logger = logging.getLogger( __name__ )
        logger.info( "Added virtual link %8s - %8s", self.veth0.veth, self.veth1.veth )


    def __del__(self) :
        self.cleanup( )

    def cleanup(self) :
        """Cleans up resources on destruction.

        VirtualLinks will create links on the system, cleanup will attempt to
        remove any links made.
        """

        try :
            cmd = "ip link del %s\n" % self.veth0.veth
            self.veth0.shell.write( cmd )
            cmd = "ip link del %s\n" % self.veth1.veth
            self.veth1.shell.write( cmd )
            sys.stdout.write( "." )
            sys.stdout.flush( )
        except pexpect.ExceptionPexpect as e:
            raise exceptions.CleanupException(e)

        return True

    def setns(self, veth, container) :
        if not container.is_host :
            cmd = "ip link set %s netns %s" % (veth, container.pid)
            print("Moving interface %8s to %8s: %s" % (veth, container.container_id, cmd))
            self.shell.sendline( cmd )

            logger = logging.getLogger( __name__ )
            logger.info( "Virtual interface %8s moved to %8s", veth, container.container_id )

            if (veth == self.veth0.veth) :
                self.veth0.shell = container.shell
            elif (veth == self.veth1.veth) :
                self.veth1.shell = container.shell
            else :
                logger = logging.getLogger( __name__ )
                logger.warn( "Apparently %8s does not belong to virtual link %8s-%8s", veth, self.veth0.veth, self.veth1.veth )



class VirtualInterface(object):

    def __init__(self, veth):
        self.veth = veth
        self.shell = None
        self.address = None
        self.routes = []


class Route(object):

    def __init__(self, address, interface):
        self.interface = interface
        self.address   = address
        self.netmask   = None
        self.via       = None

###############
## FUNCTIONS ##
###############

def cleanup(template_environment) :
    """Cleanup the system.

    Will check the cleanup lists and remove all objects.
    """
    try:
        print("Cleanup the system.")
        print("This may take a while. Grab a coffee.")

        print("\n\nCleaning links [1/3]")
        cleanup_links[:] = [obj for obj in cleanup_links if obj.cleanup( )]

        print("\n\nCleaning bridges [2/3]")
        cleanup_bridges[:] = [obj for obj in cleanup_bridges if obj.cleanup( )]

        print("\n\nCleaning containers [3/3]")
        cleanup_containers[:] = [obj for obj in cleanup_containers if obj.cleanup(template_environment)]
    except pexpect.ExceptionPexpect as e:
        raise exceptions.CleanupException(e)
