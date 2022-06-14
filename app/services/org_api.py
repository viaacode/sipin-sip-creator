import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from viaa.configuration import ConfigParser
from viaa.observability import logging


class OrgApiError(Exception):
    pass


class OrgApiClient:
    def __init__(self):
        configParser = ConfigParser()
        self.log = logging.get_logger(__name__, config=configParser)
        self.org_api_config = configParser.app_cfg["org_api"]
        self.labels = {}

    def _construct_query(self, cp_id: str):
        """Construct the Graphql query to retrieve the label defined in the MAM
        Args:
            cp_id: The cp-id for which to retrieve the label.
        Returns:
            The graphql query.
        """
        query = f"""{{
            organizations(id:"{cp_id}") {{
                label
            }}
        }}"""
        return query

    def get_label(self, cp_id: str) -> str:
        """Retrieve the label of the CP.
        The information is stored in a knowledge graph queryable via GraphQL.
        The label will be cached to minimize the amount of requests to the knowledge
        graph.
        Args:
            cp_id: The cp-id for which to retrieve the label.
        Returns:
            The label for the given cp-id.
        Raises:
            OrgApiError: When the result is not parsable.
        """
        if cp_id in self.labels:
            return self.labels[cp_id]

        query = self._construct_query(cp_id)
        data_payload = {"query": query}

        retry_strategy = Retry(
            total=10,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["POST"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        with requests.Session() as session:
            session.mount("https://", adapter)
            session.mount("http://", adapter)
            response = session.post(self.org_api_config["url"], json=data_payload)
        try:
            label = response.json()["data"]["organizations"][0]["label"]
        except (KeyError, IndexError) as e:
            raise OrgApiError(f"Could not fetch the label for CP ID '{cp_id}': {e}")
        self.labels[cp_id] = label
        return label
