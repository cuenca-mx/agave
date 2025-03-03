import json
import re

from chalice.test import Client as OriginalChaliceClient

CORE_QUEUE_REGION = 'us-east-1'


def extract_log_data(log_output: str) -> list[dict]:
    """
    Extracts JSON data from log output using a regex
    pattern and returns a list of matches.
    """
    matches = re.findall(r"(\{.*\})", log_output)
    if not matches:
        return []

    return [json.loads(match) for match in matches]


class ChaliceResponse:
    def __init__(self, chalice_response):
        self._response = chalice_response
        self._json_body = chalice_response.json_body
        self._status_code = chalice_response.status_code
        self._headers = chalice_response.headers

    def json(self):
        return self._json_body

    @property
    def status_code(self):
        return self._status_code

    @property
    def headers(self):
        return self._headers


class ChaliceClient(OriginalChaliceClient):
    def _request_with_json(
        self, method: str, url: str, **kwargs
    ) -> ChaliceResponse:
        body = json.dumps(kwargs.pop('json')) if 'json' in kwargs else None
        headers = {'Content-Type': 'application/json'}
        response = getattr(self.http, method)(
            url, body=body, headers=headers, **kwargs
        )
        return ChaliceResponse(response)

    def post(self, url: str, **kwargs) -> ChaliceResponse:
        return self._request_with_json('post', url, **kwargs)

    def get(self, url: str, **kwargs) -> ChaliceResponse:
        response = self.http.get(url, **kwargs)
        return ChaliceResponse(response)

    def patch(self, url: str, **kwargs) -> ChaliceResponse:
        return self._request_with_json('patch', url, **kwargs)

    def delete(self, url: str, **kwargs) -> ChaliceResponse:
        return self._request_with_json('delete', url, **kwargs)
