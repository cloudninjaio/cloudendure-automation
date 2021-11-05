#!/usr/bin/env bash
#Script Variables
s3bucketName="my-artifacts"
s3ObjectPrefix="cloudendure/"
CloudEndureUserApiToken=""

# Zip All the functions prior to s3 upload
zip -r cloudendure-blueprint-configurator.zip cloudendure-blueprint-configurator/* -x "cloudendure-blueprint-configurator/venv/*"
zip -r cloudendure-blueprint-updater.zip cloudendure-blueprint-updater/* -x "cloudendure-blueprint-updater/venv/*"
zip -r cloudendure-blueprint-sync.zip cloudendure-blueprint-sync/* -x "cloudendure-blueprint-sync/venv/*"
# Upload Functions
aws s3 cp ./"cloudendure-blueprint-configurator.zip" "s3://${s3bucketName}/${s3ObjectPrefix}"
aws s3 cp ./"cloudendure-blueprint-updater.zip" "s3://${s3bucketName}/${s3ObjectPrefix}"
aws s3 cp ./"cloudendure-blueprint-sync.zip" "s3://${s3bucketName}/${s3ObjectPrefix}"

# Upload CloudFormation Templates
aws s3 cp ./blueprint_functions.json "s3://${s3bucketName}/${s3ObjectPrefix}"
aws s3 cp ./dynamodb.json "s3://${s3bucketName}/${s3ObjectPrefix}"
aws s3 cp ./management_iam.json "s3://${s3bucketName}/${s3ObjectPrefix}"
aws s3 cp ./automation_solution.json "s3://${s3bucketName}/${s3ObjectPrefix}"

# Create the Cloud formation stack
aws cloudformation create-stack \
--stack-name CeBlueprintAutomation \
--template-body "file://automation_solution.json" \
--capabilities CAPABILITY_NAMED_IAM \
--parameters ParameterKey=DynamoDbTemplateURL,ParameterValue="https://s3.amazonaws.com/${s3bucketName}/${s3ObjectPrefix}dynamodb.json" \
ParameterKey=FunctionTemplateURL,ParameterValue="https://s3.amazonaws.com/${s3bucketName}/${s3ObjectPrefix}blueprint_functions.json" \
ParameterKey=IamManagementTemplateURL,ParameterValue="https://s3.amazonaws.com/${s3bucketName}/${s3ObjectPrefix}management_iam.json" \
ParameterKey=userApiToken,ParameterValue="${CloudEndureUserApiToken}" \
ParameterKey=S3Bucket,ParameterValue="${s3bucketName}" \
ParameterKey=S3Prefix,ParameterValue="${s3ObjectPrefix}"

# Cleanup zip files
rm cloudendure-blueprint-configurator.zip
rm cloudendure-blueprint-updater.zip
rm cloudendure-blueprint-sync.zip
