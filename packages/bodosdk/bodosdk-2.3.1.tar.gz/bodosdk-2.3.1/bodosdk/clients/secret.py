from typing import Union
from bodosdk.interfaces import IBodoWorkspaceClient, ISecretClient
from bodosdk.models.secret import (
    SecretGroup,
    SecretGroupList,
    Secret,
    SecretList,
    SecretGroupFilter,
    SecretFilter,
)


class SecretClient(ISecretClient):
    """
    A client for managing secrets and secret groups within a workspace.
    """

    def __init__(self, workspace_client: IBodoWorkspaceClient):
        """
        Initialize the SecretClient with a workspace client.

        :param workspace_client: The workspace client used to interact with the backend.
        """
        self._workspace_client = workspace_client

    @property
    def SecretGroup(self) -> SecretGroup:
        """
        Create a SecretGroup instance.

        :return: An instance of SecretGroup.
        """
        return SecretGroup(self._workspace_client)

    @property
    def SecretGroupList(self) -> SecretGroupList:
        """
        Create a SecretGroupList instance.

        :return: An instance of SecretGroupList.
        """
        return SecretGroupList(self._workspace_client)

    @property
    def Secret(self) -> Secret:
        """
        Create a Secret instance.

        :return: An instance of Secret.
        """
        return Secret(self._workspace_client)

    @property
    def SecretList(self) -> SecretList:
        """
        Create a SecretList instance.

        :return: An instance of SecretList.
        """
        return SecretList(self._workspace_client)

    def list_secret_groups(
        self, filters: Union[dict, SecretGroupFilter] = None
    ) -> SecretGroupList:
        """
        List all secret groups, optionally filtered by provided criteria.

        :param filters: Optional filters for listing secret groups.
        :return: A SecretGroupList instance containing the filtered secret groups.
        """
        return self.SecretGroupList(filters=filters)

    def list_secrets(self, filters: Union[dict, SecretFilter] = None) -> SecretList:
        """
        List all secrets, optionally filtered by provided criteria.

        :param filters: Optional filters for listing secrets.
        :return: A SecretList instance containing the filtered secrets.
        """
        return self.SecretList(filters=filters)

    def get_secret(
        self,
        id: str,
    ) -> Secret:
        """
        Retrieve a secret by its ID.

        :param id: The ID of the secret to retrieve.
        :return: An instance of Secret.
        """
        return self.Secret(uuid=id)._load()

    def create_secret(
        self,
        name: str,
        secret_type: str,
        data: dict,
        secret_group: SecretGroup,
    ) -> Secret:
        """
        Create a new secret.

        :param name: The name of the secret.
        :param secret_type: The type of the secret.
        :param data: The data contained in the secret.
        :param secret_group: The secret group to which the secret belongs.
        :return: The created Secret instance.
        """
        secret = self.Secret(
            secret_type=secret_type,
            name=name,
            data=data,
            secret_group=secret_group,
        )
        return secret._save()

    def delete_secret(self, id: str):
        """
        Delete a secret by its ID.

        :param id: The ID of the secret to delete.
        """
        self.Secret(uuid=id).delete()

    def create_secret_group(
        self,
        name: str,
        description: str,
    ) -> SecretGroup:
        """
        Create a new secret group.

        :param name: The name of the secret group.
        :param description: The description of the secret group.
        :return: The created SecretGroup instance.
        """
        sg = self.SecretGroup(
            name=name,
            description=description,
        )
        return sg._save()

    def delete_secret_group(self, name: str):
        """
        Delete a secret group by its name.

        :param name: The name of the secret group to delete.
        """
        self.SecretGroup(name=name).delete()
