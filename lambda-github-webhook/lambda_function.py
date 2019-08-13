import boto3
import logging
import os
import json
from github import Github

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers[0].setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s'))
logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('botocore').setLevel(logging.ERROR)

lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
  logger.info('Event %s', event)
  jsonbody = json.loads(event['body'])
  logger.info(jsonbody)
  if event['headers']['X-GitHub-Event'] == 'ping':
    return {
      'statusCode': 200,
      'body': 'It Works!'
    }
  if event['headers']['X-GitHub-Event'] == 'pull_request' and jsonbody['action'] in ['synchronize', 'opened', 'reopened']:
    repo = jsonbody['pull_request']['base']['repo']['name']
    owner = jsonbody['pull_request']['base']['repo']['owner']['login']
    sha = jsonbody['pull_request']['head']['sha']
    archive_url = jsonbody['repository']['archive_url']
    owner = jsonbody['repository']['owner']['login']
    name = jsonbody['repository']['name']
    branch_name = jsonbody['pull_request']['head']['ref'] 
    g = Github(os.environ['GITHUB_TOKEN'])
    org = g.get_organization(owner)
    repository = org.get_repo(repo)
    repository.get_commit(sha=sha).create_status(
      state="pending",
      description="Codebuild is starting.. Please Wait",
      context="ci/Codebuild"
    )
    logger.info(repo)
    logger.info(owner)
    logger.info(sha)
    logger.info(archive_url)
    logger.info(owner)
    logger.info(name)
    logger.info(branch_name)
    payload = {}
    payload['repo']        = repo
    payload['owner']       = owner
    payload['sha']         = sha
    payload['archive_url'] = archive_url
    payload['owner']       = owner
    payload['name']        = name
    payload['branch_name'] = branch_name
    try:
      lambda_client.invoke(
        FunctionName=os.environ['TARGET_LAMBDA'],
        InvocationType='Event',
        Payload=json.dumps(payload)
      )
    except Exception as e:
      raise e

    return {
      'statusCode': 200,
      'body': 'Source Download Triggered'
    }
  else:
    return {
      'statusCode': 200,
      'body': "Skipping Non-Pull Request Webhook"
    }
