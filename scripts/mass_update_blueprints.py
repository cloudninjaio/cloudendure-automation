from cloudendure2 import CloudendureSDK
import csv
import json
import argparse

def main(args):
    client = CloudendureSDK(args.userApiToken)
    blueprints = []
    filename = args.filename
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

        project_id = blueprint.pop('projectId', None)
        project_name = blueprint.pop('projectName', None)
        blueprint_id = blueprint.pop('id', None)
        machine_name = blueprint.pop('machineName', None)
        original_blueprint = client.get_blueprint(projectId=project_id, blueprintId=blueprint_id)
        original_blueprint.update(blueprint)

        # Clean up unneeded attributes
        del original_blueprint['region']
        del original_blueprint["dedicatedHostIdentifier"]
        del blueprint['subnetsHostProject']

        # Configure the updated blueprint in CloudEndure
        r = client.configure_blueprint(projectId=project_id, blueprintId=blueprint_id, blueprint=original_blueprint)
        print(r)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-u', '--user-api-token', required=True, help='Cloudendure User API Token', dest='userApiToken')
    parser.add_argument('-f', '--input-file-name', required=True, help='Input CSV file', dest='filename')

    main(args=parser.parse_args())
