


def print_help(level, cmd, message):
    cmd = cmd.ljust(20)
    help_msg = "\t{}\t{}".format(cmd, message)
    for x in range(0, level):
        help_msg = "\t%s" % help_msg
    print(help_msg)


def print_all():
    print_help(0, "lxc-checkconfig", "Check if host is capable of running lxc-containers")
    print_help(0, "lxc-list", "List all lxc-containers on this machine (based on /var/lib/lxc contents).")
    print_help(0, "lxc-ps", "Display processes information with related container name if available.")
    print_help(0, "lxc-info", "Display some information about a container with the identifier NAME.")
