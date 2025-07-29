from typing import Optional, Union

from bodosdk.interfaces import IBodoWorkspaceClient, ICatalogClient
from bodosdk.models import Catalog
from bodosdk.models.catalog import SnowflakeDetails, CatalogList


class CatalogClient(ICatalogClient):
    _deprecated_methods: dict

    def __init__(self, workspace_client: IBodoWorkspaceClient):
        """
        Initialize the CatalogClient with a workspace client.

        :param workspace_client: An instance of IBodoWorkspaceClient.
        """
        self._workspace_client = workspace_client

    @property
    def Catalog(self) -> Catalog:
        """
        Get the Catalog object.

        :return: An instance of Catalog.
        """
        return Catalog(self._workspace_client)

    @property
    def CatalogList(self) -> CatalogList:
        """
        Get the CatalogList object.

        :return: An instance of CatalogList.
        """
        return CatalogList(self._workspace_client)

    def list(self, filters: dict = None) -> CatalogList:
        """
        List all catalogs with optional filters.

        :param filters: A dictionary of filters to apply.
        :return: An instance of CatalogList containing the filtered catalogs.
        """
        return self.CatalogList(filters=filters)

    def get(self, id: str) -> Catalog:
        """
        Get a catalog by its ID.

        :param id: The UUID of the catalog.
        :return: An instance of Catalog.
        """
        return self.Catalog(uuid=id)._load()

    def create(
        self,
        name: str,
        catalog_type: str,
        details: Union[SnowflakeDetails, dict],
        description: Optional[str] = None,
    ):
        """
        Create a new catalog.

        :param name: The name of the catalog.
        :param catalog_type: The type of the catalog.
        :param details: The details of the catalog, either as a SnowflakeDetails instance or a dictionary.
        :param description: An optional description of the catalog.
        :return: The created catalog after saving.
        """
        if isinstance(details, dict) and catalog_type == "SNOWFLAKE":
            details = SnowflakeDetails(**details)
        catalog = self.Catalog(
            catalog_type=catalog_type,
            name=name,
            description=description,
            details=details,
        )
        return catalog._save()

    def create_snowflake_catalog(
        self,
        name: str,
        details: Union[SnowflakeDetails, dict],
        description: Optional[str] = None,
    ):
        """
        Create a new Snowflake catalog.

        :param name: The name of the Snowflake catalog.
        :param details: The details of the Snowflake catalog, either as a SnowflakeDetails instance or a dictionary.
        :param description: An optional description of the Snowflake catalog.
        :return: The created Snowflake catalog after saving.
        """
        return self.create(name, "SNOWFLAKE", details, description)

    def delete(self, id: str):
        """
        Delete a catalog by its ID.

        :param id: The UUID of the catalog to delete.
        """
        self.Catalog(uuid=id).delete()
