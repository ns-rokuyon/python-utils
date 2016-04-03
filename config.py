# coding: utf-8
import os
import argparse


class Config(object):
    """
    Config with argparse and yaml

    [Usage]
        from config import Config
        defs = [
            Config.Defs('file', short='f', help='Path to input file'),
            ...
            ]
        conf = Config(defs)

        filepath = conf.file

    [CLI example]
        $ python sample.py --file test.txt --config config.yaml
    """

    class Def(object):
        """
        Config definition
        """
        def __init__(self, name, short=None, nargs=None, action=None, 
                default=None, help=None):
            self.name = name
            self.short = short
            self.nargs = nargs
            self.action = action
            self.default = default
            self.help = help
            self.keys = self._all_keys

        def __getitem__(self, key):
            return getattr(self, key)

        def _cli_keys(self):
            if self.action:
                return ['action', 'help']
            return ['nargs', 'help']

        def _all_keys(self):
            return ['name', 'short', 'nargs', 'action', 'default', 'help']

        def cli_kwargs(self):
            self.keys = self._cli_keys
            return self


    class Item(object):
        """
        Config item
        """
        def __init__(self, key, value):
            self._items = {}
            self.key = key
            self.value = None
            if isinstance(value, dict):
                self._items = { k: Item(k,v) for k, v in value.items() }
            else:
                self.value = value

        def __getattr__(self, key):
            if key == self.key:
                if self.value:
                    return self.value
                else:
                    return self
            else:
                return self._items.get(key)

        def __call__(self):
            return self.value

        def __str__(self):
            if self.value:
                return str(self.value)
            return None


    def __init__(self, defs, description='Config', use_cli=True,
            use_yaml=True, use_ini=True,
            yamlfile=None, inifile=None, cli_config_opt=None):

        if not isinstance(defs, list): 
            raise TypeError('defs must be list of Config.Defs')

        self._defs = defs
        self._items = {}

        self._args = None
        self._conf = None

        if cli_config_opt is None or not isinstance(cli_config_opt, self.Def):
            cli_config_opt = self.Def('config', 'c', help='Path to config file')

        if use_cli:
            parser = argparse.ArgumentParser(description=description)

            if use_yaml or use_ini:
                self._defs.append(cli_config_opt)

            for d in self._defs:
                if d.short:
                    parser.add_argument('-{}'.format(d.short),
                            '--{}'.format(d.name), **(d.cli_kwargs()))
                else:
                    parser.add_argument(
                            '--{}'.format(d.name), **(d.cli_kwargs()))

            self._args = parser.parse_args()

        if use_yaml:
            import yaml
            yamlfile = getattr(self._args, cli_config_opt.name) if hasattr(
                    self._args, cli_config_opt.name) else yamlfile
            if yamlfile:
                with open(yamlfile, 'r') as f:
                    self._conf = yaml.load(f)
        if use_ini:
            # TODO
            pass
        self._set_items()

    def default(self, name):
        ds = [ d for d in self._defs if d.name == name ]
        return ds[0].default if ds else None
    
    def _set_items(self):
        if self._conf:
            self._items = { k: Item(k,v) for k, v in self._conf.items() }

    def __getattr__(self, name):
        item = None
        value = self.default(name)

        if self._items:
            item = self._items.get(name)

        # Value in config file
        if item:
            item = getattr(item, name)
            if isinstance(item, Item):
                return Item
            else:
                value = item

        # Value in command line arguments
        if self._args and hasattr(self._args, name):
            value = getattr(self._args, name) or value

        return value

    def __str__(self):
        strs = [ s.__str__() for s in self._items ]
        return '\n'.join(strs)

