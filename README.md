# Github - CodeBuild - CI Pipeline

This CloudFormation template will launch a continuous integration pipeline for Github using AWS Codebuild.
- New/Updated pull request webhooks from Github hit the API endpoint in AWS
- Github status is changed to pending if its a new or updated pull request, a Lambda is triggered to download the Github source to S3 bucket
- A CloudWatch rule detects the .zip download in S3 and triggers another Lambda to start Codebuild process using source
- Another CloudWatch rule detects Codebuild status on completion, and triggers a final Lambda to report back Github status with an included link to the build log.

## Architectural Overview
![alt text](/images/overview.png)

## Clone the repo

~~~
$:> git clone https://github.com/bayko/codebuild-github-ci.git
~~~

## Package each of the Lambda functions using package script

```
$:> cd codebuild-github-ci
$:> cd lambda-github-webhook
$:> sudo ./package.sh
...
```

## Create an S3 bucket and upload Lambda package zips

![alt text](/images/bucket.png)

## Push an image to ECR to use with CodeBuild

![alt text](/images/ecr.png)

## Launch the template

![alt text](/images/launch.png)

## Copy output API URL from CloudFormation

![alt text](/images/output.png)

## Create Github webhook for pull requests

![alt text](/images/webhook.png)

## Update your buildspec.yml with desired steps for codebuild 

```
version: 0.2
phases:
  install:
    commands:
       - bundle install
  pre_build:
    commands:
       - export RAILS_ENV=test
  build:
    commands:
       - bundle exec rake db:create
       - bundle exec rake db:schema:load
       - bundle exec rake db:migrate
  post_build:
    commands: 
       - bundle exec rspec
       - bundle exec cucumber

```

## Trigger a pull request and check the new CloudWatch dashboard
![alt text](/images/dashboard.png)
