import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone

s3_client = boto3.client('s3')
now = datetime.now(timezone.utc)


source_bucket="usaa-cybervault-source-test"
key="abc.txt"
time=30

response=s3_client.list_object_versions(Bucket=source_bucket,Prefix=key)


def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    final_minutes = (days*1440)+(seconds/60)
    return final_minutes


for i in response['Versions']:
	version_time=i['LastModified']
	required_time=now - version_time
	time_in_min=round(convert_timedelta(required_time))
	if time_in_min - time > 0: 
		continue
	else: 
		s3_client.delete_object(Bucket=source_bucket,Key=key,VersionId=i['VersionId'])
