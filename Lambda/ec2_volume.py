import boto3
import time
import os
timestream_client = boto3.client('timestream-write')
ec2_client = boto3.client('ec2')
response=ec2_client.describe_volumes()

def ebs_volume():
   for i in response['Volumes']:
        AZ=i['AvailabilityZone']
        VolumeID=i['VolumeId']
        State=i['State']
        Size=i['Size']
        VolumeType=i['VolumeType']
        region=AZ.rstrip(AZ[-1])
        writeData(VolumeID,State,Size,VolumeType,AZ,region)


def writeData(VolumeID,State,Size,VolumeType,AZ,region):
   print("Writing records")
   current_time = str(round(time.time() * 1000))
   dimensions = [
   {'Name': 'region', 'Value': region},
   {'Name': 'az', 'Value': AZ},
   {'Name': 'VolumeID', 'Value': VolumeID},
   {'Name': 'volumeType', 'Value': VolumeType},
   {'Name': 'volumeState', 'Value': State}
   ]
   volumeSize = {
     'Dimensions': dimensions,
     'MeasureName': 'Volume_size',
     'MeasureValue': str(Size),
     'MeasureValueType': 'BIGINT',
     'Time': current_time
   }
   records = [volumeSize]
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
   ebs_volume()


