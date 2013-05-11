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
