from __future__ import annotations
from typing import Optional, Union, List

from bodosdk.api.base import PageMetadata

from uuid import UUID

from pydantic import Field

from bodosdk.base import APIBaseModel


class AwsProviderDataAPIModel(APIBaseModel):
    provider: str = Field("AWS", alias="provider", const=True)
    tf_bucket_name: Optional[str] = Field(None, alias="tfBucketName")
    role_arn: Optional[str] = Field(None, alias="roleArn")
    external_id: Optional[str] = Field(None, alias="externalId")
    account_id: Optional[str] = Field(None, alias="accountId")
    tf_backend_region: Optional[str] = Field(None, alias="tfBackendRegion")
    secret_access_key: Optional[str] = Field(None, alias="secretAccessKey")
    access_key_id: Optional[str] = Field(None, alias="accessKeyId")


class AzureProviderDataAPIModel(APIBaseModel):
    provider: str = Field("AZURE", alias="provider", const=True)
    application_id: Optional[str] = Field(None, alias="applicationId")
    tf_backend_region: Optional[str] = Field(None, alias="tfBackendRegion")
    subscription_id: Optional[str] = Field(None, alias="subscriptionId")
    tenant_id: Optional[str] = Field(None, alias="tenantId")
    resource_group: Optional[str] = Field(None, alias="resourceGroup")


class CloudConfigAPIModel(APIBaseModel):
    uuid: Optional[Union[str, UUID]]
    status: Optional[str]
    organization_uuid: Optional[Union[str, UUID]] = Field(
        None, alias="organizationUUID"
    )
    name: Optional[str]
    provider_data: Optional[
        Union[AzureProviderDataAPIModel, AwsProviderDataAPIModel]
    ] = Field(None, alias="providerData")


class CloudConfigListAPIModel(APIBaseModel):
    data: List[CloudConfigAPIModel]
    metadata: PageMetadata
