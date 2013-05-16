import traceback
try:
    import configparser
except:
    import ConfigParser as configparser # python 2

"""
    Global variables:
        proxy
        
"""

def read_config(configfile='config.ini'):
    config = configparser.ConfigParser()
    config.read(configfile)

    # proxy
    global proxy
    try:
        proxy = config.get('connection', 'proxy')
    except configparser.NoOptionError:
        proxy = None

    # nodes
    global nodes
    nodes = {}
    try:
        nodelist = config.items('nodes')
        for node in nodelist:
            nodes[node[0]] = node[1]
    except configparser.NoOptionError:
        nodes = None


def print_all():
    print("Proxy: %s" % proxy)
