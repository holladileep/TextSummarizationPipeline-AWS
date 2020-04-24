# CSYE7245 - Text Summarization Pipeline

Pipeline to summarize news article(s)

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

**Course Documents**

[Presentation](https://docs.google.com/document/d/1YMq5QQI7rR6wszhGaVp9iZlRndOikG59GAwNEQaf1f4/edit?usp=sharing)

[Project Proposal](https://docs.google.com/document/d/1YMq5QQI7rR6wszhGaVp9iZlRndOikG59GAwNEQaf1f4/edit?usp=sharing)

---

## Table of Contents

- [Introduction](#introduction)
- [Setup](#setup)

---

## Introduction

---


## Setup

- The pipeline requires an Amazon Web Services account to deploy and run

### Clone

- Clone this repo to your local machine using `https://github.com/holladileep/TS-Pipeline.git`

### AWS Account Setup

Signup for an AWS Account [here](https://portal.aws.amazon.com/billing/signup#/start). The pipeline uses the folllowing AWS Services:

- Lambda 
- Batch
- S3
- STEP Functions
- Comprehend
- CloudWatch
- CloudTrail
- EC2
- Simple Notification Servive (SNS)

Create a new role on the AWS IAM Console and upload the policy template found at `aws_config/policy.json` on this repository to allow access to all required AWS Services

### Deploying Lambda Functions 

The pipeline extensively uses AWS Lambda Functions for Serverless Computing. All directories on this repo marked with the prefix `lambda-` are Lambda functions that have to be deployed on AWS. All functions follow a common deployment process. 

#### Deploy serverless Python code in AWS Lambda

Python Lambda is toolkit to easily package and deploy serverless code to AWS Lambda. Packaging is requried since AWS Lambda functions only ship with basic Python libraries and do not contain external libraries. Any external libraries to be used will be have to be packaged into a `.zip` and deployed to AWS Lambda. More information about Python Lambda can be found [here](https://github.com/nficano/python-lambda)

#### Setup your `config.yaml`

All `lambda-` directory contain a `config.yaml` file with the configuration information required to deploy the Lambda package to AWS. Configure the file with your access keys, secret access keys and function name before packaging and deploying the Python code. An example is as follows

```
region: us-east-1

function_name: Lambda_Function_1
handler: service.handler
description: Deployed lambda Function
runtime: python3.7
role: <Enter the role name created earlier>

# if access key and secret are left blank, boto will use the credentials
# defined in the [default] section of ~/.aws/credentials.
aws_access_key_id: <Enter your Access Keys>
aws_secret_access_key: <Enter your Secret Access Keys>

timeout: 15
memory_size: 512

environment_variables:
    ip_bucket: <enter_your_S3_Bucket>

# Build options
build:
  source_directories: lib
```

> Create a Virtual Environment 
```
pipenv shell --python 3.7
pip3 install python-lambda
```
All package dependencies are available in the respective `lambda-` directories on this repository 

> Install all Python dependencies  

```
pip3 install -r requirements.txt
```
> Initiate Lambda Deployement 
```
lambda init
```
This will create the following files: `event.json`,` __init__.py`, `service.py`, and `config.yaml`
Replace the created `service.py` and `config.yaml` files with the `service.py` and `config.yaml` files in the respective `lambda-` directory on this repository.

> Package and Deploy Lmabda function

```
lambda deploy
```
This should create a new Lambda function on your AWS Lambda Console. Follow the same steps for all `lambda` directories on this repository. 

### Deploying Model Summarization Flask Applications

The pipeline uses two summarizers, which are packaged as standalone Flask applications running on EC2. They can be found in the `docker-summary-gen-1-distil` and `docker-summary-gen-2-bertlarge` directories on this repo. Provision an EC2 instance on your AWS account ; Recommended EC2 instance type is `t2.xlarge`. The Flask applications accept requests on ports `5000` and `5001` respectively. 

> Install and run Docker on the EC2 instance 
```
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user
```
This should install Docker on the instance and start the service. Verify if the service is running by executing `docker info`

> Build Docker Images

Copy contents of `docker-summary-gen-1-distil` and `docker-summary-gen-2-bertlarge` to the instance.

Service 1 
```
cd docker-summary-gen-1-distil
docker build -t summary-gen-1 -f Dockerfile.service ./
```
Service 2 
```
cd docker-summary-gen-2-bertlarge
docker build -t summary-gen-1 -f Dockerfile.service ./
```
Verify that the images are built by running `docker images`

> Run the images and start the service
```
docker run --rm -it -p 5001:5001 summary-gen-2:latest -model bert-large-uncased
docker run --rm -it -p 5000:5000 summary-gen-1:latest -model distilbert-base-uncased
```
The Flask Application should now be running on `localhost:5000` and `localhost:5001` respectively.

## License

