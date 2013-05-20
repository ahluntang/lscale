

class Configuration(object):

    def __init__(self, name, mac):
        self.file = "output/configs/{}.ini".format(name)
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
        result += "lxc.network.veth.pair = {}\n".format(self.name)
        result += "lxc.network.hwaddr = {}\n".format(self.mac)
        result += "lxc.network.link=lxcbr0\n\n"

        # add specified links
        for interface, mac in self.interfaces.items():
            result += "lxc.network.type = veth\n"
            result += "lxc.network.flags = up\n"
            result += "lxc.network.veth.pair = {}\n".format(interface)
            result += "lxc.network.hwaddr = {}\n\n".format(mac)

        return result

    def write(self):
        with open(self.file, "w") as text_file:
            text_file.write(self.output())
