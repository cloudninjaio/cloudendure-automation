from cloudendure2 import CloudendureSDK
import csv
import json
import argparse


def main(args):
    client = CloudendureSDK(args.userApiToken)

    filename = args.filename
    blueprints = []
    projects = client.list_projects()
    for project in projects:
        project_name = project['name']
        project_id = project['id']
        print('backing up blueprints for: ' + project_name)
        for blueprint in client.list_blueprint(projectId=project_id):
            # Get machine name and project name for easy identification
            machine_name = client.get_machine(
                machineId=blueprint['machineId'],
                projectId=project_id)['sourceProperties']['name']
            blueprint.update({'machineName': machine_name})
            blueprint.update({'projectName': project_name})

            # Save lists as json formatted strings for simple import later
            blueprint['disks'] = json.dumps(blueprint['disks'])
            blueprint['securityGroupIDs'] = json.dumps(blueprint['securityGroupIDs'])
            blueprint['subnetIDs'] = json.dumps(blueprint['subnetIDs'])
            blueprint['tags'] = json.dumps(blueprint['tags'])
            blueprint['privateIPs'] = json.dumps(blueprint['privateIPs'])
            del blueprint['subnetsHostProject']
            blueprints.append(blueprint)


    # Save to a csv file
    with open(filename, 'w') as f:
        field_names = blueprints[0].keys()
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        for bp in blueprints:
            writer.writerow(bp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-u', '--user-api-token', required=True, help='Cloudendure User API Token', dest='userApiToken')
    parser.add_argument('-f', '--file-name', required=True, help='Output CSV file', dest='filename')

    main(args=parser.parse_args())




