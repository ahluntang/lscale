from utilities import script


def print_help(level, cmd, message):
    help_msg = "\t{}\t{}".format(cmd, message)
    for x in range(0, level):
        help_msg = "\t%s" % help_msg
    print(help_msg)


def print_all():
    print_help(0, "lxc-list", "list all lxc-containers")
    script.command("lxc-ps --help", False)
    print_help(0, "lxc-checkconfig", "check if host is capable of running lxc-containers")
