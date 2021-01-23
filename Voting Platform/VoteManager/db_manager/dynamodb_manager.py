import boto3
import os
import random
from response_generator.generator import generate_response as respond

class DynamoDBManager:
    
    def __init__(self):
        voters_table_name = os.environ.get("VOTERS_TABLE", None)
        candidates_table_name = os.environ.get("CANDIDATES_TABLE", None)
        votes_table_name = os.environ.get("VOTES_TABLE", None)
        parameters_table_name = os.environ.get("PARAMETER_TABLE")
        self.dynamodb = boto3.resource('dynamodb')
        self.voters_table = self.dynamodb.Table(voters_table_name)
        self.candidates_table = self.dynamodb.Table(candidates_table_name)
        self.votes_table = self.dynamodb.Table(votes_table_name)
        self.parameters_table = self.dynamodb.Table(parameters_table_name)
        
    def add_voter(self, id, email):
        token = random.randint(1,2**128)
        response = self.voters_table.put_item(Item={"student_id": id,
                                                    "email": email,
                                                    "token": str(token),
                                                    "voted": "false"
        }
                                             )
        return {"token": token, "response": response}
        
    def get_voter(self, id):
        response = self.voters_table.get_item(Key={"student_id": id})
        return response.get("Item", None)
        
    def mark_voter(self, id, status):
        self.voters_table.update_item(Key={"student_id": id},
                                                 UpdateExpression="SET #voted = :voted_flag",
                                                 ExpressionAttributeValues={
                                                     ":voted_flag": status
                                                 },
                                                 ExpressionAttributeNames={
                                                     "#voted": "voted"
                                                 }
                                                 )
        
    def add_candidate(self, candidate_full_name, candidate_email, candidate_link):
        response = self.candidates_table.put_item(Item={"full_name": candidate_full_name,
                                                        "candidate_email": candidate_email,
                                                        "candidate_page_link": candidate_link})
        return response
        
    def get_candidate(self, candidate_full_name):
        response = self.candidates_table.get_item(Key={"full_name": candidate_full_name})
        return response.get("Item", None)
        
    def get_candidates(self):
        return self.candidates_table.scan()
        
    def add_vote(self, voter_id, event_id, candidate):
        
        if not self.get_candidate(candidate):
            return respond("NO SUCH CANDIDATE, PLEASE ENTER THE CORRECT FULL NAME", 404)
        
        # Set voted status to pending
        self.mark_voter(voter_id, "pending")
        
        try:
            self.mark_voter(voter_id, "true")
            response = self.votes_table.put_item(Item={"event_id": event_id,
                                                       "candidate": candidate})
            email_client = boto3.client("ses", region_name="eu-west-1")
            sender_email = self.get_parameter("sender_email")
            voter_email = self.get_voter(voter_id)["email"]
            email_client.send_email(Source=sender_email,
                                    Destination={"ToAddresses": [voter_email,]},
                                    Message={"Subject": {"Data": "Successfuly voted!"},
                                             "Body": {"Text": {"Data": "Congats! You've successfully voted for the candidate {candidate}!".format(candidate=candidate)}}
                                             }
                                    )
            
            return respond('Congratulations! You have successfully cast your vote for the candidate {candidate}!'.format(candidate=candidate), 200)
        except Exception as e:
            self.mark_voter(voter_id, "false")
            return respond("ERROR, VOTE NOT CAST", 500)
        
    def get_parameter(self, parameter):
        # Gets a requested parameter from the parameters table
        response = self.parameters_table.get_item(Key={"parameter": parameter})
        return response.get("Item", None).get("value", None)
        
    def set_parameter(self, parameter, value):
        response = self.parameters_table.put_item(Item={"parameter": str(parameter),
                                                        "value": str(value)
                                                       }
                                                 )
        return response