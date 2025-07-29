from typing import Optional
from bodosdk.base import APIBaseModel
from bodosdk.models.job import JobConfig
from bodosdk.api.models.cluster import ClusterDefinition

from pydantic import Field


class CronJobApiModel(APIBaseModel):
    uuid: Optional[str]
    name: Optional[str]
    description: Optional[str]
    schedule: Optional[str]
    timezone: Optional[str]
    job_template_id: Optional[str] = Field(None, alias="jobTemplateUUID")
    max_concurrent_runs: Optional[int] = Field(None, alias="maxConcurrentRuns")
    cluster_id: Optional[str] = Field(None, alias="clusterUUID")
    cluster_config: Optional[ClusterDefinition] = Field(None, alias="clusterConfig")
    config: Optional[JobConfig] = Field(None, alias="jobConfig")


class CronJobUpdateApiModel(APIBaseModel):
    deactivate: Optional[bool]
