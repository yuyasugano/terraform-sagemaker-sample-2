import json
import boto3
import time
from datetime import datetime
from botocore.vendored import requests

src_path = 's3://' + "${src_path}"
role_arn = "${role_arn}"
endpoint_name = "${endpoint_name}"

def retrain_the_model():
    now_str = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S-%f')
    training_job_name = f'{endpoint_name}-{now_str}'
    sm = boto3.client('sagemaker')
    resp = sm.create_training_job(
            TrainingJobName = training_job_name, 
            AlgorithmSpecification={
                'TrainingInputMode': 'File',
                'TrainingImage': '354813040037.dkr.ecr.ap-northeast-1.amazonaws.com/sagemaker-scikit-learn:0.20.0-cpu-py3',
            }, 
            RoleArn=role_arn,
            InputDataConfig=[
                                {
                                    'ChannelName': 'train',
                                    'DataSource': {
                                        'S3DataSource': {
                                            'S3DataType': 'S3Prefix',
                                            'S3Uri': 's3://sagemaker-bucket-sample-test/sagemaker/sample/boston_housing.csv',
                                            'S3DataDistributionType': 'FullyReplicated',
                                        }
                                    },
                                },
                            ], 
            OutputDataConfig={
                                'S3OutputPath': 's3://sagemaker-bucket-sample-test/sagemaker/sample/output'
                            },
            ResourceConfig={
                            'InstanceType': 'ml.m4.xlarge',
                            'InstanceCount': 1,
                            'VolumeSizeInGB': 30,
                        }, 
            StoppingCondition={
                                'MaxRuntimeInSeconds': 86400
                            },
            HyperParameters={
                'sagemaker_program' : "scikit_learn_script.py",
                'sagemaker_region': "ap-northeast-1",
                'sagemaker_job_name': training_job_name,
                'sagemaker_submit_directory': src_path
            },
            Tags=[]
    )
    
def deploy_model(training_job_name):
    sm = boto3.client('sagemaker')
    model = sm.create_model(
        ModelName=training_job_name,
        PrimaryContainer={
            'ContainerHostname': 'model-Container',
            'Image': '354813040037.dkr.ecr.ap-northeast-1.amazonaws.com/sagemaker-scikit-learn:0.20.0-cpu-py3',
            'ModelDataUrl': f's3://sagemaker-bucket-sample-test/sagemaker/sample/output/{training_job_name}/output/model.tar.gz',
            'Environment': {
                'SAGEMAKER_PROGRAM': 'scikit_learn_gradient.py',
                'SAGEMAKER_REGION':'ap-northeast-1',
                'SAGEMAKER_SUBMIT_DIRECTORY': src_path
    
            },
        },
        ExecutionRoleArn=role_arn,
    )
    
    endpoint_config = sm.create_endpoint_config(
        EndpointConfigName=training_job_name,
        ProductionVariants=[
            {
                'VariantName': 'AllTraffic',
                'ModelName': training_job_name,
                'InitialInstanceCount': 1,
                'InstanceType': 'ml.m4.xlarge',
            },
        ],
    )
    
    sm.update_endpoint(EndpointName=endpoint_name,
                   EndpointConfigName=training_job_name)

def handle_s3_event(s3):
    print("s3=", s3)
    bucket = s3['bucket']['name']
    print("bucket: ", bucket)
    fn = s3['object']['key']
    print("fn: ", fn)
    jobid = fn.split("/")[-3]
    print("jobid=", jobid)
    return deploy_model(jobid)

def lambda_handler(event, context):
    response = event
    
    # Lambda event
    if 'Records' in event:
        for records in event['Records']:
            if 's3' in records:
                handle_s3_event(records['s3'])
    else:
        pass
    
    if 'task' in event:
        if event['task'] == 'retrain':
            # start retrain the model
            retrain_the_model()
            response = "OK"

    return {
        'statusCode': 200,
        'body': response,
    }

