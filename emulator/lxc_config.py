

class Configuration(object):

    def __init__(self, name, mac):
        self.file = "output/configs/{}.ini".format(name)
        self.name = name
        self.mac = mac
        self.interfaces = {}  # 'vethname : macaddress'
        self.config = None
        pass

    def add_interface(self, interface_id, mac, address, linkid):
        self.interfaces[interface_id] = {'mac': mac,
                                         'address': address,
                                         'linkid': linkid}

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
        for interface_id, setting in self.interfaces.items():
            result += "lxc.network.type = veth\n"
            result += "lxc.network.flags = up\n"
            result += "lxc.network.veth.pair = {}\n".format(interface_id)
            result += "lxc.network.hwaddr = {}\n".format(setting['mac'])
            result += "lxc.network.ipv4 = {}\n".format(setting['address'])
            result += "lxc.network.link={}\n\n".format(setting['linkid'])

        return result

    def create_config(self):
        self.config = self.output()

    def write(self):
        with open(self.file, "w") as text_file:
            text_file.write(self.output())
