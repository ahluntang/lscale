#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import os
import random
import time

import pexpect

from utilities import exceptions, systemconfig, script
from utilities import ContainerType, BridgeType, is_lxc, BackingStore
from emulator import lxc, lxc_config


# list of objects that might need cleanup
cleanup_containers = []
cleanup_links = []
cleanup_bridges = []

#############
## CLASSES ##
#############


class Container(object):
    """Container representation.

    Instances of this class represent a container or host.
    A container will initialise a bash shell that has it's own
    networking namespace in the kernel.

    Instance variables:
        self.container_id -- identification for container
        self.container_type -- sets type of container (host, unshared, lxc or lxc with lvm)
        self.template -- when using lxc, use this template as base
        self.username -- when using lxc, use this as username to automatically log in.
        self.password -- when using lxc, use this as password to automatically log in.
        self.shell -- holds the pexpect shell object for this instance
        self.pid -- pid of the container
        self.preroutingscript --  pre routing script for template
        self.routingscript -- routing script for template
        self.postroutingscript -- post routing script for template
        self.prerouting -- template dictionary variable for pre routing script
        self.routing -- template dictionary variable for routing script
        self.postrouting -- template dictionary variable for post routing script
        self.interfaces -- used for routing
    """

    def __init__(self, container_id, container_type=ContainerType.UNSHARED, template="base", storage=BackingStore.NONE,
                 interfaces=None, ignored_interfaces=None):
        """Constructs a new Container instance.

        Argument is identification for the container.
        Optional argument is a boolean whether it is a container or host.
        """

        # containers must be cleaned after class destruction
        cleanup_containers.append(self)

        logging.getLogger(__name__).info("Creating container %8s", container_id)
        self.container_id = container_id
        self.container_type = container_type
        self.template = template
        self.destroy = True
        self.storage = storage
        self.configuration = None

        logdir = "logs/container_logs"
        if not os.path.exists(logdir):
            os.makedirs(logdir)

        self.log_location = "%s/%s.log" % (logdir, container_id)
        self.logfile = open(self.log_location, 'w+')

        cmd = "/bin/bash"  # default shell

        if self.container_type == ContainerType.LXCCLONE:
            self.clone(interfaces, ignored_interfaces)
        elif self.container_type == ContainerType.LXC:
            self.create(interfaces, ignored_interfaces)
        elif self.container_type == ContainerType.UNSHARED:  # elif container_type == ContainerType.UNSHARED:
            cmd = "unshare --net /bin/bash"
        elif self.container_type == ContainerType.UNSHAREDMOUNT:  # elif container_type == ContainerType.UNSHARED:
            cmd = "unshare --mount --net --uts --ipc /bin/bash"

        # create the shell
        logging.getLogger(__name__).info("Spawn cmd: {}".format(cmd))
        self.shell = pexpect.spawn(cmd, logfile=self.logfile, timeout=None)

        #set prompt
        prompt = "export PS1='%s> '" % container_id
        self.shell.sendline(prompt)

        self.pid = self.shell.pid

        #setting instance variables
        self.username = "ubuntu"
        self.password = "ubuntu"
        self.preroutingscript = None
        self.routingscript = None
        self.postroutingscript = None
        self.cleanupscript = None
        self.prerouting = {'container_id': self.container_id, 'nodes': systemconfig.nodes}
        self.routing = {'container_id': self.container_id, 'routes': [], 'addresses': [],
                        'interfaces': [], 'nodes': systemconfig.nodes}
        self.postrouting = {'container_id': self.container_id, 'nodes': systemconfig.nodes}
        self.cleanupsettings = {'container_id': self.container_id, 'nodes': systemconfig.nodes}
        self.gateway = None
        self.is_managed = False
        self.management_interface = "%s.m" % self.container_id
        self.management_address = None

        logging.getLogger(__name__).info("Created container %8s with pid %8s", container_id, self.pid)

    def __del__(self):
        try:
            self.cleanup()
        except exceptions.CleanupException as e:
            pass

    def clone(self, interfaces, ignored_interfaces):
        if self.container_type == ContainerType.LXCCLONE:
            try:
                base_mac = randomMAC()
                self.configuration = lxc_config.Configuration(self.container_id, base_mac)

                for interface_id, setting in interfaces.items():
                    new_mac = randomMAC()
                    self.configuration.add_interface(interface_id, new_mac, setting['address'], setting['linkid'])
                    # link already set using configuration, add to ignore list in parser.
                    cleanup_bridges.append(Bridge(setting['linkid']))
                    ignored_interfaces.append(interface_id)

                self.configuration.write()
                print(self.configuration.output())

                if self.container_type == ContainerType.LXCCLONE:
                    lxc.clone(self.template, self.container_id, True)
                else:
                    lxc.clone(self.template, self.container_id, True)
            except lxc.ContainerAlreadyExists as e:
                # Clone was not needed
                pass
            # modify config file
            # removing network settings
            cmd = "sed -i '/lxc.network/d' /var/lib/lxc/{}/config\n".format(self.container_id)
            #applying new network settings
            cmd += "mv /var/lib/lxc/{}/config /var/lib/lxc/{}/config_old\n".format(self.container_id, self.container_id)
            cmd += "cat {} /var/lib/lxc/{}/config_old > /var/lib/lxc/{}/config\n".format(self.configuration.file,
                                                                                         self.container_id,
                                                                                         self.container_id)
            #temp_shell = pexpect.spawn("/bin/bash", logfile=self.logfile, timeout=None)
            #temp_shell.sendline(cmd)
            script.command(cmd)

            #time.sleep(2)

            # if lxc.exists(self.container_id):
            #     lxc.start(self.container_id)
            # else:
            #     raise lxc.ContainerDoesntExists('Container {} does not exist!'.format(self.container_id))

    def create(self, interfaces, ignored_interfaces):
        if self.container_type == ContainerType.LXC:
            try:
                base_mac = randomMAC()
                self.configuration = lxc_config.Configuration(self.container_id, base_mac)

                for interface_id, setting in interfaces.items():
                    new_mac = randomMAC()
                    self.configuration.add_interface(interface_id, new_mac, setting['address'], setting['linkid'])
                    # link already set using configuration, add to ignore list in parser.
                    cleanup_bridges.append(Bridge(setting['linkid']))
                    ignored_interfaces.append(interface_id)

                self.configuration.write()
                print(self.configuration.output())
                if self.storage == BackingStore.NONE:
                    lxc.create(self.container_id, self.template, None, self.configuration.file)
                elif self.storage == BackingStore.LVM:
                    lxc.create(self.container_id, self.template, 'lvm', self.configuration.file)
                elif self.storage == BackingStore.BTRFS:
                    lxc.create(self.container_id, self.template, 'btrfs', self.configuration.file)
            except lxc.ContainerAlreadyExists as e:
                # Creation was not needed
                pass

            # if lxc.exists(self.container_id):
            #     lxc.start(self.container_id)
            #     time.sleep(5)
            # else:
            #     raise lxc.ContainerDoesntExists('Container {} does not exist!'.format(self.container_id))

    def set_pid(self):
        # get pid of container
        if is_lxc(self.container_type):

            if lxc.exists(self.container_id):
                lxc.start(self.container_id)
            else:
                raise lxc.ContainerDoesntExists('Container {} does not exist!'.format(self.container_id))

            # cmd = "lxc-info -n %s | awk 'END{print $NF}'" % container_id
            # readpid = pexpect.spawn(cmd)
            # self.pid = readpid.readline()
            # print(" (pid: %8s)" % self.pid)

            lxc.wait(self.container_id, 'RUNNING')

            info = lxc.info(self.container_id)
            self.pid = info['pid']

            logging.getLogger(__name__).info("Container {} is booting, "
                                             "changing pid to {}.".format(self.container_id, self.pid))
            logging.getLogger(__name__).info("Waiting for full boot to attach console.")
            self.shell.sendline("lxc-console -n %s" % self.container_id)
            self.shell.expect('.* login:.*')
            time.sleep(4)

            logging.getLogger(__name__).info("Container {} has successfully started, logging in.".format(self.pid))
            # log into the lxc shell
            self.shell.sendline(self.username)
            self.shell.expect('.*Password:.*')
            self.shell.sendline(self.password)
            if self.username != "root":
                #self.shell.expect('.*Documentation.*')
                time.sleep(4)
                #time.sleep(5)

                self.shell.sendline("sudo su")
                self.shell.sendline(self.password)
                logging.getLogger(__name__).info("{}: changed user to root.".format(self.container_id))

    def cleanup(self, template_environment=None):
        """Cleans up resources on destruction.

        Containers will open a new shell, cleanup will exit this shell.
        """
        if template_environment is not None:
            self.run_cleanup(template_environment)

        if self.container_type is not None and is_lxc(self.container_type):
            #cmd = "lxc-stop -n %s" % self.container_id
            #self.shell.sendline(cmd)
            lxc.stop(self.container_id)
            if self.destroy:
                #cmd = "lxc-destroy -n %s" % self.container_id
                #self.shell.sendline(cmd)
                lxc.destroy(self.container_id)

        try:
            sys.stdout.write(".")
            sys.stdout.flush()
        except:
            pass
            #raise exceptions.CleanupException()
        return True

    def config_link(self, virtual_interface):
        address = Route(virtual_interface.address, virtual_interface.veth)
        self.routing['addresses'].append(address)

    def run_pre_routing(self, template_environment):
        if self.preroutingscript is not None:
            logging.getLogger(__name__).info("# Running prerouting script for %s", self.container_id)

            template = template_environment.get_template(self.preroutingscript)
            cmd = template.render(self.prerouting)
            self.shell.sendline(cmd)
            self.shell.expect('.*SCRIPTFINISHED.*')
        else:
            logging.getLogger(__name__).info("# No prerouting script defined for %s", self.container_id)

    def run_routing(self, template_environment):
        if self.routingscript is not None:
            logging.getLogger(__name__).info("# Running routing script for %s", self.container_id)
            template = template_environment.get_template(self.routingscript)
            cmd = template.render(self.routing)
            self.shell.sendline(cmd)

        else:
            logging.getLogger(__name__).info("# No routing script defined for %s", self.container_id)

    def run_post_routing(self, template_environment):
        if self.postroutingscript is not None:
            logging.getLogger(__name__).info("# Running postrouting script for %s", self.container_id)

            template = template_environment.get_template(self.postroutingscript)
            cmd = template.render(self.postrouting)
            self.shell.sendline(cmd)
            logging.getLogger(__name__).info("# Done postrouting for %s", self.container_id)
        else:
            logging.getLogger(__name__).info("# No postrouting script defined for %s", self.container_id)

    def run_cleanup(self, template_environment):
        if is_lxc(self.container_type):
            cmd = "exit\nlxc-stop -n %s\nlxc-destroy -n %s" % (self.container_id, self.container_id)
            self.shell.sendline(cmd)

        elif self.cleanupscript is not None and template_environment is not None:
            cleanup_msg = "# Running cleanup script for %s" % self.container_id
            logging.getLogger(__name__).info(cleanup_msg)

            template = template_environment.get_template(self.cleanupscript)
            cmd = template.render(self.cleanupsettings)

            self.shell.sendline(cmd)
        else:
            logging.getLogger(__name__).info("# No cleanup script defined for %s", self.container_id)


class Bridge(object):
    """Bridge representation

    Instances of this class represent a bridge on the system.

    Instance variables:
        self.bridge_id -- identification for bridge
        self.address -- ip address for bridge
        self.interfaces -- list of interfaces for bridge
        self.shell -- holds the pexpect shell object for this instance
    """

    def __init__(self, bridge_id, address='0.0.0.0', bridge_type=BridgeType.BRIDGE, controller=None, controller_port=None, datapath=None):
        """Constructs a new bridge instance.

        Argument is the identification of the bridge.
        Optional argument is the address (prefix notation) of the bridge.
            Default value: 0.0.0.0
        """

        # bridges must be cleaned after class destruction
        cleanup_bridges.append(self)

        logging.getLogger(__name__).info("Creating bridge %8s" % bridge_id)

        self.bridge_id = bridge_id
        self.address = address
        self.bridge_type = bridge_type
        self.controller = controller
        self.controller_port = controller_port
        self.datapath = datapath
        self.interfaces = []



        logdir = "logs/bridge_logs"
        if not os.path.exists(logdir):
            os.makedirs(logdir)

        self.log_location = "%s/%s.log" % (logdir, bridge_id)
        self.logfile = open(self.log_location, 'w+')

        self.shell = pexpect.spawn("/bin/bash", logfile=self.logfile)

        # creating bridge
        if self.bridge_type == BridgeType.OPENVSWITCH:
            create_bridge_cmd = "ovs-vsctl add-br %s" % bridge_id
            self.shell.sendline(create_bridge_cmd)
        else:
            create_bridge_cmd = "brctl addbr %s" % bridge_id
            self.shell.sendline(create_bridge_cmd)

            cmd = "brctl stp %s on" % bridge_id
            self.shell.sendline(cmd)

        cmd = "ifconfig %s %s up" % (bridge_id, self.address)
        self.shell.sendline(cmd)

        logging.getLogger(__name__).info("Added bridge %8s with address %8s", self.bridge_id, self.address)

    def set_controller(self, controller=None, controller_port=None, datapath=None):
        logging.getLogger(__name__).info("Setting datapath for {} to {}".format(self.bridge_id, self.datapath))
        if controller is not None:
            self.controller = controller
        if controller_port is not None:
            self.controller_port = controller_port
        if datapath is not None:
            self.datapath = datapath

        if self.controller is not None:
            cmd = "ovs-vsctl set Bridge {} other-config:datapath-id={}".format(self.bridge_id, self.datapath)
            self.shell.sendline(cmd)

            cmd = "ovs-vsctl set-controller {} tcp:{}:{}".format(self.bridge_id,
                                                                 self.controller, self.controller_port)
            self.shell.sendline(cmd)

            logging.getLogger(__name__).info("Datapath for {} set to {}".format(self.bridge_id, self.datapath))
            logging.getLogger(__name__).info(
                "Switch {} attached to tcp:{}:{}".format(self.bridge_id, self.controller, self.controller_port))

            self.shell.sendeof()
            #for line in self.shell.readlines():
            #    print(line)
        else:
            logging.getLogger(__name__).info("Switch {} has no controller".format(self.bridge_id))

    def __del__(self):
        try:
            self.cleanup()
        except exceptions.CleanupException as e:
            pass

    def cleanup(self):
        """Cleans up resources on destruction.

        Bridges will create bridges on the system, cleanup will attempt to
        shut down the bridge and remove them.
        """

        try:
            cmd = "ifconfig %s down" % self.bridge_id
            self.shell.sendline(cmd)

            # if self.bridge_type == BridgeType.OPENVSWITCH:
            #     cmd = "ovs-vsctl del-br %s\n" % self.bridge_id
            # else:
            #     cmd = "brctl delbr %s\n" % self.bridge_id

            cmd = "brctl delbr %s\n" % self.bridge_id
            self.shell.write(cmd)
            sys.stdout.write(".")
            sys.stdout.flush()
        except:
            pass
            #raise exceptions.CleanupException("Could not clean up bridge")

        return True

    def addif(self, endpoint):
        self.interfaces.append(endpoint)
        if self.bridge_type == BridgeType.OPENVSWITCH:
            cmd = "ovs-vsctl add-port %s %s" % (self.bridge_id, endpoint)
        else:
            cmd = "brctl addif %s %s" % (self.bridge_id, endpoint)

        logging.getLogger(__name__).info("Adding interface %8s to bridge %8s: %s", endpoint, self.bridge_id, cmd)

        self.shell.sendline(cmd)


class VirtualLink(object):
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

    def __init__(self, veth0, veth1):
        """Constructs a new VirtualLink instance.

        Arguments are the identification of the virtual interfaces veth0 and veth1
        """
        # links must be cleaned after class destruction
        cleanup_links.append(self)

        logging.getLogger(__name__).info("Creating virtual link %8s - %8s", veth0.veth, veth1.veth)
        self.veth0 = veth0
        self.veth1 = veth1

        logdir = "logs/link_logs"
        if not os.path.exists(logdir):
            os.makedirs(logdir)

        self.log_location = "%s/%s.log" % (logdir, "{}-{}".format(veth0, veth1))
        self.logfile = open(self.log_location, 'w+')

        self.shell = pexpect.spawn("/bin/bash", logfile=self.logfile)

        # create the link
        create_link_cmd = "ip link add name %s type veth peer name  %s" % (self.veth0.veth, self.veth1.veth)
        self.shell.sendline(create_link_cmd)
        # set virtual interfaces from link to up
        cmd = "ifconfig %s up" % self.veth0.veth
        self.shell.sendline(cmd)
        cmd = "ifconfig %s up" % self.veth1.veth
        self.shell.sendline(cmd)

        self.veth0.shell = self.shell
        self.veth1.shell = self.shell

        logger = logging.getLogger(__name__)
        logger.info("Added virtual link %8s - %8s", self.veth0.veth, self.veth1.veth)

    def __del__(self):
        try:
            self.cleanup()
        except exceptions.CleanupException as e:
            pass

    def cleanup(self):
        """Cleans up resources on destruction.

        VirtualLinks will create links on the system, cleanup will attempt to
        remove any links made.
        """

        try:
            cmd = "ip link del %s\n" % self.veth0.veth
            self.veth0.shell.write(cmd)
            cmd = "ip link del %s\n" % self.veth1.veth
            self.veth1.shell.write(cmd)
            sys.stdout.write(".")
            sys.stdout.flush()
        except BaseException as e:
            pass

        return True

    def setns(self, veth, container):
        if not container.container_type == ContainerType.NONE:
            cmd = "ip link set %s netns %s" % (veth, container.pid)
            logging.getLogger(__name__).info("Moving interface %8s to %8s: %s", veth, container.container_id, cmd)
            self.shell.sendline(cmd)
            container.routing['interfaces'].append(veth)

            logging.getLogger(__name__).info("Virtual interface %8s moved to %8s", veth, container.container_id)

            if veth == self.veth0.veth:
                self.veth0.shell = container.shell
            elif veth == self.veth1.veth:
                self.veth1.shell = container.shell
            else:
                logging.getLogger(__name__).warn("Apparently %8s does not belong to virtual link "
                                                 "%8s-%8s", veth, self.veth0.veth, self.veth1.veth)


class VirtualInterface(object):
    def __init__(self, veth):
        self.veth = veth
        self.shell = None
        self.address = None
        self.mac = None
        self.datapath = None
        self.routes = []


class Route(object):
    def __init__(self, address, interface):
        self.interface = interface
        self.address = address
        self.netmask = None
        self.via = None


###############
## FUNCTIONS ##
###############


def cleanup(template_environment):
    """Cleanup the system.

    Will check the cleanup lists and remove all objects.
    """
    try:
        logging.getLogger(__name__).info("Cleanup the system.")
        logging.getLogger(__name__).info("This may take a while. Grab a coffee.")

        logging.getLogger(__name__).info("Cleaning links [1/3]")
        cleanup_links[:] = [obj for obj in cleanup_links if obj.cleanup()]

        logging.getLogger(__name__).info("Cleaning bridges [2/3]")
        cleanup_bridges[:] = [obj for obj in cleanup_bridges if obj.cleanup()]

        logging.getLogger(__name__).info("Cleaning containers [3/3]")
        cleanup_containers[:] = [obj for obj in cleanup_containers if obj.cleanup(template_environment)]
    except exceptions.CleanupException as e:
        pass
    except pexpect.ExceptionPexpect as e:
        pass
    except BaseException as e:
        pass


def randomMAC():
    mac = [0x00, 0x16, 0x3e,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))
