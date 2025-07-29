import os

from bodosdk import _version
from bodosdk.api.auth import AuthApi
from bodosdk.api.catalog import CatalogApi
from bodosdk.api.cluster import ClusterApi
from bodosdk.api.cron_job import CronJobApi
from bodosdk.api.instance_role import InstanceRoleApi
from bodosdk.api.job import JobApi
from bodosdk.api.job_tpl import JobTplApi
from bodosdk.api.request_wrapper import RequestWrapper
from bodosdk.api.sdk import SdkVersionApi
from bodosdk.api.secret_group import SecretGroupApi
from bodosdk.api.secrets import SecretsApi
from bodosdk.api.workspace import WorkspaceApi
from bodosdk.base import APIKeys
from bodosdk.clients.catalog import CatalogClient
from bodosdk.clients.cluster import ClusterClient
from bodosdk.clients.cron_job import CronJobClient
from bodosdk.clients.instance_role import InstanceRoleClient
from bodosdk.clients.job import JobClient
from bodosdk.clients.job_tpl import JobTemplateClient
from bodosdk.clients.secret import SecretClient
from bodosdk.exceptions import APIKeysMissing
from bodosdk.interfaces import (
    IBodoWorkspaceClient,
    IWorkspace,
    IJobClient,
    IJobTemplateClient,
    IClusterClient,
    ICronJobClient,
)
from bodosdk.models.cloud_config import Provider
from bodosdk.models.workspace import Workspace


class BodoWorkspaceClient(IBodoWorkspaceClient):
    ClusterClient: IClusterClient
    JobClient: IJobClient
    JobTemplateClient: IJobTemplateClient
    CronJobClient: ICronJobClient

    def __init__(
        self,
        client_id=None,
        secret_key=None,
        api_url="https://api.bodo.ai/api",
        auth_url="https://auth.bodo.ai",
        print_logs=False,
    ):
        """
        Initialize BodoWorkspaceClient.

        Args:
            client_id (str): Client id.
            secret_key (str): Secret key.
            api_url (str): API url.
            auth_url (str): Auth url.
            print_logs (bool): Print logs

        Raises:
            APIKeysMissing: If client_id or secret_key is not passed and environment variables are not set



        """
        self._client_id = client_id
        self._secret_key = secret_key
        self._api_url = api_url
        self._auth_url = auth_url
        self._print_logs = print_logs
        self._workspace_data = None

        if not self._client_id:
            self._client_id = os.environ.get("BODO_CLIENT_ID")

        if not self._secret_key:
            self._secret_key = os.environ.get("BODO_SECRET_KEY")

        if not self._client_id or not self._secret_key:
            raise APIKeysMissing(
                "BODO_CLIENT_ID and BODO_SECRET_KEY environment variables "
                "should be set if APIKeys are not passed to BodoWorkspaceClient()"
            )

        auth = APIKeys(client_id=self._client_id, secret_key=self._secret_key)

        self._auth_api = AuthApi(auth, auth_url, RequestWrapper(print_logs))

        self._job_api = JobApi(self._auth_api, api_url, RequestWrapper(print_logs))

        self._job_tpl_api = JobTplApi(
            self._auth_api, api_url, RequestWrapper(print_logs)
        )

        self._cron_job_api = CronJobApi(
            self._auth_api, api_url, RequestWrapper(print_logs)
        )

        self._cluster_api = ClusterApi(
            self._auth_api, api_url, RequestWrapper(print_logs)
        )

        self._instance_api = InstanceRoleApi(
            self._auth_api, api_url, RequestWrapper(print_logs)
        )

        self._secret_group_api = SecretGroupApi(
            self._auth_api, api_url, RequestWrapper(print_logs)
        )

        self._secrets_api = SecretsApi(
            self._auth_api, api_url, RequestWrapper(print_logs)
        )

        self._catalog_api = CatalogApi(
            self._auth_api, api_url, RequestWrapper(print_logs)
        )

        self._workspace_api = WorkspaceApi(
            self._auth_api, api_url, RequestWrapper(print_logs)
        )

        self._sdk_api = SdkVersionApi(
            self._auth_api, api_url, RequestWrapper(print_logs)
        )

        self._request_api = RequestWrapper(print_logs)

        self._sdk_api.check_deprecation(_version.get_versions().get("version"))

        self.ClusterClient = ClusterClient(self)
        self.JobClient = JobClient(self)
        self.JobTemplateClient = JobTemplateClient(self)
        self.CronJobClient = CronJobClient(self)
        self.InstanceRoleClient = InstanceRoleClient(self)
        self.CatalogClient = CatalogClient(self)
        self.SecretClient = SecretClient(self)

        decoded_auth_token = self._auth_api.decode_token(self._auth_api.auth_token)
        self._workspace_uuid = decoded_auth_token.get("tenantId")

    @property
    def workspace_data(self) -> IWorkspace:
        """
        Get workspace data.

        Returns:
            Workspace: Workspace object.
        """
        if not self._workspace_data:
            self._workspace_data = Workspace(
                **self._workspace_api.get(self._workspace_uuid).dict()
            )
        return self._workspace_data

    @property
    def workspace_id(self) -> str:
        """
        Get workspace id.

        Returns:
            str: Workspace id.
        """
        return self._workspace_uuid

    def upload_file(self, filename: str, destination: str):
        workspace = self.workspace_data
        workspace_provider = workspace.cloud_config.provider

        url = self._workspace_api.get_upload_pre_signed_url(workspace, destination)

        headers = (
            {"x-ms-blob-type": "BlockBlob"}
            if workspace_provider == Provider.AZURE
            else {}
        )
        with open(filename, "rb") as file:
            data = file.read()
            req = self._request_api.put(url, data=data, headers=headers)
            req.raise_for_status()
