import boto3
from github3 import login
import os
import json
import sys
import logging

codebuild = boto3.client('codebuild')

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers[0].setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s'))
logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('botocore').setLevel(logging.ERROR)

def lambda_handler(event, context):
  if event:
    logger.info(event)
    build_id = event['detail']['build-id'].split('/')[1]
    status = event['detail']['build-status']
    state = {
      "FAILED": 'failure',
      "STOPPED": 'error',
      "SUCCEEDED": 'success'
    }
    build = codebuild.batch_get_builds(
      ids=[build_id]
    )
    logger.info(build)
    owner = build['builds'][0]['source']['location'].split('/')[1]
    project = build['builds'][0]['source']['location'].split('/')[2]
    sha = event['detail']['additional-information']['environment']['environment-variables'][0]['value']
    logger.info('owner: ' + owner)
    logger.info('project: ' + project)
    logger.info('sha: ' + sha)
    token = os.environ['GITHUB_TOKEN']
    gh = login(token=token)
    repository = gh.repository(owner, project)
    result = repository.create_status(
      sha=sha,
      state=state[status],
      target_url="https://us-east-1.console.aws.amazon.com/codebuild/home?region=us-east-1#/builds/" + build_id + "/view/new",
      description="Build was a " + state[status] + ".",
      context="ci/Codebuild"
    )
    return {
      'statusCode': 200,
      'body': "Created Status '" + state[status] + "' - ID: " + str(result.id)
    }
  else:
    return {
      'statusCode': 400,
      'body': 'unknown command'
    }
