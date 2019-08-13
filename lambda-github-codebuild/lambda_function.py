import boto3
import os
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers[0].setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s'))
logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('botocore').setLevel(logging.ERROR)

def lambda_handler( event, context ):
  logger.info(event)
  s3 = boto3.resource('s3')
  bucket = s3.Bucket(event['detail']['requestParameters']['bucketName'])
  key = event['detail']['requestParameters']['key']
  sha = key.split("/")[3]
  logger.info(key)
  objs = list(bucket.objects.filter(Prefix=key))  
  bucket_name = event['detail']['requestParameters']['bucketName']
  source = (bucket_name + "/" + key)
  logger.info(source)
  if len(objs) > 0 and objs[0].key == key:
    if ".zip" in key:
      cb = boto3.client( 'codebuild' )
      build = {
        'projectName': os.environ['BUILD_PROJECT'],
        'environmentVariablesOverride': [
          {
            'name': 'GIT_COMMIT_SHA',
            'value': sha,
            'type': 'PLAINTEXT'
          }
        ],
        'sourceTypeOverride': 'S3',
        'sourceLocationOverride': source
      }
      cb.start_build( **build )
      print ("Successfully launched build.")  
      return ("Successfully launched build.")     
    else:
      print ("File uploaded was not a zip.. ignoring")
      
  else:
    print ("Couldnt detect build source in S3.")
    return ("Couldnt detect build source in S3.")
