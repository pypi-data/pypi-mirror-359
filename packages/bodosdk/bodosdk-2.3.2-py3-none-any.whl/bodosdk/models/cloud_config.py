from __future__ import annotations

from enum import Enum
from typing import Optional, Union, Any, List
from uuid import UUID

from pydantic import Field

from bodosdk.base import SDKBaseModel
from bodosdk.deprecation_decorator import check_deprecation
from bodosdk.exceptions import ValidationError
from bodosdk.interfaces import (
    IBodoOrganizationClient,
    ICloudConfig,
    ICloudConfigList,
    IAzureProviderData,
    IAwsProviderData,
)


class Provider(str, Enum):
    AWS = "AWS"
    AZURE = "AZURE"

    def __str__(self):
        return str(self.value)


class AzureProviderData(SDKBaseModel, IAzureProviderData):
    provider: str = Field(Provider.AZURE, alias="provider", const=True)
    tf_backend_region: Optional[str] = Field(None, alias="tfBackendRegion")
    resource_group: Optional[str] = Field(None, alias="resourceGroup")
    subscription_id: Optional[str] = Field(None, alias="subscriptionId")
    tenant_id: Optional[str] = Field(None, alias="tenantId")
    tf_storage_account_name: Optional[str] = Field(None, alias="tfStorageAccountName")
    application_id: Optional[str] = Field(None, alias="applicationId")


class AwsProviderData(SDKBaseModel, IAwsProviderData):
    provider: str = Field(Provider.AWS, alias="provider", const=True)
    role_arn: Optional[str] = Field(None, alias="roleArn")
    tf_bucket_name: Optional[str] = Field(None, alias="tfBucketName")
    tf_backend_region: Optional[str] = Field(None, alias="tfBackendRegion")
    external_id: Optional[str] = Field(None, alias="externalId")
    account_id: Optional[str] = Field(None, alias="accountId")
    access_key_id: Optional[str] = Field(None, alias="accessKeyId")
    secret_access_key: Optional[str] = Field(None, alias="secretAccessKey")


class CloudConfig(SDKBaseModel, ICloudConfig):
    name: Optional[str]
    status: Optional[str]
    organization_uuid: Optional[str] = Field(None, alias="organizationUUID")
    custom_tags: Optional[dict] = Field(None, alias="customTags")
    uuid: Optional[Union[str, UUID]] = None
    provider: str = Field(None, alias="provider")
    provider_data: Optional[Union[AwsProviderData, AzureProviderData]]

    def __init__(self, org_client: IBodoOrganizationClient = None, **data):
        """
        Initializes a new CloudConfig model.

        Args:
            org_client: An optional client for interacting with the CloudConfig API.
            **data: Arbitrary keyword arguments representing CloudConfig properties.
        """
        super().__init__(**data)
        self._org_client = org_client

    def __call__(self, **data) -> CloudConfig:
        """
        Creates a new CloudConfig with the same CloudConfig client and provided data.

        Args:
            **data: Arbitrary keyword arguments representing CloudConfig properties.

        Returns:
            A new instance of CloudConfig.
        """
        return CloudConfig(self._org_client, **data)

    @property
    def id(self):
        return self.uuid

    @check_deprecation
    def _save(self) -> CloudConfig:
        if self._modified:
            if self.uuid:
                resp = self._org_client._cloud_config_api.update(self)
            else:
                resp = self._org_client._cloud_config_api.create(self)
            self._update(resp.dict())
            self._modified = False
        return self

    @check_deprecation
    def _load(self) -> CloudConfig:
        resp = self._org_client._cloud_config_api.get(self.uuid)
        self._update(resp.dict())
        self._modified = False
        return self

    @check_deprecation
    def delete(self):
        self._org_client._cloud_config_api.delete(self.uuid)

    def __setattr__(self, key: str, value: Any):
        if key == "provider_data" and isinstance(value, dict):
            try:
                if value["provider"] == Provider.AZURE:
                    super().__setattr__(key, AzureProviderData(**value))
                if value["provider"] == Provider.AWS:
                    super().__setattr__(key, AwsProviderData(**value))
            except ValidationError as e:
                raise ValueError(f"Invalid data for data: {e}")
        else:
            super().__setattr__(key, value)


class CloudConfigFilter(SDKBaseModel):
    ids: Optional[List[str]]
    providers: Optional[List[str]]
    statuses: Optional[List[str]]


class CloudConfigList(ICloudConfigList, SDKBaseModel):
    class Config:
        """
        Configuration for Pydantic models.
        https://docs.pydantic.dev/latest/api/config/
        """

        extra = "forbid"
        allow_population_by_field_name = True

    page: Optional[int] = Field(0, alias="page")
    page_size: Optional[int] = Field(10, alias="pageSize")
    total: Optional[int] = Field(None, alias="total")
    order: Optional[dict] = Field(default_factory=dict, alias="order")
    filters: Optional[CloudConfigFilter] = Field(None, alias="filters")

    def __init__(self, org_client: IBodoOrganizationClient = None, **data):
        super().__init__(**data)
        self._elements = []
        self._org_client = org_client

    def __call__(self, **data) -> CloudConfigList:
        cloud_config_list = CloudConfigList(self._org_client, **data)
        return cloud_config_list._load_next_page()

    def __iter__(self) -> CloudConfig:
        yield from super().__iter__()

    def _load_next_page(self) -> CloudConfigList:
        self._mutable = True
        self.page += 1
        resp = self._org_client._cloud_config_api.list(
            page=self.page,
            page_size=self.page_size,
            provider=self.filters.providers if self.filters else None,
            status=self.filters.statuses if self.filters else None,
            uuids=self.filters.ids if self.filters else None,
            order=self.order,
        )
        self._deprecated_fields.update(
            resp._deprecated_fields if isinstance(resp._deprecated_fields, dict) else {}
        )
        self._deprecated_methods.update(
            resp._deprecated_methods
            if isinstance(resp._deprecated_methods, dict)
            else {}
        )
        if self.filters:
            self.filters._deprecated_fields.update(
                self._deprecated_fields.get("filters", {}).get("_deprecated_fields", {})
            )
            self.filters._deprecated_methods.update(
                self._deprecated_methods.get("filters", {}).get(
                    "_deprecated_methods", {}
                )
            )
        for cc in resp.data:
            cloud_config = self._org_client.CloudConfig(**cc.dict())
            self._elements.append(cloud_config)
        self.total = resp.metadata.total_items
        self._mutable = False
        return self

    @check_deprecation
    def delete(self):
        for cloud_config in self:
            cloud_config.delete()
