#!/bin/bash

set -e

if command -v python3 > /dev/null 2>&1; then

  echo ""
  echo "Creating Lambda Deployment Package..."
  echo ""

  # Remove old export directory if it exists
  EXPORT_DIR="./lambda/export"
  if [ -d "$EXPORT_DIR" ]
  then
    rm -rf $EXPORT_DIR
  fi
  # Make new export directory
  mkdir -p ./export
  # Copy our code
  cp ./lambda_function.py ./export
  # Install our modules
  pip3 install -r ./requirements.txt -t ./export
  # Create ZIP file
  cd ./export
  zip -r ../../ci-github-status.zip .
  cd -
  # Clean Up export
  rm -rf ./export


else

    echo ""
    echo "Error:"
    echo "  python3 is required for this Lambda function."
    echo "  Please install python3 then try again."
    echo ""
    exit 1

fi
