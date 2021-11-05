#!/usr/bin/env bash
# Zip / Upload / Delete
#zip -r ~/Desktop/cloudendure-blueprint-sync.zip * -x "venv/*"
zip -r cloudendure-blueprint-sync.zip * -x "venv/*"
aws s3 cp ./cloudendure-blueprint-sync.zip s3://cmendez-build-artifacts/
rm cloudendure-blueprint-sync.zip
aws lambda update-function-code --function-name  cloudendure-blueprint-sync --s3-bucket cmendez-build-artifacts --s3-key cloudendure-blueprint-sync.zip
