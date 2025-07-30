"""Main Dependency Track API Class."""

__version__ = "0.1.4"


from typing import Dict

from .access_control_list import AccessControlList
from .analysis import Analysis
from .exceptions import DependencyTrackApiError
from .session import DependencyTrackAPISession


class DependencyTrack(AccessControlList, Analysis):
    """
    Main Dependency Track API Class.

    This class provides methods to interact with the Dependency Track API.
    """

    def __init__(self, api_host: str, api_key: str):
        """
        Dependency Track API Class Constructor.

        Args:
            api_host (str): The host where is located the Dependency Track API instance.
            api_key (str): The API key for accessing the Dependency Track API.
        """
        self.session = DependencyTrackAPISession(
            session_api_host=api_host, session_api_key=api_key
        )
        AccessControlList.__init__(self, session=self.session)
        Analysis.__init__(self, session=self.session)

    def get_version(self) -> Dict:
        """
        Get Dependency Track API Version.

        Returns:
            dict: A dictionary containing information about the Dependency Track API version.

            The dictionary includes the following fields:
            - version (str): The version of the Dependency Track API.
            - timestamp (str): The timestamp when the version information was retrieved.
            - systemUuid (str): The UUID of the system.
            - uuid (str): The UUID of the Dependency Track instance.
            - application (str): The name of the Dependency Track application.
            - framework (dict): A dictionary containing information about the framework including:
                - name (str): The name of the framework.
                - version (str): The version of the framework.
                - timestamp (str): The timestamp when the framework information was retrieved.
                - uuid (str): The UUID of the framework instance.
        """
        response = self.session.get(f"{self.session.api_base_url}/version")

        if response.status_code == 200:
            return response.json()

        description = "Error while quering the api."
        raise DependencyTrackApiError(description, response)
