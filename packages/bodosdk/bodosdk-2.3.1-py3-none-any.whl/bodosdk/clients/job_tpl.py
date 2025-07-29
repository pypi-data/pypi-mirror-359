from typing import Dict, Union

from bodosdk.interfaces import (
    IBodoWorkspaceClient,
    IGitRepoSource,
    IS3Source,
    IWorkspaceSource,
    ICluster,
    IJobTemplateClient,
    ITextSource,
)
from bodosdk.models import JobTemplateList, JobTemplate


class JobTemplateClient(IJobTemplateClient):
    _deprecated_methods: Dict = {}

    def __init__(self, workspace_client: IBodoWorkspaceClient):
        self._workspace_client = workspace_client

    @property
    def JobTemplate(self) -> JobTemplate:
        return JobTemplate(workspace_client=self._workspace_client)

    @property
    def JobTemplateList(self) -> JobTemplateList:
        return JobTemplateList(workspace_client=self._workspace_client)

    def create(
        self,
        name: str = None,
        description: str = None,
        cluster: Union[dict, ICluster] = None,
        code_type: str = None,
        source: Union[
            dict, IS3Source, IGitRepoSource, IWorkspaceSource, ITextSource
        ] = None,
        exec_file: str = None,
        exec_text: str = None,
        args: Union[dict, str] = None,
        env_vars: dict = None,
        timeout: int = None,
        num_retries: int = None,
        delay_between_retries: int = None,
        retry_on_timeout: bool = None,
        catalog: str = None,
        store_result: bool = False,
    ) -> JobTemplate:
        """
        Create a new job template with the given parameters.

        Args:
            name (str): Name of the job template.
            description (str): Description of the job template.
            cluster (Union[dict, ICluster]): Cluster object or cluster config.
            code_type (str): Code type.
            source (Union[dict, IS3Source, IGitRepoSource, IWorkspaceSource, ITextSource]): Source object.
            exec_file (str): Exec file path.
            exec_text (str): Exec text.
            args (Union[dict, str]): Arguments.
            env_vars (dict): Environment variables.
            timeout (int): Timeout.
            num_retries (int): Number of retries.
            delay_between_retries (int): Delay between retries.
            retry_on_timeout (bool): Retry on timeout.
            catalog (str): Catalog, applicable only for SQL code type.
            store_result (bool): Whether to store the result.
        """
        if isinstance(cluster, dict):
            cluster = self._workspace_client.ClusterClient.Cluster(**cluster)
        data = {
            "name": name,
            "description": description,
            "config": {
                "type": code_type,
                "source": (
                    {"type": "SQL"} if code_type == "SQL" and exec_text else source
                ),
                "store_result": (
                    store_result if store_result is not None else code_type == "SQL"
                ),
                "exec_file": exec_file,
                "exec_text": exec_text,
                "args": args if code_type != "SQL" else None,
                "sql_query_parameters": args if code_type == "SQL" else None,
                "env_vars": env_vars,
                "timeout": timeout,
                "catalog": catalog,
            },
        }
        if (
            num_retries is not None
            or delay_between_retries is not None
            or retry_on_timeout is not None
        ):
            data["config"]["retry_strategy"] = {
                "num_retries": num_retries,
                "delay_between_retries": delay_between_retries,
                "retry_on_timeout": retry_on_timeout,
            }
        data["cluster_config"] = cluster
        return self.JobTemplate(**data)._save()

    def get(self, id: str) -> JobTemplate:
        """
        Get job template by id.

        Args:
            id (str): Job template id.

        Returns:
            JobTemplate: Job template object.
        """
        return self.JobTemplate(uuid=id)._load()

    def remove(self, id: str):
        """
        Delete job template by id.

        Args:
            id (str): Job template id.
        """
        return self.JobTemplate(uuid=id).delete()

    def list(self, filters: Dict = None) -> JobTemplateList:
        """
        List job templates with the given filters.

        Args:
            filters (Dict): Filters to apply on the list.

        Returns:
            JobTemplateList: JobTemplateList object.
        """
        return self.JobTemplateList(filters=filters)
