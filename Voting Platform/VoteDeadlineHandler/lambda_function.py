""" 
This function is responsible for all post-election actions, such as:
1. Vote counting
2. Informing voters about voting results
3. Unlocking the system to disable the login alarm function
"""
import json
import boto3
import os

def get_parameter(parameter):
    dynamodb = boto3.resource('dynamodb')
    parameters_table = dynamodb.Table(os.environ.get("PARAMETERS_TABLE_NAME"))
    response = parameters_table.get_item(Key={"parameter": parameter})
    return response.get("Item", None).get("value", None)
    
def set_parameter(parameter, value):
    dynamodb = boto3.resource('dynamodb')
    parameters_table = dynamodb.Table(os.environ.get("PARAMETERS_TABLE_NAME"))
    parameters_table.put_item(Item={"parameter": str(parameter),
                                    "value": str(value)}
                             )
def lambda_handler(event, context):
    
    dynamodb = boto3.resource('dynamodb')
    candidates_table = dynamodb.Table(os.environ.get("CANDIDATES_TABLE_NAME"))
    votes_table = dynamodb.Table(os.environ.get("VOTES_TABLE_NAME"))
    voters_table = dynamodb.Table(os.environ.get("VOTERS_TABLE_NAME"))
    
    # Get a list of all candidates' names
    candidates = candidates_table.scan().get("Items", None)
    candidate_names = [candidate["full_name"] for candidate in candidates]
    
    # Get all vote records
    votes = votes_table.scan().get("Items", None)
    results = {}
    
    # Nullify initial vote count
    for name in candidate_names:
        results[name] = 0
    
    # Count votes for each candidate
    for vote in votes:
        results[vote["candidate"]] += 1
    
    results_message = "Voting results:\n\n"
    for candidate in results.keys():
        results_message += (str(candidate) + ": " + str(results[candidate]) + "\n")
    
    # Get voters and inform them about voting results
    voters = voters_table.scan().get("Items", None)
    email_client = boto3.client("ses", region_name="eu-west-1")
    sender_email = get_parameter("sender_email")
    for voter in voters:
        voter_email = voter["email"]
        email_client.send_email(Source=sender_email,
                                Destination={"ToAddresses": [voter_email,]},
                                Message={"Subject": {"Data": "Voting results available"},
                                         "Body": {"Text": {"Data": results_message}}
                                        }
                                )
    
    # Unlock the system
    set_parameter("started", "false")
    set_parameter("locked", "false")
    
    return {
        'statusCode': 200,
        'body': json.dumps("VOTING FINISHED")
    }
