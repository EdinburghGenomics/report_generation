import os
import yaml

class Configuration:
    def __init__(self, cfg_search_path):
        self.cfg_search_path = cfg_search_path
        self.config_file = self._find_config_file(self.cfg_search_path)
        self.content = yaml.safe_load(open(self.config_file, 'r'))

    @staticmethod
    def _find_config_file(search_path):
        for p in search_path:
            if p and os.path.isfile(p):
                return p
        raise Exception('Could not find config file in self.cfg_search_path')

    def get(self, item, ret_default=None):
        """
        Dict-style item retrieval with default
        :param item: The key to search for
        :param ret_default: What to return if the key is not present
        """
        try:
            return self[item]
        except KeyError:
            return ret_default

    def query(self, *parts, top_level=None, ret_default=None):
        """
        Drill down into a config, e.g. cfg.query('logging', 'handlers', 'a_handler', 'level')
        :return: The relevant item if it exists in the config, else None.
        """
        if top_level is None:
            top_level = self.content
        item = None

        for p in parts:
            item = top_level.get(p)
            if item:
                top_level = item
            else:
                return ret_default

        return item

    def report(self):
        return yaml.safe_dump(self.content, default_flow_style=False)

    def __getitem__(self, item):
        """
        Allow dict-style access, e.g. config['this'] or config['this']['that']
        """
        return self.content[item]

    def __contains__(self, item):
        """
        Allow search in the first layer of the config with "in" operator
        """
        return self.content.__contains__(item)


class EnvConfiguration(Configuration):
    def __init__(self, cfg_search_path=None):
        if not cfg_search_path:
            cfg_search_path = [
                os.getenv('REPORTGENERATIONCONFIG'),
                os.path.expanduser('~/.reportgeneration.yaml')
            ]
        super().__init__(cfg_search_path)
        env = os.getenv('REPORTGENERATIONENV', 'development')
        if self.content.get('default'):
            self.content = dict(self._merge_dicts(self.content['default'], self.content[env]))
        else:
            self.content = self.content[env]

    @classmethod
    def _merge_dicts(cls, default_dict, override_dict):
        """
        Recursively merge a default dict and an overriding dict.
        """
        for k in set(override_dict.keys()).union(default_dict.keys()):
            if k in default_dict and k in override_dict:
                if type(default_dict[k]) is dict and type(override_dict[k]) is dict:
                    yield k, dict(cls._merge_dicts(default_dict[k], override_dict[k]))
                else:
                    yield k, override_dict[k]
            elif k in default_dict:
                yield k, default_dict[k]
            else:
                yield k, override_dict[k]

    def merge(self, override_dict):
        """
        Merge the provided dict with the config content potententially overiding existing parameters
        """
        self.content = dict(self._merge_dicts(self.content, override_dict))

