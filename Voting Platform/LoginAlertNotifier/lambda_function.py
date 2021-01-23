"""
This function is responsible for sending alert messages to all observers of the voting process.
The function processes all incoming payloads from a CloudWatch Alarm that is set to react to any console login.
If the lock flag is set - that means the detected login was unauthorized and observers must be informed that the system is compromised.
"""

import json
import boto3
import gzip
import os

def lambda_handler(event, context):
    
    print(event)
    
    ALERT_MESSAGE_OBSERVERS = "Dear observers, we have detected an apparent login into the management console, voting results may have been compromised."
    OBSERVER_TOPIC_ARN = os.environ.get("OBSERVER_ALERT_TOPIC")
    
    # If a console login is detected - ring the alarm
    dynamodb = boto3.resource('dynamodb')
    parameters_table = dynamodb.Table(os.environ.get("PARAMETERS_TABLE_NAME"))
    locked = parameters_table.get_item(Key={"parameter": "locked"}).get("Item", None).get("value", None)
    if locked=="true":
        print("UNAUTHORIZED LOGIN DETECTED, VOTING PROCESS SECURITY COMPROMISED")
        sns_client = boto3.client('sns')
        sns_client.publish(TopicArn=OBSERVER_TOPIC_ARN, Message=ALERT_MESSAGE_OBSERVERS)
        
    return {
        'statusCode': 200,
        'body': json.dumps("I'm on guard in the name of justice!")
    }
