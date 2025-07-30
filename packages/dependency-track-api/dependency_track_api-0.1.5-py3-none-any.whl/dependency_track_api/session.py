"""Session class for the Dependency Track API."""

import requests


class DependencyTrackAPISession:
    """
    Session class for the Dependency Track API.

    This class provides methods to open and close the api session.
    """

    def __init__(self, session_api_host: str, session_api_key: str):
        """
        Dependency Track API Session Class Constructor.

        Args:
            api_host (str): The host where is located the Dependency Track API instance.
            api_key (str): The API key for accessing the Dependency Track API.
        """
        self.api_base_url = f"{session_api_host}/api"
        self.session = requests.Session()
        self.session.headers.update({"X-Api-Key": f"{session_api_key}"})

    def __del__(self):
        """
        Dependency Track API Session.

        This method closes the session used to interact with the Dependency Track API.
        """
        self.session.close()

    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Perform an HTTP GET request.

        Args:
            url (str): The URL for the request.
            **kwargs: Additional keyword arguments to pass to `requests.Session.get`.

        Returns:
            requests.Response: The response object.
        """
        return self.session.get(url, **kwargs)

    def post(self, url: str, data=None, json=None, **kwargs) -> requests.Response:
        """
        Perform an HTTP POST request.

        Args:
            url (str): The URL for the request.
            data (dict, bytes, or file-like object): The body for the request.
            json (dict): JSON data for the request.
            **kwargs: Additional keyword arguments to pass to `requests.Session.post`.

        Returns:
            requests.Response: The response object.
        """
        return self.session.post(url, data=data, json=json, **kwargs)

    def put(self, url: str, data=None, json=None, **kwargs) -> requests.Response:
        """
        Perform an HTTP PUT request.

        Args:
            url (str): The URL for the request.
            data (dict, bytes, or file-like object): The body for the request.
            json (dict): JSON data for the request.
            **kwargs: Additional keyword arguments to pass to `requests.Session.put`.

        Returns:
            requests.Response: The response object.
        """
        return self.session.put(url, data=data, json=json, **kwargs)

    def delete(self, url: str, **kwargs) -> requests.Response:
        """
        Perform an HTTP DELETE request.

        Args:
            url (str): The URL for the request.
            **kwargs: Additional keyword arguments to pass to `requests.Session.delete`.

        Returns:
            requests.Response: The response object.
        """
        return self.session.delete(url, **kwargs)
