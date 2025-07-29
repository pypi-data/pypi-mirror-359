import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry
import functools


class RequestWrapper:
    def __init__(self, print_logs=False):
        self._print_logs = print_logs
        self._session = requests.Session()
        # Retry for:
        # Request Timeout, Locked, Too Early, Too Many Requests, Conflict
        # Internal Server Error, Gateway Timeout
        retries = Retry(
            total=10,
            backoff_factor=0.1,
            status_forcelist=[408, 423, 425, 429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )

        self._session.mount("http://", HTTPAdapter(max_retries=retries))
        self._session.mount("https://", HTTPAdapter(max_retries=retries))

        # set timeout to 15s
        self._session.request = functools.partial(self._session.request, timeout=15)

    def get(self, *args, **kwargs):
        return self._request("GET", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._request("POST", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._request("DELETE", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._request("PUT", *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self._request("PATCH", *args, **kwargs)

    def _request(self, method, *args, **kwargs):
        if self._print_logs:
            if str(args[0]).endswith("identity/resources/auth/v2/api-token"):
                msg = f"{method}\n {args}"
            else:
                msg = f"{method}\n {args}\n {kwargs}"
            print(msg)
        resp = self._session.request(method, *args, **kwargs)
        if self._print_logs:
            print(f"{resp.status_code} \n {resp.content}")
        return resp
