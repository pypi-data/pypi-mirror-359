# *** imports

# ** app
from ...data import DataObject
from ...data.app import AppInterfaceYamlData
from ...contracts.app import AppRepository, AppInterface
from ...clients import yaml_client


# *** proxies

# ** proxy: app_yaml_proxy
class AppYamlProxy(AppRepository):

    # * field: config_file
    config_file: str = None

    # * method: init
    def __init__(self, app_config_file: str):
        '''
        Initialize the YAML proxy.

        :param app_config_file: The application configuration file.
        :type app_config_file: str
        '''

        # Set the configuration file.
        self.config_file = app_config_file

    # * method: list_interfaces
    def list_interfaces(self) -> list[AppInterface]:
        '''
        List all app interfaces.

        :return: The list of app interfaces.
        :rtype: List[AppInterface]
        '''

        # Load the app interface data from the yaml configuration file and map it to the app interface object.
        interfaces = yaml_client.load(
            self.config_file,
            create_data=lambda data: [
                DataObject.from_data(
                    AppInterfaceYamlData,
                    id=interface_id,
                    **record
                ).map() for interface_id, record in data.items()],
            start_node=lambda data: data.get('interfaces'))

        # Return the list of app interface objects.
        return interfaces

    # * method: get_interface
    def get_interface(self, id: str) -> AppInterface:
        '''
        Get the app interface.

        :param id: The app interface id.
        :type id: str
        :return: The app interface.
        :rtype: AppInterface
        '''

        # Load the app interface data from the yaml configuration file.
        _data: AppInterface = yaml_client.load(
            self.config_file,
            create_data=lambda data: DataObject.from_data(
                AppInterfaceYamlData,
                id=id, 
                **data
            ),
            start_node=lambda data: data.get('interfaces').get(id))

        # Return the app interface object.
        # If the data is None, return None.
        try:
            return _data.map()
        except AttributeError:
            return None