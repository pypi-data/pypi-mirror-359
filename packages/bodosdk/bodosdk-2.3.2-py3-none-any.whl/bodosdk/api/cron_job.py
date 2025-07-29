from pydantic import validate_arguments
from typing import Optional, Dict

from bodosdk.api.base import BodoApi
from bodosdk.api.models.job import (
    DEFAULT_ORDER,
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
)
from bodosdk.api.helpers import ordering_to_query_params

# helper function to compose query string from query parameters
from bodosdk.interfaces import ICronJob, ICronJobApi
from bodosdk.api.models.cron_job import CronJobApiModel, CronJobUpdateApiModel
from bodosdk.base import PaginationOrder


class CronJobApi(BodoApi, ICronJobApi):
    def __init__(self, *args, **kwargs):
        super(CronJobApi, self).__init__(*args, **kwargs)
        self._resource_url = "cron-jobs"

    @validate_arguments
    def list_cron_jobs(
        self,
        page: int = DEFAULT_PAGE,
        size: int = DEFAULT_PAGE_SIZE,
        order: PaginationOrder = DEFAULT_ORDER,
        ordering: Optional[Dict] = None,
    ) -> dict:
        headers = self.get_auth_header()
        resource_url = f"{self.get_resource_url('v1')}"
        resp = self._requests.get(
            resource_url,
            headers=headers,
            params={
                "page": page,
                "size": size,
                "order": order,
                "ordering": ordering_to_query_params(ordering),
            },
        )
        self.handle_error(resp)
        return resp.json()

    def delete_cron_job(self, uuid):
        headers = self.get_auth_header()
        resource_url = f"{self.get_resource_url('v1')}/{uuid}"
        resp = self._requests.delete(
            resource_url,
            headers=headers,
        )
        self.handle_error(resp)
        return resp.status_code

    def create_cron_job(self, cron_job: ICronJob):
        headers = {"Content-type": "application/json"}
        headers.update(self.get_auth_header())
        cron_job_dict = cron_job.dict(by_alias=True)
        request_data = CronJobApiModel(**cron_job_dict)
        resp = self._requests.post(
            f"{self.get_resource_url('v1')}",
            data=request_data.json(by_alias=True, exclude_none=True),
            headers=headers,
        )
        self.handle_error(resp)
        return resp.json()

    def get_cron_job(self, uuid):
        headers = self.get_auth_header()
        resource_url = f"{self.get_resource_url('v1')}/{uuid}"
        resp = self._requests.get(
            resource_url,
            headers=headers,
        )
        self.handle_error(resp)
        return resp.json()

    def run_cron_job(self, uuid):
        headers = self.get_auth_header()
        resource_url = f"{self.get_resource_url('v1')}/{uuid}/run"
        resp = self._requests.post(
            resource_url,
            headers=headers,
        )
        self.handle_error(resp)
        return resp.json()

    def __update_cron_job(self, uuid, payload):
        headers = {"Content-type": "application/json"}
        headers.update(self.get_auth_header())
        resource_url = f"{self.get_resource_url('v1')}/{uuid}"
        request_data = CronJobUpdateApiModel(**payload)
        resp = self._requests.put(
            resource_url,
            data=request_data.json(by_alias=True, exclude_none=True),
            headers=headers,
        )
        self.handle_error(resp)
        return resp.status_code

    def deactivate_cron_job(self, uuid):
        return self.__update_cron_job(uuid, {"deactivate": True})

    def reactivate_cron_job(self, uuid):
        return self.__update_cron_job(uuid, {"deactivate": False})
