import boto3
import urllib.parse
from datetime import date
import json
import os 
from botocore.exceptions import ClientError


s3_client=boto3.client('s3')
bucket_upload="s3-version-test-new"


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    l1=current(bucket,key)
    l2=existing(bucket,key)
    for i in l2:
        if i in l1:
            continue
        else:
            print(i)
    
def current(bucket,key):
    Object_version=s3_client.list_object_versions(Bucket=bucket,Prefix=key)
    data=""
    for i in Object_version['Versions']: 
	    data+=f"{i['VersionId']}\n"
    list_data_current=data.rsplit("\n")
    return list_data_current
    

def existing(bucket,key):
    try:
        key_value=os.path.splitext(key)[0]
        obj = s3_client.get_object(Bucket=bucket_upload, Key=f"{date.today()}/{bucket}/{key_value}.txt")
        list_data=obj['Body'].read().decode("utf-8")
        list_data_exist=list_data.rsplit("\n")
        return list_data_exist
    except ClientError as e:
        error_code = str(e.response['Error']['Code'])
        print(error_code)
        if error_code == 'NoSuchKey':
            key=os.path.splitext(key_value)[0]
            Object_version=s3_client.list_object_versions(Bucket=bucket,Prefix=key)
            data=""
            for i in Object_version['Versions']: 
                data+=f"{i['VersionId']}\n"
                put_object(data,bucket,key)
            obj = s3_client.get_object(Bucket=bucket_upload, Key=f"{date.today()}/{bucket}/{key}.txt")
            list_data=obj['Body'].read().decode("utf-8")
            list_data_exist=list_data.rsplit("\n")
            return list_data_exist
            
            
			    
def put_object(data,bucket,key):
    s3_client.put_object(Bucket=bucket_upload,Key=f"{date.today()}/{bucket}/{key}.txt",Body=f"{data}")
