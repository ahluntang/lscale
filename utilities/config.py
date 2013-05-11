
try:
    import configparser
except:
    import ConfigParser as configparser # python 2


proxy = None

def read_config(configfile='config.ini'):
    config = configparser.ConfigParser()
    config.read(configfile)
    if 'connection' in config:
        proxy = config['connection']['proxy']
