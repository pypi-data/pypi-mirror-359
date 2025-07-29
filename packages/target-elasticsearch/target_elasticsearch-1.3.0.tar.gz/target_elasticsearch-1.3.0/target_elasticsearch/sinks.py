import elasticsearch
import jinja2

from typing import List, Dict, Optional, Union, Any, Tuple, Set

import jsonpath_ng
import singer_sdk.io_base
from elasticsearch.helpers import bulk
from singer_sdk import PluginBase
from singer_sdk.sinks import BatchSink

import datetime

from target_elasticsearch.common import (
    INDEX_FORMAT,
    SCHEME,
    HOST,
    PORT,
    USERNAME,
    PASSWORD,
    BEARER_TOKEN,
    API_KEY_ID,
    API_KEY,
    ENCODED_API_KEY,
    SSL_CA_FILE,
    INDEX_TEMPLATE_FIELDS,
    ELASTIC_YEARLY_FORMAT,
    ELASTIC_MONTHLY_FORMAT,
    ELASTIC_DAILY_FORMAT,
    METADATA_FIELDS,
    INDEX_MAPPINGS,
    NAME,
    REQUEST_TIMEOUT,
    RETRY_ON_TIMEOUT,
    to_daily,
    to_monthly,
    to_yearly,
)


def template_index(stream_name: str, index_format: str, schemas: Dict) -> str:
    """
    _index templates the input index config to be used for elasticsearch indexing
    currently it operates using current time as index.
    this may not be optimal and additional support can be added to parse @timestamp out and use it in index
    templating depending on how your elastic instance is configured.
    @param stream_name:
    @param index_format:
    @param schemas:
    @return: str
    """
    today = datetime.date.today()
    arguments = {
        **{
            "stream_name": stream_name,
            "current_timestamp_daily": today.strftime(ELASTIC_DAILY_FORMAT),
            "current_timestamp_monthly": today.strftime(ELASTIC_MONTHLY_FORMAT),
            "current_timestamp_yearly": today.strftime(ELASTIC_YEARLY_FORMAT),
            "to_daily": to_daily,
            "to_monthly": to_monthly,
            "to_yearly": to_yearly,
        },
        **schemas,
    }
    environment = jinja2.Environment()
    template = environment.from_string(index_format)
    return template.render(**arguments).replace("_", "-")


def build_fields(
    stream_name: str,
    mapping: Dict,
    record: Dict[str, Union[str, Dict[str, str], int]],
    logger: singer_sdk.io_base.logger,
) -> Dict:
    """
    build_fields parses records for supplied mapping to be used later in index templating and ecs metadata field formulation
    @param logger:
    @param stream_name:
    @param mapping: dict
    @param record:  str
    @return: dict
    """
    schemas = {}
    if stream_name in mapping:
        logger.debug(INDEX_TEMPLATE_FIELDS, ": ", mapping[stream_name])
        for k, v in mapping[stream_name].items():
            match = jsonpath_ng.parse(v).find(record)
            if len(match) == 0:
                logger.warning(
                    f"schema key {k} with json path {v} could not be found in record: {record}"
                )
                schemas[k] = v
            else:
                if len(match) < 1:
                    logger.warning(
                        f"schema key {k} with json path {v} has multiple associated fields, may cause side effects"
                    )
                schemas[k] = match[0].value
    return schemas


class ElasticSink(BatchSink):
    """ElasticSink target sink class."""

    max_size = 1000  # Max records to write in one batch

    def __init__(
        self,
        target: PluginBase,
        stream_name: str,
        schema: Dict,
        key_properties: Optional[List[str]],
    ):
        super().__init__(target, stream_name, schema, key_properties)
        self.client = self._authenticated_client()

    def build_request_body_and_distinct_indices(
        self, records: List[Dict[str, Union[str, Dict[str, str], int]]]
    ) -> Tuple[List[Dict[Union[str, Any], Union[str, Any]]], Set[str]]:
        """
        build_request_body_and_distinct_indices builds the bulk request body
        and collects all distinct indices that will be used to create indices before bulk upload.
        @param records:
        @return:
        """
        updated_records = []
        index_mapping = {}
        metadata_fields = {}
        distinct_indices = set()
        if INDEX_TEMPLATE_FIELDS in self.config:
            index_mapping = self.config[INDEX_TEMPLATE_FIELDS]
        if METADATA_FIELDS in self.config:
            metadata_fields = self.config[METADATA_FIELDS]

        for r in records:
            index = template_index(
                self.stream_name,
                self.config[INDEX_FORMAT],
                build_fields(self.stream_name, index_mapping, r, self.logger),
            )
            distinct_indices.add(index)
            updated_records.append(
                {
                    **{"_op_type": "index", "_index": index, "_source": r},
                    **build_fields(self.stream_name, metadata_fields, r, self.logger),
                }
            )

        return updated_records, distinct_indices

    def create_indices(self, indices: Set[str]) -> None:
        """
        create_indices creates elastic indices using cluster defaults or configured mappings
        @param indices: set
        """
        for index in indices:
            self.logger.info(f"index mappings: {self.config.get(INDEX_MAPPINGS, {})}")
            self.logger.debug(
                f"Creating index: {index} with mapping: {self.config.get(INDEX_MAPPINGS, {})}"
            )
            # Check if we have mapping configuration for this stream
            if self.stream_name in self.config.get(INDEX_MAPPINGS, []):
                # Use the new mapping method which handles both creation and updates
                self.create_or_update_mapping(index)
            else:
                # Fallback to original behavior for indices without mapping configuration
                try:
                    self.client.indices.create(index=index)
                except elasticsearch.exceptions.RequestError as e:
                    if e.error == "resource_already_exists_exception":
                        self.logger.debug("index already created skipping creation")
                    else:  # Other exception - raise it
                        raise e

    def build_body(
        self, records: List[Dict[str, Union[str, Dict[str, str], int]]]
    ) -> List[Dict[Union[str, Any], Union[str, Any]]]:
        """
        build_body constructs the bulk message body and creates all necessary indices if needed
        @param records: str
        @return: list[dict[Union[str, Any], Union[str, Any]]]
        """
        updated_records, distinct_indices = self.build_request_body_and_distinct_indices(records)
        self.create_indices(distinct_indices)
        return updated_records

    def _authenticated_client(self) -> elasticsearch.Elasticsearch:
        """
        _authenticated_client generates a newly authenticated elasticsearch client
        attempting to support all auth permutations and ssl concerns
        https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/connecting.html
        @return: elasticsearch.Elasticsearch
        """
        config = {}
        scheme = self.config[SCHEME]
        if SSL_CA_FILE in self.config:
            scheme = "https"
            config["ca_certs"] = self.config[SSL_CA_FILE]

        config["hosts"] = [f"{scheme}://{self.config[HOST]}:{self.config[PORT]}"]

        if REQUEST_TIMEOUT in self.config:
            config["request_timeout"] = self.config[REQUEST_TIMEOUT]

        if RETRY_ON_TIMEOUT in self.config:
            config["retry_on_timeout"] = self.config[RETRY_ON_TIMEOUT]

        if USERNAME in self.config and PASSWORD in self.config:
            config["basic_auth"] = (self.config[USERNAME], self.config[PASSWORD])
        elif API_KEY in self.config and API_KEY_ID in self.config:
            config["api_key"] = (self.config[API_KEY_ID], self.config[API_KEY])
        elif ENCODED_API_KEY in self.config:
            config["api_key"] = self.config[ENCODED_API_KEY]
        elif BEARER_TOKEN in self.config:
            config["bearer_auth"] = self.config[BEARER_TOKEN]
        else:
            self.logger.info("using default elastic search connection config")

        config["headers"] = {"user-agent": self._elasticsearch_user_agent()}

        return elasticsearch.Elasticsearch(**config)

    def write_output(self, records):
        """
        write_output creates indices, builds batch request body, and writing to elastic via bulk helper function
        # https://elasticsearch-py.readthedocs.io/en/master/helpers.html#bulk-helpers
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html
        @param records:
        """
        records = self.build_body(records)
        self.logger.debug(records)
        try:
            bulk(self.client, records)
        except elasticsearch.helpers.BulkIndexError as e:
            self.logger.error(e.errors)

    def process_batch(self, context: Dict[str, Any]) -> None:
        """
        process_batch handles batch records and overrides the default sink implementation
        @param context: dict
        """
        records = context["records"]
        self.write_output(records)
        self.tally_record_written(len(records))

    def clean_up(self) -> None:
        """
        clean_up closes the elasticsearch client
        """
        self.logger.debug(f"Cleaning up sink for {self.stream_name}")
        self.client.close()

    def _elasticsearch_user_agent(self) -> str:
        """
        Returns a user agent string for the elasticsearch client
        """
        return f"meltano-loader-elasticsearch/{PluginBase._get_package_version(NAME)}"

    def create_or_update_mapping(self, index: str) -> None:
        """
        create_or_update_mapping creates or updates the mapping for an index based on the configuration
        @param index: str - the index name to create/update mapping for
        """
        index_mappings = self.config[INDEX_MAPPINGS]

        # Check if there's a mapping for this stream
        mapping = index_mappings[self.stream_name]
        self.logger.debug(f"Creating/updating mapping for index {index} with mapping: {mapping}")

        try:
            # Check if index exists
            if self.client.indices.exists(index=index):
                # Update mapping for existing index
                self.client.indices.put_mapping(index=index, body=mapping)
                self.logger.info(f"Updated mapping for existing index: {index}")
            else:
                # Create index with mapping
                self.client.indices.create(index=index, body={"mappings": mapping})
                self.logger.info(f"Created index with mapping: {index}")

        except elasticsearch.exceptions.RequestError as e:
            if e.error == "resource_already_exists_exception":
                self.logger.debug(f"Index {index} already exists, attempting to update mapping")
                try:
                    self.client.indices.put_mapping(index=index, body=mapping)
                    self.logger.info(f"Updated mapping for index: {index}")
                except elasticsearch.exceptions.RequestError as update_error:
                    self.logger.error(f"Failed to update mapping for index {index}: {update_error}")
                    raise update_error
            else:
                self.logger.error(f"Failed to create index {index} with mapping: {e}")
                raise e
