from typing import Dict, Optional, Union

from bodosdk.interfaces import (
    IBodoWorkspaceClient,
    ICluster,
    ICronJobClient,
    IJobTemplate,
)
from bodosdk.models import CronJobList, CronJob


class CronJobClient(ICronJobClient):
    _deprecated_methods: Dict = {}

    def __init__(self, workspace_client: IBodoWorkspaceClient):
        self._workspace_client = workspace_client

    @property
    def CronJob(self) -> CronJob:
        return CronJob(workspace_client=self._workspace_client)

    @property
    def CronJobList(self) -> CronJobList:
        return CronJobList(workspace_client=self._workspace_client)

    def create(
        self,
        name: str = None,
        description: str = None,
        schedule: str = None,
        timezone: str = "Etc/GMT",
        max_concurrent_runs: int = 1,
        job_template: IJobTemplate = None,
        cluster: Union[dict, ICluster] = None,
        pause_cluster_when_finished: bool = None,
    ) -> CronJob:
        """
        Create a new cron job with the given parameters.

        Args:
            name (str): Name of the cron job.
            description (str): Description of the cron job.
            schedule (str): Schedule the cron job should follow in UNIX cron syntax.
            timezone (str): Timezone the cron job schedule should be based off of.
            max_concurrent_runs (int): Maximum number of cron job runs that can happen concurrently (max is 10).
            job_template (IJobTemplate): Job Template the cron job is derived from.
            cluster (Union[dict, ICluster]): Cluster object or cluster config.
            pause_cluster_when_finished (bool): Whether to pause the cluster when the cron job run has finished.
                                                Note this is only used when passing a non-job-dedicated cluster.
        """
        data = {
            "name": name,
            "schedule": schedule,
            "timezone": timezone,
            "description": description,
            "max_concurrent_runs": max_concurrent_runs,
            "job_template_id": job_template.id,
        }
        if cluster and isinstance(cluster, dict):
            cluster = self._workspace_client.ClusterClient.Cluster(**cluster)
        if cluster and hasattr(cluster, "id"):
            # Use existing cluster
            data["cluster_id"] = cluster.id
            if pause_cluster_when_finished is True:
                data["config"] = {
                    "pause_cluster_when_finished": pause_cluster_when_finished,
                }
        elif cluster:
            # Use job dedicated cluster
            data["cluster_config"] = cluster

        return self.CronJob(**data)._save()

    def get(self, id: str) -> CronJob:
        """
        Get cron job by id.

        Args:
            id (str): Cron Job id.

        Returns:
            CronJob: Cron Job object.
        """
        return self.CronJob(uuid=id)._load()

    def remove(self, id: str):
        """
        Delete cron job by id.

        Args:
            id (str): Cron job id.
        """
        return self.CronJob(uuid=id).delete()

    def list(self, order: Optional[Dict] = None) -> CronJobList:
        """
        List cron jobs with the given order.

        Args:
            order (Dict, optional): The order in which to list the clusters.

        Returns:
            CronJobList: CronJobList object.
        """
        return self.CronJobList(order=order)
