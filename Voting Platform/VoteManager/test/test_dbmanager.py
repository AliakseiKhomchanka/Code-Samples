import unittest
from unittest import mock

from db_manager.dynamodb_manager import DynamoDBManager
from response_generator.generator import generate_response as respond


class TestDBManager(unittest.TestCase):

    @mock.patch("db_manager.dynamodb_manager.random.randint")
    @mock.patch("db_manager.dynamodb_manager.boto3.resource")
    def test_add_voter(self, mock_boto3_resource, mock_randint):
        manager = DynamoDBManager()
        mock_randint.return_value = "random"
        id = "some id"
        email = "some email"
        manager.add_voter(id, email)
        manager.voters_table.put_item.assert_called_with(Item={"student_id": id,
                                                               "email": email,
                                                               "token": "random",
                                                               "voted": "false"
                                                               }
                                                         )

    @mock.patch("db_manager.dynamodb_manager.boto3.resource")
    def test_get_voter(self, mock_boto3_resource):
        manager = DynamoDBManager()
        id = "some id"
        manager.get_voter(id)
        manager.voters_table.get_item.assert_called_with(Key={"student_id": id})

    @mock.patch("db_manager.dynamodb_manager.boto3.resource")
    def test_mark_voter(self, mock_boto3_resource):
        manager = DynamoDBManager()
        id = "some id"
        status = "true"
        manager.mark_voter(id, status)
        manager.voters_table.update_item.assert_called_with(Key={"student_id": id},
                                                            UpdateExpression="SET #voted = :voted_flag",
                                                            ExpressionAttributeValues={
                                                                ":voted_flag": "true"
                                                            },
                                                            ExpressionAttributeNames={
                                                                "#voted": "voted"
                                                            }
                                                            )

    @mock.patch("db_manager.dynamodb_manager.boto3.resource")
    def test_add_candidate(self, mock_boto3_resource):
        manager = DynamoDBManager()
        candidate_full_name = "Person Personson"
        candidate_email = "some email"
        candidate_link = "some link"
        manager.add_candidate(candidate_full_name, candidate_email, candidate_link)
        manager.candidates_table.put_item.assert_called_with(Item={"full_name": candidate_full_name,
                                                                   "candidate_email": candidate_email,
                                                                   "candidate_page_link": candidate_link})

    @mock.patch("db_manager.dynamodb_manager.boto3.resource")
    def test_get_candidate(self, mock_boto3_resource):
        manager = DynamoDBManager()
        candidate_full_name = "Person Personson"
        manager.get_candidate(candidate_full_name)
        manager.candidates_table.get_item.assert_called_with(Key={"full_name": candidate_full_name})

    @mock.patch("db_manager.dynamodb_manager.boto3.resource")
    def test_get_candidates(self, mock_boto3_resource):
        manager = DynamoDBManager()
        manager.get_candidates()
        manager.candidates_table.scan.assert_called()

    @mock.patch("db_manager.dynamodb_manager.boto3.client")
    @mock.patch("db_manager.dynamodb_manager.boto3.resource")
    def test_add_vote(self, mock_boto3_resource, mock_boto3_client):
        manager = DynamoDBManager()
        voter_id = "1337"
        event_id = "1111"
        candidate = "Person Personson"

        # Case 1: everything is normal ---------------------------------------------------------------------------------

        response = manager.add_vote(voter_id, event_id, candidate)
        assert response == respond('Congratulations! You have successfully cast your vote for the candidate {candidate}!'.format(candidate=candidate), 200)

        # --------------------------------------------------------------------------------------------------------------

        # Case 2: no such candidate ------------------------------------------------------------------------------------

        manager.get_candidate = (lambda candidate_name: None)
        response = manager.add_vote(voter_id, event_id, candidate)
        assert response == respond("NO SUCH CANDIDATE, PLEASE ENTER THE CORRECT FULL NAME", 404)

        # --------------------------------------------------------------------------------------------------------------

    @mock.patch("db_manager.dynamodb_manager.boto3.resource")
    def test_get_parameter(self, mock_boto3_resource):
        manager = DynamoDBManager()
        parameter = "some parameter"
        manager.get_parameter(parameter)
        manager.parameters_table.get_item.assert_called_with(Key={"parameter": parameter})

    @mock.patch("db_manager.dynamodb_manager.boto3.resource")
    def test_set_parameter(self, mock_boto3_resource):
        manager = DynamoDBManager()
        parameter = "some parameter"
        value = "some value"
        manager.set_parameter(parameter, value)
        manager.parameters_table.put_item.assert_called_with(Item={"parameter": str(parameter),
                                                                   "value": str(value)
                                                                   }
                                                             )


if __name__ == '__main__':
    unittest.main()