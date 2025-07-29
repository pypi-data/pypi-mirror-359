from bodosdk.api.base import BodoApi
from bodosdk.api.models.cloud_config import (
    CloudConfigAPIModel,
    CloudConfigListAPIModel,
)
from bodosdk.interfaces import (
    ICloudConfigApi,
    ICloudConfig,
)


class CloudConfigApi(BodoApi, ICloudConfigApi):
    def __init__(self, *args, **kwargs):
        super(CloudConfigApi, self).__init__(*args, **kwargs)
        self._resource_url = "cloud-configs"

    def create(
        self,
        cloud_config: ICloudConfig,
    ) -> CloudConfigAPIModel:
        headers = {"Content-type": "application/json"}
        headers.update(self.get_auth_header())
        data = CloudConfigAPIModel(**cloud_config.dict())
        resp = self._requests.post(
            f"{self.get_resource_url('v1')}",
            data=data.json(by_alias=True, exclude_none=True),
            headers=headers,
        )
        self.handle_error(resp)
        return CloudConfigAPIModel(**resp.json())

    def update(
        self,
        cloud_config: CloudConfigAPIModel,
    ) -> CloudConfigAPIModel:
        headers = self.get_auth_header()
        data = CloudConfigAPIModel(**cloud_config.dict())
        resp = self._requests.put(
            f"{self.get_resource_url('v1')}/{cloud_config.uuid}",
            data=data.json(by_alias=True, exclude_none=True),
            headers=headers,
        )
        self.handle_error(resp)
        return CloudConfigAPIModel(**resp.json())

    def list(
        self,
        page=None,
        page_size=None,
        order=None,
        provider=None,
        status=None,
        uuids=None,
    ) -> CloudConfigListAPIModel:
        headers = self.get_auth_header()
        resp = self._requests.get(
            f"{self.get_resource_url('v1')}",
            headers=headers,
            params={"provider": provider, "status": status, "uuid": uuids},
        )
        self.handle_error(resp)
        return CloudConfigListAPIModel(**resp.json())

    def get(self, uuid) -> CloudConfigAPIModel:
        headers = self.get_auth_header()
        resp = self._requests.get(
            f"{self.get_resource_url('v1')}/{uuid}", headers=headers
        )
        self.handle_error(resp)
        return CloudConfigAPIModel(**resp.json())

    def delete(self, uuid):
        headers = self.get_auth_header()
        resp = self._requests.delete(
            f"{self.get_resource_url('v1')}/{uuid}", headers=headers
        )
        self.handle_error(resp)
