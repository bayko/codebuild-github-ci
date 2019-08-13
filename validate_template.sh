#!/bin/sh
# Run a validation check on a Cloudformation template
TEMPLATE=$1
# Check for param
if [ -n "$1" ]; then
  # Generate random bucket name
  BUCKET_NAME=$(cat /dev/urandom | tr -dc 'a-z' | fold -w 10 | head -n 1)
  # Create Bucket
  aws s3 mb s3://$BUCKET_NAME/
  # Copy template to s3
  aws s3 cp "$TEMPLATE" s3://$BUCKET_NAME/
  echo "Upload Complete"
  # Create object URL
  GET_URL="$(aws s3 presign s3://$BUCKET_NAME/$TEMPLATE)"
  # Run validation
  aws cloudformation validate-template --template-url $GET_URL
  echo "Validation Complete"
  # Delete template from S3
  aws s3 rm s3://$BUCKET_NAME/$TEMPLATE
  # Delete bucket
  aws s3 rb s3://$BUCKET_NAME
else
  echo "Please supply a template file as paramater when executing..."
  echo "Example Usage: ./validate.sh template.yml"
fi