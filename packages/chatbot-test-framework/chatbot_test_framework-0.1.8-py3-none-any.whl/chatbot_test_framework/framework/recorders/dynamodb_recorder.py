import logging
from typing import Dict, Any, List
from decimal import Decimal

import boto3
from boto3.dynamodb.types import TypeSerializer
from botocore.exceptions import ClientError

from .base import TraceRecorder

logger = logging.getLogger(__name__)

class DynamoDBRecorder(TraceRecorder):
    """
    Records trace data to an AWS DynamoDB table.

    Includes a sanitization method to automatically handle data types
    that are incompatible with DynamoDB, such as Python floats.
    """
    def __init__(self, settings: Dict[str, Any]):
        super().__init__(settings)
        if 'table_name' not in self.settings:
            raise ValueError("DynamoDBRecorder settings must include 'table_name'.")
        
        self.table_name = self.settings['table_name']
        self.region = self.settings.get('region')
        self.run_id_key = self.settings.get('run_id_key', 'run_id')
        self.trace_list_key = 'trace_steps'

        try:
            self.client = boto3.client('dynamodb', region_name=self.region)
            self._serializer = TypeSerializer()
        except ImportError:
            raise ImportError("The 'boto3' package is required for DynamoDB. Please run 'pip install boto3'.")

    # --- NEW: Helper method for data sanitization ---
    def _sanitize_item_for_dynamodb(self, obj: Any) -> Any:
        """
        Recursively traverses a Python object (dict, list) and converts
        any float values into high-precision Decimals. This prevents the
        "Float types are not supported" error from boto3.
        """
        if isinstance(obj, dict):
            return {k: self._sanitize_item_for_dynamodb(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize_item_for_dynamodb(elem) for elem in obj]
        elif isinstance(obj, float):
            # Convert float to string first to preserve its exact representation,
            # then convert to a Decimal.
            return Decimal(str(obj))
        return obj

    def record(self, trace_data: Dict[str, Any]):
        """
        Appends a sanitized trace step to a list within a DynamoDB item.
        """
        run_id = trace_data.get('run_id')
        if not run_id:
            logger.error("Trace data is missing 'run_id'. Cannot record.")
            return

        # --- FIX: Sanitize the data before attempting to record it ---
        logger.debug("Sanitizing trace data for DynamoDB compatibility...")
        safe_trace_data = self._sanitize_item_for_dynamodb(trace_data)
        
        # Serialize the now-safe data into the DynamoDB JSON format.
        step_as_dynamodb_json = [self._serializer.serialize(safe_trace_data)]
        
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
            logger.debug(f"Successfully recorded step '{safe_trace_data.get('name')}' for run_id {run_id}.")
        except ClientError as e:
            # The log will now show the sanitized data if an error still occurs.
            logger.error(f"Failed to record trace to DynamoDB for run_id {run_id}. Data: {safe_trace_data}", exc_info=True)
            raise e

    def get_trace(self, run_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves the complete list of trace steps for a given run_id.
        The boto3 deserializer automatically converts DynamoDB Numbers back to Decimal objects.
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

        dynamodb_list = item[self.trace_list_key].get('L', [])
        # The deserializer correctly handles the Number -> Decimal conversion on the way out.
        return [deserializer.deserialize({'M': step['M']}) for step in dynamodb_list]
