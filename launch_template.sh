#!/bin/sh
# Launch stack from a Cloudformation template

GITHUB_TOKEN="my-personal-access-token"
LAMBDA_BUCKET="bucket-containing-lambdas"
CODEBUILD_BUCKET="bucket-name-for-codebuild"
API_NAME="my-api-name"
STACK_NAME="my-stack-name"
CODEBUILD_IMAGE="XXXXXXXXXXXXX.dkr.ecr.us-east-1.amazonaws.com/my-app:latest"
DASHBOARD_NAME="my-dashboard-name"

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
  # Launch test stack
  aws cloudformation create-stack --stack-name $STACK_NAME --template-url $GET_URL --parameters \
    ParameterKey=LambdaBucketName,ParameterValue=$LAMBDA_BUCKET \
    ParameterKey=GithubToken,ParameterValue=$GITHUB_TOKEN \
    ParameterKey=CodebuildBucketName,ParameterValue=$CODEBUILD_BUCKET \
    ParameterKey=APIName,ParameterValue=$API_NAME \
    ParameterKey=CodebuildImage,ParameterValue=$CODEBUILD_IMAGE \
    ParameterKey=CloudWatchDashboardName,ParameterValue=$DASHBOARD_NAME \
    --capabilities CAPABILITY_IAM
  echo "Stack Launched"
  # Delete template from S3
  aws s3 rm s3://$BUCKET_NAME/$TEMPLATE
  # Delete bucket
  aws s3 rb s3://$BUCKET_NAME
  # Watch build status
  echo "Checking Build Status"
  while true; do
    if aws cloudformation describe-stacks --stack-name $STACK_NAME | grep -q 'CREATE_IN_PROGRESS'; then
      echo "Status: CREATE_IN_PROGRESS"
      echo "      Please wait...      "
      echo "****************************"
      sleep 5
    elif aws cloudformation describe-stacks --stack-name $STACK_NAME | grep -q 'ROLLBACK_IN_PROGRESS'; then
      echo "Status: ROLLBACK_IN_PROGRESS"
      echo "****************************"
      aws cloudformation describe-stacks --stack-name $STACK_NAME
      break
    elif aws cloudformation describe-stacks --stack-name $STACK_NAME | grep -q 'CREATE_COMPLETE'; then
      echo "Status: CREATE_COMPLETED"
      echo "****************************"
      aws cloudformation describe-stacks --stack-name $STACK_NAME
      break
    else
      aws cloudformation describe-stacks --stack-name $STACK_NAME
      break
    fi
  done
else
  echo "Please supply a template file as paramater when executing..."
  echo "Example Usage: ./validate.sh template.yml"
fi
