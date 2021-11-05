from cloudendure2 import CloudendureSDK
import boto3
import csv
import json

filename = "test.csv"
userApiToken = ""
client = CloudendureSDK(userApiToken)

blueprints = []
with open(filename, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        blueprints.append(row)
# Convert from json strings to list
for blueprint in blueprints:
    blueprint['disks'] = json.loads(blueprint['disks'])
    blueprint['securityGroupIDs'] = json.loads(blueprint['securityGroupIDs'])
    blueprint['subnetIDs'] = json.loads(blueprint['subnetIDs'])
    blueprint['tags'] = json.loads(blueprint['tags'])
    blueprint['privateIPs'] = json.loads(blueprint['privateIPs'])

    # Fix Bool
    if blueprint['byolOnDedicatedInstance'] == "TRUE":
        blueprint['byolOnDedicatedInstance'] = bool(1)
    else:
        blueprint['byolOnDedicatedInstance'] = bool(0)

    if blueprint['forceUEFI'] == "TRUE":
        blueprint['forceUEFI'] = bool(1)
    else:
        blueprint['forceUEFI'] = bool(0)

    if blueprint['runAfterLaunch'] == "TRUE":
        blueprint['runAfterLaunch'] = bool(1)
    else:
        blueprint['runAfterLaunch'] = bool(0)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('cedr_automation_blueprints')
    table.put_item(Item=blueprint)






