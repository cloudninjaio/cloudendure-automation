import boto3
import os
import json
import logging
from cloudendure2 import CloudendureSDK

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def compare_blueprints(blueprint1, blueprint2):
    diff_count = 0
    diffs = []
    for k in blueprint1:
        if k == 'recommendedPrivateIP' or k == 'disks':
            continue
        try:
            if (blueprint1[k] != blueprint2[k]) is True:
                diff_count += 1
                diffs.append(k)
        except KeyError as k:
            logger.debug(k)
            continue

    # check disks
    for disk in blueprint1['disks']:
        if disk not in blueprint2['disks']:
            diff_count += 1
            diffs.append('disks')
    for sg in blueprint1['securityGroupIDs']:
        if sg not in blueprint2['securityGroupIDs']:
            diff_count += 1
            diffs.append('securityGroupIDs')
    # Check Subnets
    for sbnt in blueprint1['subnetIDs']:
        if sbnt not in blueprint2['subnetIDs']:
            diff_count += 1
            diffs.append('subnetIDs')
    # Check Tags
    for tag in blueprint1['tags']:
        if tag not in blueprint2['tags']:
            diff_count += 1
            diffs.append('tags')

    # Check Private IPs
    for tag in blueprint1['privateIPs']:
        if tag not in blueprint2['privateIPs']:
            diff_count += 1
            diffs.append('privateIPs')

    return {
        'diffCount': diff_count,
        'diffs': diffs
    }


def check_blueprint(event, context):
    userApiToken = os.environ['userApiToken']
    client = CloudendureSDK(userApiToken)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('cedr_automation_blueprints')
    sqs = boto3.client('sqs')
    queue_url = os.environ['QueueURL']

    # Get all the blueprints from the database
    db_blueprints = table.scan()
    for blueprint in db_blueprints['Items']:
        print(blueprint)
        blueprint_id = blueprint['id']
        project_id = blueprint['projectId']
        project_name = blueprint['projectName']
        machine_name = blueprint['machineName']
        del blueprint['region']
        ce_blueprint = client.get_blueprint(projectId=project_id, blueprintId=blueprint_id)
        del ce_blueprint['region']

        test = compare_blueprints(blueprint, ce_blueprint)
        print(test)

        # Fix decimal conversion error
        for d in blueprint['disks']:
            d['throughput'] = int(d['throughput'])
            d['iops'] = int(d['iops'])

        print(json.dumps(blueprint))
        if test['diffCount'] > 0:
            r = sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(blueprint))
            print("Sent Msg")
        else:
            msg = 'no difs found for ' + machine_name + ' in project ' + project_name
            print(msg)
            return {
                'status': 200,
                'message': msg
            }
