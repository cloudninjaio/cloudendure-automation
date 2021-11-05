# Blueprint Mass-Update
This document provides instructions on updating CloudEndure blueprints in mass.

## Prerequisites

### Python >=3.6
The script described in this guide requires python 3.6 or later. If not already installed you can follow the links below for your particular OS

- [Linux](#)
- [Windows](#)

### CloudEndure API Token
Before backing up the blueprints in your CloudEndure account you will need obtain your User API token. The process to get this token is described below.

1. Log into the CloudEndure console at [console.cloudendure.com](console.cloudendure.com)
2. Navigating to Setup & Info > OTHER SETTINGS > API Token
3. If a key was not previously generated, Click on GENERATE NEW TOKEN to generate a new API Token. If a token already exists you can use it or generate a new one.

After the prerequisites are completed you are ready to run the script as needed

## Script

### Input CSV File

The settings for each blue print mus be contained in a CSV file. The following field names are required:

>Tip: Create a backup of the existing blueprints and modify to ensure proper formating


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




### Running the Script

1. Open the your shell window and enter the following command and navigate to the folder containing the script.

2. Run the following comand to start the update
``` shell
python3 mass_update_blueprints.py --user-api-token "<<TOKEN>>" --input-file-name "ce_blueprints.csv"
```

### Code
The following pyhton script connects to CloudEndure with a user api token then updates blueprints based on the CSV input file containing the desiered blueprint settings. 

```python
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

```