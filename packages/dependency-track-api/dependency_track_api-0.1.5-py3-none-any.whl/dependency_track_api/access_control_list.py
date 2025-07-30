"""Access Control List Module."""

from typing import Dict, List

from .exceptions import DependencyTrackApiError
from .session import DependencyTrackAPISession


class AccessControlList:
    """Access Control List Class."""

    def __init__(self, session: DependencyTrackAPISession):
        """
        Access Control List Class Constructor.

        Args:
            session (DependencyTrackAPISession): The session object to interact with the API.
        """
        self.session = session

    def add_acl_mapping(self, team: str, project: str) -> Dict:
        """
        Add an Access Control List mapping.

        Args:
            team (str): The UUID of the team.
            project (str): The UUID of the project.

        Returns:
            dict: The response data.
        """
        response = self.session.put(
            f"{self.session.api_base_url}/v1/acl/mapping",
            json={
                "team": str(team),
                "project": str(project),
            },
        )
        if response.status_code == 200:
            return response.json()

        descriptions = {
            401: "Unauthorized",
            404: "The UUID of the team, project, or team could not be found",
            409: "A mapping with the same team and project already exists",
        }

        description = descriptions.get(response.status_code, "Unknown error")
        raise DependencyTrackApiError(description, response)

    def delete_mapping(self, team_uuid: str, project_uuid: str) -> None:
        """
        Remove an Access Control List mapping.

        Args:
            team_uuid (str): The UUID of the team to delete the mapping for.
            project_uuid (str): The UUID of the project to delete the mapping for.

        Raises:
            DependencyTrackApiError: If an error occurs during the request and the status
            code is not 200. The exception includes a description of the error
            and the response object.
        """
        response = self.session.delete(
            f"{self.session.api_base_url}/v1/acl/mapping/team/{team_uuid}/project/{project_uuid}"
        )

        if response.status_code == 401:
            raise DependencyTrackApiError("Unauthorized", response)

        if response.status_code == 404:
            raise DependencyTrackApiError(
                "The UUID of the team or project could not be found", response
            )

        # Raise an exception for any other status code
        if response.status_code != 200:
            raise DependencyTrackApiError(
                f"Unexpected status code: {response.status_code}", response
            )

    def retrieve_projects_for_team(
        self, team_uuid: str, exclude_inactive: bool = False, only_root: bool = False
    ) -> List[str]:
        """
        Return the projects assigned to the specified team.

        Args:
            team_uuid (str): The UUID of the team to retrieve mappings for.
            exclude_inactive (bool): Optionally excludes inactive projects from being returned.
            only_root (bool): Optionally excludes children projects from being returned.

        Returns:
            list: List of project UUIDs.
        """
        params = {"excludeInactive": exclude_inactive, "onlyRoot": only_root}
        response = self.session.get(
            f"{self.session.api_base_url}/v1/acl/team/{team_uuid}", params=params
        )
        if response.status_code == 200:
            return response.json()

        descriptions = {
            401: "Unauthorized",
            404: "The UUID of the team, project, or team could not be found",
        }

        description = descriptions.get(response.status_code, "Unknown error")
        raise DependencyTrackApiError(description, response)
