from db_manager.dynamodb_manager import DynamoDBManager
import random
import boto3

class VotersManager:

    @classmethod
    def add_voters(cls, voters_list):
        """
        This method adds specified voters to the database. It also sends the voting token to every voter using the provided e-mail address.
        """
        database = DynamoDBManager()
        email_client = boto3.client("ses", region_name="eu-west-1")
        sender_email = database.get_parameter("sender_email")
        
        for voter in voters_list:
            response = database.add_voter(voter["student_id"], voter["student_email"])
            message = """
            Congratulations!
            You have been successfully registered for the upcoming election!
            Your personal voter code is:
            {token}""".format(token=response["token"])
            email_client.send_email(Source=sender_email,
                                    Destination={"ToAddresses": [voter["student_email"],]},
                                    Message={"Subject": {"Data": "Your personal voter code"},
                                             "Body": {"Text": {"Data": message}}
                                            }
                                    )
            response = respond("Voter {voter} successfully added to the database!".format(voter=voter["student_id"]), 200)
        return response