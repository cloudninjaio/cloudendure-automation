from cloudendure2 import CloudendureSDK
import json
import os
import logging

# Turn on Logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def configurator(event, context):
    # Get the API key from the env vars and initiate the cloudendure sdk
    user_api_token = os.environ['userApiToken']
    client = CloudendureSDK(user_api_token)

    logger.debug("Processing " + str(len(event['Records'])) + " Blueprint(s)")
    try:
        for record in event['Records']:
            blueprint = json.loads(record['body'])
            print(json.dumps(blueprint))
            print(json.dumps(context))

            # Remove attributes that will not be accepted by the Cloudendure API
            blueprint_id = blueprint.pop('id', None)
            project_id = blueprint.pop('projectId', None)
            project_name = blueprint.pop('projectName', None)
            machine_name = blueprint.pop('machineName', None)

            logger.debug("Attempting to update blueprint for " + machine_name + " in " + project_name)
            client.configure_blueprint(projectId=project_id, blueprintId=blueprint_id, blueprint=blueprint)
            return blueprint
    except Exception as e:
        logger.error(e)
        raise
