# Github - CodeBuild - CI Pipeline

This CloudFormation template will launch a continuous integration pipeline for Github using AWS Codebuild.
- New or Updated pull request webhooks trigger a status update and source download to s3
- Codebuild is run using source version detected in s3
- Build status and log URL is reported back to Github on completion

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
