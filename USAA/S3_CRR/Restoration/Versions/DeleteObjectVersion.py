import boto3
from datetime import date
import urllib.parse
import os 
import json

s3_client=boto3.client('s3')
bucket_upload="s3-version-test-new"




def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    bucket = event['Records'][0]['s3']['bucket']['name']
    key_data = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    key=os.path.splitext(key_data)[0]
    Object_version=s3_client.list_object_versions(Bucket=bucket,Prefix=key)
    data=""
    for i in Object_version['Versions']: 
	    data+=f"{i['VersionId']}\n"
    put_object(data,bucket,key)
	    

def put_object(data,bucket,key):
    s3_client.put_object(Bucket=bucket_upload,Key=f"{date.today()}/{bucket}/{key}.txt",Body=f"{data}")
	
