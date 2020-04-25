# CSYE7245 - Text Summarization Pipeline


[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

**Team Members**<br />
Uthsav Shetty <br />
Dileep Ravindranath Holla <br />
Swarna Ananthaswamy <br />

#### Quick Links

##### Presentations <br />
[Presentation](https://docs.google.com/document/d/1YMq5QQI7rR6wszhGaVp9iZlRndOikG59GAwNEQaf1f4/edit?usp=sharing)<br />
[Project Proposal](https://docs.google.com/document/d/1QRjOFOU81qru-dsCTIoF4OCbajMffB-vANqJgpZCjGs/edit?usp=sharing)<br />

##### Images on DockerHub.com <br />
[summary-gen-1](https://hub.docker.com/r/holladileep/summary-gen-1)<br />
[summary-gen-2](https://hub.docker.com/r/holladileep/summary-gen-2)<br />

##### Streamlit Application<br />
[TS-Pipeline | WebApp](http://18.234.153.64:8501/)<br />

##### Test Cases<br />
[Document](https://docs.google.com/document/d/1fUBjMMH8iwD7WO291wInE3U9daDpmmAYEeFQTnxxT2w/edit?usp=sharing)

---

## Table of Contents

- [Introduction](#introduction)
- [Setup](#setup)
- [TestCases](#testcases)


## Introduction

Scalable Data Pipeline for scraping/collecting articles, generating text summaries & sentiment analysis, benchmarking ROUGE scores, and deploying them on the cloud to run completely on a Serverless Infrastructure on-demand. Summarization is done using `bert` models based on the HuggingFace Pytorch transformers library to run extractive summarizations.

#### Architecture 

![alt text](https://github.com/holladileep/TS-Pipeline/blob/dev/img/CSYE7245_v2-2.png)

---


## Setup

The pipeline requires an Amazon Web Services account to deploy and run. Signup for an AWS Account [here](https://portal.aws.amazon.com/billing/signup#/start). The pipeline uses the folllowing AWS Services:

- Lambda 
- Batch
- S3
- STEP Functions
- DynamoDB
- Comprehend
- CloudWatch
- CloudTrail
- EC2
- Simple Notification Servive (SNS)

Create a new role on the AWS IAM Console and upload the policy template found at `aws_config/policy.json` on this repository to allow access to all required AWS Services

### Clone

Clone this repo to your local machine using `https://github.com/holladileep/TS-Pipeline.git`

### Setup `config.ini` 

All scripts make use of the `configparser` Python library to easily pass configuration data to running scripts/deployed packages. This allows for easy replication of code with zero modifications to Python scripts. Find configuration file can be found in `config/config.ini` directory on this repository. Modify the file with your environment variables and place it on your S3 bucket under the `config` directory like so `YourS3BucketName/config/config.ini` ; All packages and scripts are designed to read the configuration values from this path.

```
[aws]
input_dir: demo/
link_op: stage1/
stage2: stage2/
bucket: <enter your bucketname here>

[sentry]
init_params: <Enter Sentry Endpoint Here>

[slack]
webhook_url: <Enter Slack WebHook here>

[flask]
app1: <Enter endpoint for Summary-Gen-1>
app2: <Enter endpoint for Summary-Gen-1>
```

### Deploying Lambda Functions 

The pipeline extensively uses AWS Lambda Functions for Serverless Computing. All directories on this repo marked with the prefix `lambda-` are Lambda functions that have to be deployed on AWS. All functions follow a common deployment process. 

#### Deploy serverless Python code in AWS Lambda

Python Lambda is toolkit to easily package and deploy serverless code to AWS Lambda. Packaging is requried since AWS Lambda functions only ship with basic Python libraries and do not contain external libraries. Any external libraries to be used will be have to be packaged into a `.zip` and deployed to AWS Lambda. More information about Python Lambda can be found [here](https://github.com/nficano/python-lambda)

#### Setup your `config.yaml`

All `lambda-` directories contain a `config.yaml` file with the configuration information required to deploy the Lambda package to AWS. Configure the file with your access keys, secret access keys and function name before packaging and deploying the Python code. An example is as follows

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
This should create a new Lambda function on your AWS Lambda Console. Follow the same steps for all `lambda` directories on this repository to deploy packages to AWS Lambda.

### Deploying Model Summarization Flask Applications

The pipeline uses two summarizers, which are packaged as standalone Flask applications running on EC2. They can be found in the `docker-summary-gen-1-distil` and `docker-summary-gen-2-bertlarge` directories on this repo. Provision an EC2 instance on your AWS account ; Recommended EC2 instance type is `t2.xlarge`. The Flask applications accept requests on ports `5000` and `5001` respectively. 

#### DockerHub

All images are pushed to DockerHub. They can be found here:<br />
[summary-gen-1](https://hub.docker.com/r/holladileep/summary-gen-1)<br />
[summary-gen-2](https://hub.docker.com/r/holladileep/summary-gen-2)

> Pull Images

```
docker pull holladileep/summary-gen-1
docker pull holladileep/summary-gen-2
```

#### Build Docker Images manually from this repository 

> Install and run Docker on the EC2 instance 
```
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user
```
This should install Docker on the instance and start the service. Verify if the service is running by executing `docker info`

> Build Docker Images

Copy contents of `docker-summary-gen-1-distil` and `docker-summary-gen-2-bertlarge` to the instance.

*Service 1*
```
cd docker-summary-gen-1-distil
docker build -t summary-gen-1 -f Dockerfile.service ./
```
*Service 2*
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

Summarization Lambda Consumers use the created Flask URLs in the pipeline. To allow the Consumers to make an API request to the endpoints, place the API endpoints for the two running services under the keys `app1` and `app2` inside the `config.ini` file. 

### Deploying Step Workflow 

AWS Step is used the pipeline and for job orchestration. Go to AWS Console and create a new state machine. AWS Step requires the workflow to be written in [Amazon States Language](https://docs.aws.amazon.com/step-functions/latest/dg/concepts-amazon-states-language.html). 

The ASL `workflow.json` file is available on `aws_step_workflow` directory on this repository. Paste the contents of the file on State Machine Definition after creating a new State Machine on the AWS Step console.

#### Triggering the workflow

Click on the newly created Step workflow and click on New Execution

#### Auto-Trigger the workflow on placing an input file on S3 Bucket 

CloudTrail and CloudWatch are used to auto-trigger the pipeline on any `PUT` operations on the S3 Bucket. In order to set this up - create a new CloudTrail and add the source S3 Bucket. Once the trail is created, go to the CloudWatch console to create a new Rule. Provide the rule name and select the `Event Pattern` option. Select `Simple Storage Service` as the service name and `Object Level Operations` as the Event Type. Select `PutOperations` for the type of operations and specify the Bucket name. On the target screen, choose AWS Step and choose the newly created Step Workflow as the target. Deploy the created rule. 

AWS Provides a handy guide to walk through the entire process. It can be found [here](https://docs.aws.amazon.com/step-functions/latest/dg/tutorial-cloudwatch-events-s3.html#tutorial-cloudwatch-events-s3-trail)

### Deploying Streamlit App 

The pipeline uses [Streamlit](https://www.streamlit.io/) for allowing the user to upload a file with URLs, enter a single URL or quicky summarize text and sentiments for a given text input. The app directly interacts with the built components on AWS and provides a GUI to run the pipeline without the need for the end-user to manually login to AWS Account and trigger the pipeline.

The Python code for this app can be found at `streamlit_webapp/app.py`. This app is deployed on the EC2 Instance.

> Install required libraries

```
pip3 install streamlit
pip3 install boto3
pip3 install pandas
pip3 install configparser
```

> Run `app.py`

Run the WebApp by running `streamlit run app.py`. 

### Deploying the AWS Batch Docker Container

The Python script for batch scraping URLs can be found in `scrape-batch/` directory. Copy contents of the directory on your machine. 

> Create new ECR Repository

Create a new repository on ECR with the following name `ts-pipeline1`

> Login to the repository

`aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your_account_id>/ts-pipeline1`

> Build the Image

`docker build -t ts-pipeline1 .`

> Tag the image

`docker tag <your_ECR_repository_URL>/ts-pipeline1:latest`

> Push the image to ECR
`docker push <your_ECR_repository_URL>/ts-pipeline1:latest`

Create a new Compute Environment first followed by a Job Queue on the AWS Batch Console with the default configurations.
Create a Job Definition on the console and provide the ECR container ID created earlier as the input to the `container` attribute. The batch process is ready for execution

### DynamoDB

The pipleine requires three tables to be created on DynamoDB:

- `articles` Store the scraped data 
- `sentiments` Store sentiment scores
- `summary` Store generated summaries and scores

Create all tables from the DynamoDB console with `url` as the **Primary Key**. There is NO need to specify additional fields.

### Slack 

The pipeline delivers real-time notifications via Slack. All Python processes are designed to push notifications to Slack via the Web-Hook placed in the `config.ini` file. Step by step instructions to create an App and generate an incoming Web-Hook can be found [here](https://api.slack.com/messaging/webhooks).

Once the Web-Hook is generated, place the same inside the `config.ini` file for the key `webhook_url`.


## TestCases

All Test Cases have been documented [here](https://docs.google.com/document/d/1fUBjMMH8iwD7WO291wInE3U9daDpmmAYEeFQTnxxT2w/edit?usp=sharing)

Streamlit App can be accessed using this link: [TS-Pipeline | WebApp](http://18.234.153.64:8501/)

The pipeline can be tested with the sample `demo.txt` file present in the `tests` directory. Additonally any URL can be entered in the Streamlit app and results can be seen. 

Additionally, POST request can be made to the following URLs to receive a summarized response.

> Model 1
```
POST http://18.234.153.64:5001/summarize?ratio=0.2
Content-type: text/plain
Body: <enter your text here>
```
> Model 2
```
POST http://3.87.77.113:5000/summarize?ratio=0.2
Content-type: text/plain
Body: <enter your text here>
```


![ForTheBadge built-with-love](http://ForTheBadge.com/images/badges/built-with-love.svg)
