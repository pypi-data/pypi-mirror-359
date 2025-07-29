from typing import Optional, List

from pydantic import Field

from bodosdk.base import SDKBaseModel


class NetworkData(SDKBaseModel):
    """
    A base model for network-related data within an SDK context.

    Attributes:
        region (Optional[str]): The geographic region where the network is located.
    """

    region: Optional[str] = None


class AWSNetworkData(NetworkData):
    """
    Extends the NetworkData class to include specific properties for AWS networking.

    Attributes:
        vpc_id (Optional[str]): The ID of the AWS Virtual Private Cloud (VPC) where workspace should be created.
        public_subnets_ids (Optional[List[str]]): List of IDs for the public subnets within the AWS VPC.
        private_subnets_ids (Optional[List[str]]): List of IDs for the private subnets within the AWS VPC.
        policies_arn (Optional[List[str]]): List of AWS Resource Names (ARNs) for the policies applied to the network.
    """

    vpc_id: Optional[str] = Field(None, alias="vpcId")
    public_subnets_ids: Optional[List[str]] = Field(None, alias="publicSubnetsIds")
    private_subnets_ids: Optional[List[str]] = Field(None, alias="privateSubnetsIds")
    policies_arn: Optional[List[str]] = Field(None, alias="policyArns")


class AWSWorkspaceData(SDKBaseModel):
    """
    AWS base model for workspace related data within an SDK context.

    Attributes:
        kms_key_arn (Optional[str]): The ARN key for kms.
    """

    kms_key_arn: Optional[str] = Field(None, alias="kmsKeyArn")
