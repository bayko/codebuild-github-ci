import boto3
from botocore.vendored import requests
import logging
import base64
import os
import shutil
from zipfile import ZipFile
from cStringIO import StringIO
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers[0].setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s'))
logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('botocore').setLevel(logging.ERROR)

s3_client = boto3.client('s3')

def get_members(zip):
    parts = []
    for name in zip.namelist():
        if not name.endswith('/'):
            parts.append(name.split('/')[:-1])
    prefix = os.path.commonprefix(parts)
    if prefix:        
        prefix = '/'.join(prefix) + '/'
    offset = len(prefix)
    for zipinfo in zip.infolist():
        name = zipinfo.filename
        if len(name) > offset:
            zipinfo.filename = name[offset:]
            yield zipinfo

def lambda_handler(event, context):
    logger.info('Event %s', event)
    OAUTH_token = os.environ['GITHUB_TOKEN']
    OutputBucket = os.environ['OUTPUT_BUCKET']
    headers = {}
    repo = event['repo']
    owner = event['owner']
    sha = event['sha']
    archive_url = event['archive_url']
    owner = event['owner']
    name = event['name']
    branch_name = event['branch_name']
    verify = False
    archive_url = archive_url.replace('{archive_format}', 'zipball').replace('{/ref}', '/' + branch_name)
    archive_url = archive_url+'?access_token='+OAUTH_token
    requests.packages.urllib3.disable_warnings()
    s3_archive_file = "%s/%s/%s/%s/%s.zip" % (owner, name, branch_name, sha, name)
    logger.info('Downloading archive from %s' % archive_url)
    r = requests.get(archive_url, verify=verify, headers=headers)
    f = StringIO(r.content)
    zip = ZipFile(f)
    path = '/tmp/code'
    zipped_code = '/tmp/zipped_code'
    try:
        shutil.rmtree(path)
        os.remove(zipped_code + '.zip')
    except:
        pass
    finally:
        os.makedirs(path)
    zip.extractall(path, get_members(zip))
    shutil.make_archive(zipped_code, 'zip', path)
    logger.info("Uploading zip to S3://%s/%s" % (OutputBucket, s3_archive_file))
    s3_client.upload_file(zipped_code + '.zip', OutputBucket, s3_archive_file)
    logger.info('Upload Complete')
