import logging
from datetime import date
from typing import Optional

from pydantic import Field

from bodosdk.api.base import BodoApi
from bodosdk.base import APIBaseModel
from bodosdk.exceptions import ResourceNotFound


class SdkVersionApi(BodoApi):
    def __init__(self, *args, **kwargs):
        super(SdkVersionApi, self).__init__(*args, **kwargs)
        self._resource_url = "sdk-versions"

    def check_deprecation(self, version):
        resp = self._requests.get(
            f"{self.get_resource_url('v1')}/{version}", headers=self.get_auth_header()
        )
        try:
            self.handle_error(resp)
        except ResourceNotFound:
            pass
        data = SdkVersion(**resp.json())
        if data.is_deprecated:
            msg = f"""This version of SDK is deprecated. It will be supported till {data.end_of_support}.
Please upgrade your bodosdk package. {"" if not data.notes else f"Additional Notes: {data.notes}"}"""
            print(msg)
            logging.warning(msg)


class SdkVersion(APIBaseModel):
    end_of_support: Optional[date] = Field(None, alias="endOfSupport")
    is_deprecated: Optional[bool] = Field(None, alias="isDeprecated")
    notes: Optional[str]
    sdk_version: Optional[str] = Field(None, alias="sdkVersion")
