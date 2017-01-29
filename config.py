from configparser import ConfigParser
import os

class Config():
    """
    Buttflare DDNS config class. Very little error checking right now.
    """
    def __init__(self, verbose=False):
        if 'XDG_CONFIG_HOME' in os.environ:
            config_root = os.environ['XDG_CONFIG_HOME']
        else:
            config_root = os.path.join(os.environ['HOME'], '.config')
        self.config_dir = os.path.join(config_root, 'buttflare')
        config_file = os.path.join(self.config_dir, 'buttflare.ini')
        if verbose:
            print('config_file: {}'.format(config_file))

        config = ConfigParser()
        if not len(config.read(config_file)):
            raise RuntimeError(
                'config file not found at {}'.format(config_file))

        if 'cloudflare' not in config.sections():
            raise RuntimeError('malformed config file {}'.format(config_file))

        # bring in settings under [cloudflare] section as object attributes
        for item in config['cloudflare']:
            setattr(self, item, config['cloudflare'][item])
        config.remove_section('cloudflare')

        # we only support one zone at present
        self.zone_name = config.sections()[0]
        self.v4_host = config[self.zone_name].get('v4_host', None)
        self.v6_host = config[self.zone_name].get('v6_host', None)
