# Blueprint Backup
This document provides instruction on backing up all the blueprints in a CloudEndure account.

## Prerequisites


### Python >=3.6
The script described in this guide requires python 3.6 or later. If not already installed you can follow the links below for your particular OS

- [Linux](https://docs.python-guide.org/starting/install3/linux/)
- [Windows](https://www.python.org/downloads/)

### CloudEndure API Token
Before backing up the blueprints in your CloudEndure account you will need obtain your User API token. The process to get this token is described below.

1. Log into the CloudEndure console at [console.cloudendure.com](console.cloudendure.com)
2. Navigating to Setup & Info > OTHER SETTINGS > API Token
3. If a key was not previously generated, Click on GENERATE NEW TOKEN to generate a new API Token. If a token already exists you can use it or generate a new one.

After the prerequisites are completed you are ready to run the script as needed

## Script

### Running the Script

1. Open the your shell window and enter the following command and navigate to the folder containing the script.

2. Run the following comand to create the backup
``` shell
python3 backup_all_blueprints.py --user-api-token "<<TOKEN>>" --file-name "ce_backup.csv"
```


### Code

The following pyhton script connects to CloudEndure with a user api token then provides a CSV output of all blueprints in all projects. 

```python
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

```



### Script Output
The following fields are included in the csv for every blueprint created in the environment.

|Field        |Description                       					 |
|-------------|--------------------------------------------|
|projectName  |The name of the CloudEndure project         |
|projectId    |The id of the CloudEndure project  				 |
|iamRole      |The IAM role for the target machine (if any)|
|instanceType |The instance type of Target machine.        |
|subnetIDs    |The AWS subnet ids where the target instance will be launched|
|securityGroupIDs |The AWS security group ids to attach to the target instance on launch|
|privateIPAction | Indicates how a private IP is allocated to the target instance. This can be one of the following<br>CREATE\_NEW - Assignes a random IP within the subnet CIDR. COPY\_ORIGIN - Use the same IP as the source machine.<br>CUSTOM\_IP - Assigning a custom IP within the subnet CIDR (privateIPs)<br>USE\_NETWORK\_INTERFACE- Use an existing ENI (networkInterface)|
|privateIPs |If CUSTOM\_IP is selected in privateIPAction, the IP is specified here|
|staticIpAction |Indicates how an elastic IP is allocated to the target instance. This can be one of the following<br>EXISTING - Use an existing EIP.<br>DON’T\_CREATE - No EIP is created or attached<br>CREATE\_NEW- A new EIP is allocated and attached. |
|staticIp |If EXISTING is selected in staticIPAction, the IP is specified here |
|publicIPAction |Determins if AWS should assign public IPv4 address to the target machine. Valid options are:<br>ALLOCATE - auto-assign public IPv4 address<br>DONT\_ALLOCATE - Do not assign public address<br>AS\_SUBNET - Assignment is based on the setting configured on the subnet.|
|runAfterLaunch |power on the launched target machine after launch |
|tags |Tags that will be applied to the target machine |
|tenancy |Tenancy defines how EC2 instances are distributed across physical hardware. Valid options are:<br>SHARED (default) - Multiple AWS accounts may share the same physical hardware.<br>DEDICATED - instance runs on single-tenant hardware.<br>HOST - instance runs on a physical server with EC2 instance capacity fully dedicated to your use, an isolated server with configurations that you can control.|
|disks |Target machine disk properties. |
|region |CloudEndure Region ID |
|byolOnDedicatedInstance|specifies whether to use byol windows license if dedicated instance tenancy is selected. |
|dedicatedHostIdentifier|If HOST is selected in tenancy, the host identifier is provided here |
|forceUEFI |Force UEFI boot. Nitro based instances only |
|networkInterface       |If USE\_NETWORK\_INTERFACE is selected in privateIPAction, the ENI is specified here |
|placementGroup  |Placement Group to associate with the machine, if applicable. |

