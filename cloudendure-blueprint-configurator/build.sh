#!/usr/bin/env bash
# Zip / Upload / Delete
#zip -r ~/Desktop/cloudendure-blueprint-configurator.zip * -x "venv/*"
#pip install cloudendure2 -t .
#pip install requests -t .
#pip install boto3 -t .
zip -r cloudendure-blueprint-configurator.zip * -x "venv/*"
aws s3 cp ./cloudendure-blueprint-configurator.zip s3://cmendez-build-artifacts/
rm cloudendure-blueprint-configurator.zip
aws lambda update-function-code --function-name  cloudendure-blueprint-configurator --s3-bucket cmendez-build-artifacts --s3-key cloudendure-blueprint-configurator.zip
