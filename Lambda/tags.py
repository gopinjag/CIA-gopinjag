import boto3 
import os 
import time 

ec2_client=boto3.client('ec2')
timestream_client = boto3.client('timestream-write')
tag1=os.getenv('tag1')
value1=os.getenv('value1')



F1={'Name': f'tag:{tag1}','Values': [f'{value1}']}
print(F1)
#F1={'Name': 'tag:cost','Values': ['1234']}

response = ec2_client.describe_instances(Filters=[F1])

def instance_tags():
    for i in response['Reservations']:
        for j in i['Instances']:
            InstanceId=j['InstanceId']
            AZ=j['Placement']['AvailabilityZone']
            region=AZ.rstrip(AZ[-1])
        writeData(InstanceId,AZ,region)
    


def writeData(InstanceId,AZ,region):
   print("Writing records")
   current_time = str(round(time.time() * 1000))
   dimensions = [
   {'Name': 'region', 'Value': region },
   {'Name': 'az', 'Value': AZ }
   ]
   InstanceTags = {
     'Dimensions': dimensions,
     'MeasureName': 'InstanceId',
     'MeasureValue': InstanceId,
     'MeasureValueType': 'VARCHAR',
     'Time': current_time
   }
   records = [InstanceTags]
   try:
       result = timestream_client.write_records(DatabaseName=os.getenv("DATABASE_NAME"), TableName=os.getenv("TABLE_NAME"),
Records=records, CommonAttributes={})
       print("WriteRecords Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])
   except timestream_client.exceptions.RejectedRecordsException as err:
       print("RejectedRecords: ", err)
       for rr in err.response["RejectedRecords"]:
           print("Rejected Index " + str(rr["RecordIndex"]) + ": " + rr["Reason"])
       print("Other records were written successfully. ")
   except Exception as err:
       print("Error:", err)
       
       
def lambda_handler(event, context): 
    instance_tags()

