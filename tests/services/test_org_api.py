import json

from app.services.org_api import OrgApiClient, OrgApiError

import pytest
import responses


class TestOrgApiClient:
    def test_init(self):
        client = OrgApiClient()
        assert len(client.labels) == 0
        assert client.org_api_config == {
            "url": "https://org_api_url",
        }

    def test_construct_query(self):
        client = OrgApiClient()
        query = client._construct_query("cp_id")
        result = """{
            organizations(id:"cp_id") {
                label
            }
        }"""
        assert query == result

    @responses.activate
    def test_get_label(self):
        client = OrgApiClient()
        cp_id = "cp_id"
        label = "label"
        result = f"""{{
            "data": {{
                "organizations": [
                    {{
                        "label": "{label}"
                    }}
                ]
            }}
        }}"""
        responses.add(responses.POST, "https://org_api_url", body=result)
        assert len(responses.calls) == 0
        result = client.get_label(cp_id)
        assert result == label
        assert cp_id in client.labels
        assert len(responses.calls) == 1

        # The cp_id is cached, no call to org-api needed.
        result_2 = client.get_label(cp_id)
        assert result_2 == label
        assert cp_id in client.labels
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_label_key_error(self):
        client = OrgApiClient()
        result = {"data": {"organizations": []}}
        responses.add(responses.POST, "https://org_api_url", body=json.dumps(result))
        with pytest.raises(OrgApiError):
            client.get_label("")

    @responses.activate
    def test_get_label_index_error(self):
        client = OrgApiClient()
        result = {"data": {}}
        responses.add(responses.POST, "https://org_api_url", body=json.dumps(result))
        with pytest.raises(OrgApiError):
            client.get_label("")
