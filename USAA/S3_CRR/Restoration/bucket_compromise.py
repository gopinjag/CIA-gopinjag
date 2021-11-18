import boto3
from botocore.exceptions import ClientError

client = boto3.client('s3')
iam_client=boto3.client('iam')
s3_list=client.list_buckets()
account_id = boto3.client('sts').get_caller_identity().get('Account')

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

for i in s3_list['Buckets']:
	try:
		bucket_name=i['Name']
		#print(bucket_name)
		s3_status=client.get_bucket_replication(Bucket=bucket_name)
		for j in s3_status['ReplicationConfiguration']['Rules']:
			if j['Status'] == "Enabled": 
				check(bucket_name)
			else: 
				print("Replication disabled")
	except ClientError as e:
		error_code = str(e.response['Error']['Code'])
		print(error_code)
