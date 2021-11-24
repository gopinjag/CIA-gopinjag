import boto3
from botocore.exceptions import ClientError

client = boto3.client('s3')
iam_client=boto3.client('iam')
org_client = boto3.client('organizations')
sts = boto3.client('sts')

s3_list=client.list_buckets()
account_id = boto3.client('sts').get_caller_identity().get('Account')
role_arn = "arn:aws:iam::241576475648:role/CrossAccountS3ReadOnlyRole"

src_list=[]
dest_list=[]


def check(bucket_name):
	s3_input=client.get_bucket_encryption(Bucket=bucket_name)
	for j in s3_input['ServerSideEncryptionConfiguration']['Rules']:
		kms_key=j['ApplyServerSideEncryptionByDefault']['KMSMasterKeyID']
		#print(kms_key)
		role_policy=iam_client.get_role_policy(RoleName=f'{account_id}-{bucket_name}-CRR-Role',PolicyName='CrossRegionReplicationPolicy')
		#print(role_policy)
		for k in role_policy['PolicyDocument']['Statement']:
			if kms_key in k['Resource']:
				print("All configuration in tact")
			else: 
				continue
			
def lambda_handler(event, context):
	for i in s3_list['Buckets']:
		try:
			bucket_name=i['Name']
			src_list.append(bucket_name)
			s3_status=client.get_bucket_replication(Bucket=bucket_name)
			for j in s3_status['ReplicationConfiguration']['Rules']:
				if j['Status'] == "Enabled": 
					check(bucket_name)
				else: 
					print("Replication disabled")
		except ClientError as e:
			error_code = str(e.response['Error']['Code'])
			print(error_code)
			if error_code == 'ReplicationConfigurationNotFoundError':
				print('Replication does not exist on the Bucket ' + bucket_name)
	assume_role_response = sts.assume_role(RoleArn=role_arn, RoleSessionName="LambdaExecution")
	if "Credentials" in assume_role_response:
		assumed_session = boto3.session.Session(
			aws_access_key_id=assume_role_response['Credentials']['AccessKeyId'],
    		aws_secret_access_key=assume_role_response['Credentials']['SecretAccessKey'],
        	aws_session_token=assume_role_response['Credentials']['SessionToken'])
	s3_client = assumed_session.client('s3')
	buckets_response = s3_client.list_buckets()
	crv_buckets(buckets_response,s3_client)
	bucket_exist(dest_list)


def crv_buckets(s3_response,s3_client):
	for bucket in s3_response['Buckets']:
		if s3_client.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint'] == 'us-west-1':
			s3_uw1=bucket['Name']
			bucket_uw1=s3_uw1[13:][:-3]
			dest_list.append(bucket_uw1)
		if s3_client.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint'] == None:
			s3_ue1=bucket['Name']
			bucket_ue1=s3_ue1[13:]
			dest_list.append(bucket_ue1)	
	return(dest_list)

def bucket_exist(dest_list):
	for bucket_exist in src_list:
		if bucket_exist in dest_list:
			print(f"{bucket_exist} bucket exist in src and crv account")
		else:
			print(f"{bucket_exist} bucket deleted")
