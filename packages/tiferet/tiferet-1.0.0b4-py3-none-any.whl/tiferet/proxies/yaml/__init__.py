# *** imports

# ** core
from typing import Dict, Any

# ** app
from ...commands import raise_error
from ...clients import yaml_client


# *** classes

# ** class yaml_proxy
class YamlProxy(object):
    '''
    A base class for YAML proxies.
    '''

    # * field: config_file
    config_file: str = None

    # * method: init
    def __init__(self, config_file: str):
        '''
        Initialize the YAML proxy.

        :param config_file: The configuration file.
        :type config_file: str
        '''
        self.config_file = config_file

    # * method: load_yaml
    def load_yaml(self, start_node: str = None, create_data: callable = None) -> any:
        '''
        Load data from the YAML configuration file.

        :param start_node: The starting node in the YAML file.
        :type start_node: str
        :param create_data: A callable to create data objects from the loaded data.
        :type create_data: callable
        :return: The loaded data.
        :rtype: any
        '''

        # Load the YAML file using the yaml client.
        try:
            return yaml_client.load(
                self.config_file,
                create_data=create_data,
                start_node=start_node
            )
        except FileNotFoundError as e:
            # If the file is not found, raise an error.
            raise_error.execute(
                'CONFIG_FILE_NOT_FOUND',
                f'Configuration file {self.config_file} not found.',
                self.config_file
            )

    
    # * method: save_yaml
    def save_yaml(self, data: Dict[str, Any]):
        '''
        Save data to the YAML configuration file.

        :param data: The data to save.
        :type data: Dict[str, Any]
        '''

        # Save the data to the YAML file using the yaml client.
        try:
            yaml_client.save(self.config_file, data)
        except FileNotFoundError as e:
            # If the file is not found, raise an error.
            raise_error.execute(
                'CONFIG_FILE_NOT_FOUND',
                f'Configuration file {self.config_file} not found.',
                self.config_file
            )