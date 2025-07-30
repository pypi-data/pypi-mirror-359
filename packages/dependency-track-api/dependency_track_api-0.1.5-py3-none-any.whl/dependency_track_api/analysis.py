"""Analysis Module."""

from typing import Dict

from .exceptions import DependencyTrackApiError
from .session import DependencyTrackAPISession


class Analysis:
    """Analysis Class."""

    def __init__(self, session: DependencyTrackAPISession):
        """
        Analysis Class Constructor.

        Args:
            session (DependencyTrackAPISession): The session object to interact with the API.
        """
        self.session = session

    def retrieve_analysis(self, project: str, component: str, vulnerability: str) -> Dict:
        """
        Retrieve an analysis trail.

        Args:
            project (str): The UUID of the project.
            component (str): The UUID of the component.
            vulnerability (str): The UUID of the vulnerability.

        Returns:
            dict: The analysis data.
        """
        params = {"project": project, "component": component, "vulnerability": vulnerability}
        response = self.session.get(f"{self.session.api_base_url}/v1/analysis", params=params)
        if response.status_code == 200:
            return response.json()

        descriptions = {
            401: "Unauthorized",
            404: "The project, component, or vulnerability could not be found",
        }

        description = descriptions.get(response.status_code, "Unknown error")
        raise DependencyTrackApiError(description, response)

    def update_analysis(self, analysis_request: Dict) -> Dict:
        """
        Record an analysis decision.

        Args:
            analysis_request (dict): The analysis request data.

        Returns:
            dict: The updated analysis data.
        """
        response = self.session.put(
            f"{self.session.api_base_url}/v1/analysis",
            json=analysis_request,
        )
        if response.status_code == 200:
            return response.json()

        descriptions = {
            401: "Unauthorized",
            404: "The project, component, or vulnerability could not be found",
        }

        description = descriptions.get(response.status_code, "Unknown error")
        raise DependencyTrackApiError(description, response)
