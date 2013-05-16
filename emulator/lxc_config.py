

class Configuration(object):

    def __init__(self, name, mac):
        self.name = name
        self.mac = mac
        self.interfaces = {}  # 'vethname : macaddress'
        pass

    def add_interface(self, name, mac):
        self.interfaces[name] = mac

    def output(self):

        result = ""
        #result += "lxc.utsname = {}\n".format(self.name)

        # adding default link (for lxcbr0)
        result += "lxc.network.type = veth\n"
        result += "lxc.network.flags = up\n"
        result += "lxc.network.hwaddr = {}\n".format(self.mac)
        result += "lxc.network.link=lxcbr0\n\n"

        # add specified links
        for interface, mac in self.interfaces.items():
            result += "lxc.network.type = veth\n"
            result += "lxc.network.flags = up\n"
            result += "lxc.network.veth.pair = {}\n".format(interface)
            result += "lxc.network.hwaddr = {}\n\n".format(mac)

        return result
