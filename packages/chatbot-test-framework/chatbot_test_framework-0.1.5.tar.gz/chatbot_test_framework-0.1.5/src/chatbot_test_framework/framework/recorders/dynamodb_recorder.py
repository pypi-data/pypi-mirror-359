# This is the implementation for recording traces to AWS DynamoDB. It's designed to be efficient by appending each new step to a list within a single DynamoDB item, which is identified by the run_id.

import logging
from typing import Dict, Any, List

import boto3
from boto3.dynamodb.types import TypeSerializer
from botocore.exceptions import ClientError

from .base import TraceRecorder

logger = logging.getLogger(__name__)

class DynamoDBRecorder(TraceRecorder):
    """
    Records trace data to an AWS DynamoDB table.

    Each run_id corresponds to a single item in DynamoDB. Each traced step
    is appended to a list attribute within that item, which is efficient
    for both writing and reading a full trace.
    """
    def __init__(self, settings: Dict[str, Any]):
        super().__init__(settings)
        if 'table_name' not in self.settings:
            raise ValueError("DynamoDBRecorder settings must include 'table_name'.")
        
        self.table_name = self.settings['table_name']
        self.region = self.settings.get('region')
        self.run_id_key = self.settings.get('run_id_key', 'run_id') # The primary key column name
        self.trace_list_key = 'trace_steps' # The column that will store the list of steps

        try:
            self.client = boto3.client('dynamodb', region_name=self.region)
            self._serializer = TypeSerializer()
        except ImportError:
            raise ImportError("The 'boto3' package is required for DynamoDB. Please run 'pip install boto3'.")

    def record(self, trace_data: Dict[str, Any]):
        """
        Appends a trace step to a list within a DynamoDB item.

        If the item for the run_id does not exist, it is created.
        """
        run_id = trace_data.get('run_id')
        if not run_id:
            logger.error("Trace data is missing 'run_id'. Cannot record.")
            return

        # boto3's update_item requires Python types to be serialized into the
        # DynamoDB JSON format. We wrap the step data in a list for appending.
        step_as_dynamodb_json = [self._serializer.serialize(trace_data)]
        
        try:
            self.client.update_item(
                TableName=self.table_name,
                Key={self.run_id_key: {'S': run_id}},
                UpdateExpression=f"SET {self.trace_list_key} = list_append(if_not_exists({self.trace_list_key}, :empty_list), :step)",
                ExpressionAttributeValues={
                    ':step': {'L': step_as_dynamodb_json},
                    ':empty_list': {'L': []}
                }
            )
            logger.debug(f"Successfully recorded step '{trace_data.get('name')}' for run_id {run_id}.")
        except ClientError as e:
            logger.error(f"Failed to record trace to DynamoDB for run_id {run_id}: {e}")
            # Depending on the desired behavior, you might want to re-raise the exception
            # raise e

    def get_trace(self, run_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves the complete list of trace steps for a given run_id.
        """
        from boto3.dynamodb.types import TypeDeserializer
        deserializer = TypeDeserializer()

        try:
            response = self.client.get_item(
                TableName=self.table_name,
                Key={self.run_id_key: {'S': run_id}}
            )
        except ClientError as e:
            logger.error(f"Failed to get trace from DynamoDB for run_id {run_id}: {e}")
            return []

        item = response.get('Item')
        if not item or self.trace_list_key not in item:
            logger.warning(f"No trace data found in DynamoDB for run_id: {run_id}")
            return []

        # The data is stored in DynamoDB's format, so it must be deserialized
        # back into a standard Python list of dictionaries.
        dynamodb_list = item[self.trace_list_key].get('L', [])
        return [deserializer.deserialize({'M': step['M']}) for step in dynamodb_list]