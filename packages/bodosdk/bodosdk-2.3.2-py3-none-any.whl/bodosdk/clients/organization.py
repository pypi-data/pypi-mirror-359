import os
from time import sleep
from typing import Optional, List, Union

from bodosdk import _version
from bodosdk.api.auth import AuthApi
from bodosdk.api.cloud_config import CloudConfigApi
from bodosdk.api.request_wrapper import RequestWrapper
from bodosdk.api.sdk import SdkVersionApi
from bodosdk.api.workspace import WorkspaceApi
from bodosdk.base import APIKeys
from bodosdk.exceptions import APIKeysMissing
from bodosdk.interfaces import (
    IBodoOrganizationClient,
)
from bodosdk.models.cloud_config import (
    CloudConfigList,
    CloudConfig,
    AwsProviderData,
    AzureProviderData,
    CloudConfigFilter,
)
from bodosdk.models.common import AWSWorkspaceData
from bodosdk.models.workspace import Workspace, WorkspaceList, WorkspaceFilter


class BodoOrganizationClient(IBodoOrganizationClient):
    def __init__(
        self,
        client_id=None,
        secret_key=None,
        api_url="https://api.bodo.ai/api",
        auth_url="https://auth.bodo.ai",
        print_logs=False,
    ):
        self._client_id = client_id
        self._secret_key = secret_key
        self._api_url = api_url
        self._auth_url = auth_url
        self._print_logs = print_logs
        self._workspace_data = None

        if not self._client_id:
            self._client_id = os.environ.get("BODO_ORG_CLIENT_ID")

        if not self._secret_key:
            self._secret_key = os.environ.get("BODO_ORG_SECRET_KEY")

        if not self._client_id or not self._secret_key:
            raise APIKeysMissing(
                "BODO_ORG_CLIENT_ID and BODO_ORG_SECRET_KEY environment variables "
                "should be set if APIKeys are not passed to BodoWorkspaceClient()"
            )

        auth = APIKeys(client_id=self._client_id, secret_key=self._secret_key)

        self._auth_api = AuthApi(auth, auth_url, RequestWrapper(print_logs))

        self._workspace_api = WorkspaceApi(
            self._auth_api, api_url, RequestWrapper(print_logs)
        )

        self._cloud_config_api = CloudConfigApi(
            self._auth_api, api_url, RequestWrapper(print_logs)
        )

        self._sdk_api = SdkVersionApi(
            self._auth_api, api_url, RequestWrapper(print_logs)
        )

        self._sdk_api.check_deprecation(_version.get_versions().get("version"))

    @property
    def Workspace(self) -> Workspace:
        return Workspace(org_client=self)

    @property
    def WorkspaceList(self) -> WorkspaceList:
        return WorkspaceList(org_client=self)

    @property
    def CloudConfig(self) -> CloudConfig:
        return CloudConfig(org_client=self)

    @property
    def CloudConfigList(self) -> CloudConfigList:
        return CloudConfigList(org_client=self)

    def create_workspace(
        self,
        name: str,
        region: str,
        cloud_config_id: str,
        vpc_id: Optional[str] = None,
        public_subnets_ids: Optional[List[str]] = None,
        private_subnets_ids: Optional[List[str]] = None,
        custom_tags: Optional[dict] = None,
        kms_key_arn: Optional[str] = None,
    ) -> Workspace:
        """
        Create a new workspace in the organization with the given parameters.

        Args:
            name (str): Name of the workspace.
            region (str): Region of the workspace.
            storage_endpoint_enabled (bool): Enable storage endpoint for the workspace.
            cloud_config_id (str): Cloud config id for the workspace.
            vpc_id (Optional[str]): VPC id for the workspace.
            public_subnets_ids (Optional(List[str])): List of public subnet ids.
            private_subnets_ids (Optional(List[str])): List of private subnet ids.
            custom_tags (Optional(dict)): Custom tags for the workspace.

        Returns:
            Workspace: Workspace object.
        """
        workspace_data = None
        if kms_key_arn:
            workspace_data = AWSWorkspaceData(kms_key_arn=kms_key_arn)

        workspace = self.Workspace(
            name=name,
            custom_tags=custom_tags,
            region=region,
            workspace_data=workspace_data,
            cloud_config=CloudConfig(uuid=cloud_config_id),
        )
        return workspace._save()

    def get_workspace(self, id) -> Workspace:
        """
        Get workspace by id.

        Args:
            id (str): Workspace id.

        Returns:
            Workspace: Workspace object.
        """
        return self.Workspace(uuid=id)._load()

    def delete_workspace(self, id) -> Workspace:
        """
        Delete workspace by id.

        Args:
            id (str): Workspace id.

        Returns:
            Workspace: Workspace object.
        """
        return self.Workspace(uuid=id).delete()

    def list_workspaces(
        self, filters: Optional[Union[WorkspaceFilter, dict]] = None
    ) -> WorkspaceList:
        """
        List workspaces in the organization.

        Args:
            filters (Optional[Union[WorkspaceFilter, dict]]): Filters to apply on the list.

        Returns:
            WorkspaceList: WorkspaceList object.
        """
        return self.WorkspaceList(filters=filters)

    def list_cloud_configs(
        self, filters: Optional[Union[dict, CloudConfigFilter]] = None
    ) -> CloudConfigList:
        """
        List cloud configs in the organization.

        Args:
            filters (Optional[Union[dict]]): Filters to apply on the list.

        Returns:
            CloudConfigList: CloudConfigList object.
        """
        return self.CloudConfigList(filters=filters)

    def create_aws_cloud_config(
        self,
        name: str,
        tf_backend_region: str,
        role_arn: Optional[str] = None,
        tf_bucket_name: Optional[str] = None,
        account_id: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        custom_tags: Optional[dict] = None,
    ) -> CloudConfig:
        """
        Create a new AWS cloud config in the organization with the given parameters.

        Args:
            name (str): Name of the cloud config.
            tf_backend_region (str): Terraform backend region.
            role_arn (Optional[str]): Role ARN.
            tf_bucket_name (Optional[str]): Terraform bucket name.
            account_id (Optional[str]): Account id.
            access_key_id (Optional[str]): Access key id.
            secret_access_key (Optional[str]): Secret access key.
            custom_tags (Optional[dict]): Custom tags for the cloud config.

        Returns:
            CloudConfig: CloudConfig object.
        """
        cloud_config = self.CloudConfig(
            name=name,
            custom_tags=custom_tags,
            provider_data=AwsProviderData(
                tf_backend_region=tf_backend_region,
                role_arn=role_arn,
                tf_bucket_name=tf_bucket_name,
                account_id=account_id,
                access_key_id=access_key_id,
                secret_access_key=secret_access_key,
            ),
        )
        cloud_config._save()
        cloud_config._load()
        # need to wait till AWS / AZURE resource be ready
        sleep(10)
        return cloud_config

    def create_azure_cloud_config(
        self,
        name: str,
        tf_backend_region: str,
        tenant_id: str,
        subscription_id: str,
        resource_group: str,
        custom_tags: Optional[dict] = None,
    ) -> CloudConfig:
        """
        Create a new Azure cloud config in the organization with the given parameters.

        Args:
            name (str): Name of the cloud config.
            tf_backend_region (str): Terraform backend region.
            tenant_id (str): Tenant id.
            subscription_id (str): Subscription id.
            resource_group (str): Resource group.
            custom_tags (Optional[dict]): Custom tags for the cloud config.

        Returns:
            CloudConfig: CloudConfig object.
        """
        cloud_config = self.CloudConfig(
            name=name,
            custom_tags=custom_tags,
            provider_data=AzureProviderData(
                tf_backend_region=tf_backend_region,
                resource_group=resource_group,
                tenant_id=tenant_id,
                subscription_id=subscription_id,
            ),
        )
        cloud_config._save()
        # need to wait till AWS / AZURE resource be ready
        sleep(20)
        return cloud_config

    def get_cloud_config(self, id) -> CloudConfig:
        """
        Get cloud config by id.

        Args:
            id (str): Cloud config id.

        Returns:
            CloudConfig: CloudConfig object.
        """
        return self.CloudConfig(uuid=id)._load()
