from typing import Optional, List, Union

from pydantic import Field

from bodosdk.api.base import PageMetadata
from bodosdk.base import APIBaseModel


class AwsInstanceRoleDataAPIModel(APIBaseModel):
    role_arn: str = Field(..., alias="roleArn")


class AzureInstanceRoleDataAPIModel(APIBaseModel):
    identity: str = Field(..., alias="identity")


class InstanceRoleApiModel(APIBaseModel):
    uuid: Optional[str] = Field(None, alias="uuid")
    name: str = Field(None, alias="name")
    data: Optional[
        Union[AwsInstanceRoleDataAPIModel, AzureInstanceRoleDataAPIModel, dict]
    ] = Field(None, alias="data")
    status: Optional[str] = Field(None, alias="status")
    description: Optional[str] = Field(None, alias="description")


class InstanceRoleListAPIModel(APIBaseModel):
    data: List[InstanceRoleApiModel]
    metadata: PageMetadata
