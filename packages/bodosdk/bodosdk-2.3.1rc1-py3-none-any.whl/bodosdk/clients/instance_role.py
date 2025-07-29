from __future__ import annotations

from typing import Optional, Union, Dict

from bodosdk.interfaces import IBodoWorkspaceClient, IInstanceRoleClient
from bodosdk.models.instance_role import (
    InstanceRole,
    InstanceRoleList,
    InstanceRoleFilter,
)


class InstanceRoleClient(IInstanceRoleClient):
    _deprecated_methods: dict

    def __init__(self, workspace_client: IBodoWorkspaceClient):
        """
        Initializes the InstanceRoleClient with a given workspace client.

        Args:
            workspace_client (IBodoWorkspaceClient): The workspace client to interact with the API.
        """
        self._workspace_client = workspace_client

    @property
    def InstanceRole(self) -> InstanceRole:
        """
        Get the InstanceRole object.

        Returns:
            InstanceRole: An instance of InstanceRole.
        """
        return InstanceRole(self._workspace_client)

    @property
    def InstanceRoleList(self) -> InstanceRoleList:
        """
        Get the InstanceRoleList object.

        Returns:
            InstanceRoleList: An instance of InstanceRoleList.
        """
        return InstanceRoleList(self._workspace_client)

    def list(
        self,
        filters: Optional[Union[Dict, InstanceRoleFilter]] = None,
        order: Optional[Dict] = None,
    ) -> InstanceRoleList:
        """
        List all instance roles with optional filters and order.

        Args:
            filters (Optional[Union[Dict, InstanceRoleFilter]]): A dictionary or InstanceRoleFilter
            object to apply filters.
            order (Optional[Dict]): A dictionary to specify the order of the results.

        Returns:
            InstanceRoleList: An instance of InstanceRoleList containing the filtered and ordered instance roles.
        """
        return self.InstanceRoleList(filters=filters, order=order)

    def get(self, id: str) -> InstanceRole:
        """
        Get an instance role by its ID.

        Args:
            id (str): The UUID of the instance role.

        Returns:
            InstanceRole: An instance of InstanceRole.
        """
        return self.InstanceRole(uuid=id)._load()

    def create(
        self,
        role_arn: str = None,
        identity: str = None,
        description: str = None,
        name: str = None,
    ) -> InstanceRole:
        """
        Create a new instance role.

        Args:
            role_arn (str, optional): The ARN of the role (for aws).
            identity (str, optional): The identity of the role (for azure).
            Either role_arn or identity is required.
            description (str, optional): A description of the role.
            name (str, optional): The name of the role. Defaults to None.

        Returns:
            InstanceRole: The created instance role after saving.
        """
        return self.InstanceRole(
            role_arn=role_arn, identity=identity, name=name, description=description
        )._save()

    def delete(self, id: str):
        """
        Delete an instance role by its ID.

        Args:
            id (str): The UUID of the instance role to delete.
        """
        self.InstanceRole(uuid=id).delete()
