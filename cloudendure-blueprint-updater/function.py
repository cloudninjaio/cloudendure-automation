import boto3
import json
import os
import logging
from boto3.dynamodb.types import TypeDeserializer

# Setup For logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# Create function to deserialize dynamo stream
def dynamo_obj_to_python_obj(dynamo_obj: dict) -> dict:
    deserializer = TypeDeserializer()
    return {
        k: deserializer.deserialize(v)
        for k, v in dynamo_obj.items()
    }


def updater(event, context):
    sqs = boto3.client('sqs')
    queue_url = os.environ['QueueURL']
    print(json.dumps(event))
    print(json.dumps(context))
    try:
        for record in event['Records']:
            logger.debug("Detected " + record['eventName'] + " event.")
            # Skip remove events in the DynamoDB stream
            if record['eventName'] == 'REMOVE':
                continue
            # Extract and format the new or changed data from the DynamoDB stream event
            blueprint = dynamo_obj_to_python_obj(record['dynamodb']['NewImage'])
            # Fix decimal conversion error from the TypeDeserializer()
            for d in blueprint['disks']:
                d['throughput'] = int(d['throughput'])
                d['iops'] = int(d['iops'])
            print(json.dumps(blueprint))
            sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(blueprint))
            return blueprint
    except Exception as e:
        logger.error(e)
        raise
