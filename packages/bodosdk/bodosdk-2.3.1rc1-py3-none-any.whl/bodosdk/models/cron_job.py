from __future__ import annotations

from pydantic import Field
from typing import Dict, List, Optional, Any
from datetime import date

from bodosdk.base import SDKBaseModel
from bodosdk.interfaces import IBodoWorkspaceClient, ICronJob, ICronJobList
from bodosdk.deprecation_decorator import check_deprecation
from bodosdk.models.job import JobRun, JobRunList, JobConfig
from bodosdk.models.cluster import Cluster


class CronJobList(ICronJobList, SDKBaseModel):
    """
    Represents a list of CronJobs, providing pagination and filtering capabilities.

    Attributes:
        page (Optional[int]): The current page number in the list of Cron Jobs. Defaults to 0.
        page_size (Optional[int]): The number of Cron Jobs to display per page. Defaults to 10.
        total (Optional[int]): The total number of Cron Jobs available.
        order (Optional[Dict]): A dictionary specifying the order in which Cron Jobs are sorted.
    """

    _workspace_client: IBodoWorkspaceClient
    page: Optional[int] = Field(0, alias="page")
    page_size: Optional[int] = Field(10, alias="pageSize")
    total: Optional[int] = Field(None, alias="total")
    order: Optional[Dict] = Field(default_factory=dict, alias="order")

    def __init__(self, workspace_client: IBodoWorkspaceClient = None, **data):
        super().__init__(**data)
        self._elements = []
        self._workspace_client = workspace_client

    def __call__(self, **data) -> ICronJobList:
        cron_jobs = CronJobList(self._workspace_client, **data)
        return cron_jobs._load_next_page()

    def _load_next_page(self) -> CronJobList:
        self._mutable = True
        self.page += 1
        resp = self._workspace_client._cron_job_api.list_cron_jobs(
            page=self.page, size=self.page_size, order="ASC", ordering=self.order
        )
        for resp_obj in resp["data"]:
            self._elements.append(
                self._workspace_client.CronJobClient.CronJob(**resp_obj)
            )
        self._deprecated_fields.update(
            resp.get("_deprecatedFields")
            if isinstance(resp.get("_deprecatedFields"), dict)
            else {}
        )
        self._deprecated_methods.update(
            resp.get("_deprecatedMethods")
            if isinstance(resp.get("_deprecatedMethods"), dict)
            else {}
        )
        self.total = resp["metadata"]["total_items"]
        self._mutable = False
        return self

    @check_deprecation
    def refresh(self) -> CronJobList:
        """
        Refreshes the list of cron jobs by clearing the current elements and reloading the next page of cron job data.

        This method resets the internal state of the list, including the pagination index and the elements themselves.
        It then loads the next page of data from the underlying data source to repopulate the list.
        The list is temporarily set to mutable during this process to allow updates, and then set back to
        immutable once the refresh is complete.

        Returns:
            CronJobList: The refreshed cron job list instance, with elements reloaded from
                             the next available page.
        """
        self._mutable = True
        self._index = 0
        self.page = 0
        self._elements = []
        self._load_next_page()
        self._mutable = False
        return self


class CronJob(SDKBaseModel, ICronJob):
    """
    Represents a Cron Job for creating and managing Bodo cron jobs within an SDK environment,
    encapsulating common cron job configurations.

    Attributes:
        uuid (Optional[str]): The unique identifier for the cron job.
        name (Optional[str]): The name of the cron job.
        description (Optional[str]): A brief description of the cron job.
        created_by (Optional[str]): The identifier of the user who created the cron job.
        schedule (Optional[str]): The schedule in cron syntax the cron job follows.
        timezone (Optional[str]): The timezone the schedule should follow. Default is UTC if unspecified.
        last_run_date (Optional[datetime]): The datetime of the last cron job run. Default is None at first.
        next_run_date (Optional[datetime]): The datetime of the next cron job run.
        max_concurrent_runs (Optional[int]): Number of maximum cron job runs that can occur concurrently.
        config (Optional[JobConfig]): The job configuration specifics for this cron job.
        cluster_config (Optional[Cluster]): Configuration details of the cluster on which the cron job will run.
        cluster_id (Optional[str]): UUID of the cluster to run cron jobs on.
        job_template_id (Optional[str]): UUID of the template from which this cron job was created.
        job_runs (List[JobRun]): A list of job runs associated with this cron job. Default is an empty list
                                 if none are specified.
    """

    _workspace_client = None
    uuid: Optional[str]
    name: Optional[str]
    description: Optional[str]
    created_by: Optional[str] = Field(None, alias="createdBy")
    schedule: Optional[str]
    timezone: Optional[str]
    last_run_date: Optional[date] = Field(None, alias="lastRunDate")
    next_run_date: Optional[date] = Field(None, alias="nextRunDate")
    max_concurrent_runs: Optional[int]
    config: Optional[JobConfig]
    cluster_config: Optional[Cluster] = Field(None, alias="clusterConfig")
    cluster_id: Optional[str]
    job_template_id: Optional[str]
    job_runs: List[JobRun] = Field(None, alias="jobRuns")

    @property
    def id(self):
        return self.uuid

    def __init__(self, workspace_client: IBodoWorkspaceClient = None, **data):
        super().__init__(**data)
        self._workspace_client = workspace_client

    def __call__(self, **data) -> CronJob:
        cron_job = CronJob(self._workspace_client, **data)
        if cron_job.cluster_config and isinstance(cron_job.cluster_config, dict):
            cron_job.cluster_config = self._workspace_client.ClusterClient.Cluster(
                **cron_job.cluster_config
            )
        if cron_job.config and isinstance(cron_job.config, dict):
            cron_job.config = JobConfig(**cron_job.config)
        return cron_job

    def __setattr__(self, key: str, value: Any):
        if key == "cluster_config" and isinstance(value, dict):
            value = self._workspace_client.ClusterClient.Cluster(**value)
        elif key == "config" and isinstance(value, dict):
            value = JobConfig(**value)
        super().__setattr__(key, value)

    @check_deprecation
    def run(self):
        """
        Runs an instance of the cron job manually. This does not replace any scheduled job runs, but could delay
        them based on your maximum concurrent run limit.

        Returns:
            IJobRun: The job run instance.
        """
        return self._workspace_client._cron_job_api.run_cron_job(self.uuid)

    @check_deprecation
    def delete(self):
        """
        Deletes the cron job.
        """
        return self._workspace_client._cron_job_api.delete_cron_job(self.uuid)

    @check_deprecation
    def deactivate(self):
        """
        Deactivates a cron job. All cron jobs that were scheduled before time of deactivation
        or during deactivation period will not run.

        Returns:
            A status code on if the deactivation was successful or not.
        """
        return self._workspace_client._cron_job_api.deactivate_cron_job(self.uuid)

    @check_deprecation
    def reactivate(self):
        """
        Reactivates a cron job. All cron job runs scheduled after time of reactivation will
        be scheduled like normal.

        Returns:
            A status code on if the deactivation was successful or not.
        """
        return self._workspace_client._cron_job_api.reactivate_cron_job(self.uuid)

    @check_deprecation
    def history(self):
        """
        Get the history of previously scheduled and manual job runs of this cron job.

        Returns:
            IJobRunList: A job run list.
        """
        return JobRunList(
            workspace_client=self._workspace_client,
            filters={"cron_job_ids": [self.uuid]},
        )

    @check_deprecation
    def _save(self) -> CronJob:
        """
        Saves the cron job. This can only create a new cron job.

        Returns:
            Cron Job: The new cron job.
        """
        if self._modified:
            resp = self._workspace_client._cron_job_api.create_cron_job(self)
            self._update(resp)
            self._modified = False
        return self

    @check_deprecation
    def _load(self) -> CronJob:
        """
        Loads the cron job from the API.

        Returns:
            CronJob: The loaded cron job instance.
        """
        resp = self._workspace_client._cron_job_api.get_cron_job(self.uuid)
        self._update(resp)
        return self


from bodosdk.models import Cluster  # noqa

CronJob.update_forward_refs()
