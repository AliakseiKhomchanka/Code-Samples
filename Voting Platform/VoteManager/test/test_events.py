import unittest
from unittest import mock

from event_processor.event_processor import EventProcessor
from response_generator.generator import generate_response as respond
from test.payloads.test_payloads import add_candidates, add_voters, cast_vote, get_candidates, lock, start



class TestEvents(unittest.TestCase):

    @classmethod
    def SetUpClass(cls):
        pass

    @mock.patch("event_processor.event_processor.DynamoDBManager")
    def test_event_recognition(self, mock_db_manager):
        processor = EventProcessor()

        # Case 1: add_candidates
        payload = add_candidates
        determined = processor._determine_event(payload)
        assert determined == "ADD_CANDIDATES"

        # Case 2: add_voters
        payload = add_voters
        determined = processor._determine_event(payload)
        assert determined == "ADD_VOTERS"

        # Case 3: cast_vote
        payload = cast_vote
        determined = processor._determine_event(payload)
        assert determined == "CAST_VOTE"

        # Case 4: get_candidates
        payload = get_candidates
        determined = processor._determine_event(payload)
        assert determined == "GET_CANDIDATES"

        # Case 5: lock
        payload = lock
        determined = processor._determine_event(payload)
        assert determined == "LOCK"

        # Case 6: start
        payload = start
        determined = processor._determine_event(payload)
        assert determined == "START"

    @mock.patch("event_processor.event_processor.VotersManager.add_voters")
    @mock.patch("event_processor.event_processor.DynamoDBManager")
    def test_add_voters(self, mock_db_manager, mock_votemanager_add_voters):
        processor = EventProcessor()
        payload = add_voters

        # Case 1: voting already started -------------------------------------------------------------------------------

        processor.started = "true"

        result = processor.command_add_voters(payload)
        assert result == respond("VOTING ALREADY STARTED", 403)

        # --------------------------------------------------------------------------------------------------------------

        # Case 2: voting not started yet, should call VotersManager.add_voters()

        processor.started = "false"
        processor.admin_token = payload["administrator_token"]

        processor.command_add_voters(payload)
        mock_votemanager_add_voters.assert_called_with(payload["voters_to_add"])
        mock_votemanager_add_voters.reset_mock()

        # --------------------------------------------------------------------------------------------------------------

        # Case 3: voting not started yet, wrong token, should return the 403 response

        processor.started = "false"
        processor.admin_token = "abracadabra"

        response = processor.command_add_voters(payload)
        mock_votemanager_add_voters.assert_not_called()
        assert response == respond("WRONG TOKEN, COMMAND REJECTED", 403)

        # --------------------------------------------------------------------------------------------------------------

    @mock.patch("event_processor.event_processor.CandidatesManager.add_candidates")
    @mock.patch("event_processor.event_processor.DynamoDBManager")
    def test_add_candidates(self, mock_db_manager, mock_candidatesmanager_add_candidates):
        processor = EventProcessor()
        payload = add_candidates

        # Case 1: voting already started -------------------------------------------------------------------------------

        processor.started = "true"

        result = processor.command_add_candidates(payload)
        assert result == respond("VOTING ALREADY STARTED", 403)

        # --------------------------------------------------------------------------------------------------------------

        # Case 2: voting not started yet, should call CandidatesManager.add_candidates()

        processor.started = "false"
        processor.admin_token = payload["administrator_token"]

        processor.command_add_candidates(payload)
        mock_candidatesmanager_add_candidates.assert_called_with(payload["candidates_to_add"])
        mock_candidatesmanager_add_candidates.reset_mock()

        # --------------------------------------------------------------------------------------------------------------

        # Case 3: voting not started yet, wrong token, should return the 403 response

        processor.started = "false"
        processor.admin_token = "abracadabra"

        response = processor.command_add_voters(payload)
        mock_candidatesmanager_add_candidates.assert_not_called()
        assert response == respond("WRONG TOKEN, COMMAND REJECTED", 403)

        # --------------------------------------------------------------------------------------------------------------

    @mock.patch("event_processor.event_processor.DynamoDBManager")
    def test_get_candidates(self, mock_db_manager):
        processor = EventProcessor()
        processor.db_manager.get_candidates = (lambda: "CALLED")
        payload = get_candidates

        # Case 1: voting not started yet -------------------------------------------------------------------------------

        processor.started = "false"

        result = processor.command_get_candidates(payload)
        assert result == respond("VOTING NOT STARTED YET", 403)

        # --------------------------------------------------------------------------------------------------------------

        # Case 2: voting started, should call DynamoDbManager.get_candidates() -----------------------------------------

        processor.started = "true"

        response = processor.command_get_candidates(payload)
        assert response == respond("CALLED", 200)

        # --------------------------------------------------------------------------------------------------------------

    @mock.patch("event_processor.event_processor.DynamoDBManager.set_parameter")
    @mock.patch("event_processor.event_processor.DynamoDBManager")
    def test_lock(self, mock_db_manager, mock_dbmanager_set_parameter):
        processor = EventProcessor()
        processor.db_manager.set_parameter = mock_dbmanager_set_parameter
        payload = lock

        # Case 1: system already locked --------------------------------------------------------------------------------

        processor.locked = "true"

        result = processor.command_lock(payload)
        assert result == respond("SYSTEM ALREADY LOCKED", 403)

        # --------------------------------------------------------------------------------------------------------------

        # Case 2: system not locked, should call DynamoDBManager.set_parameter() ---------------------------------------

        processor.locked = "false"
        processor.admin_token = payload["administrator_token"]

        response = processor.command_lock(payload)
        processor.db_manager.set_parameter.assert_called()
        assert response == respond("SYSTEM LOCKED", 200)

        # --------------------------------------------------------------------------------------------------------------

        # Case 3: wrong token, reject command --------------------------------------------------------------------------

        processor.locked = "false"
        processor.admin_token = "abracadabra"

        response = processor.command_lock(payload)
        assert response == respond("WRONG TOKEN, COMMAND REJECTED", 403)

        # --------------------------------------------------------------------------------------------------------------

    @mock.patch("event_processor.event_processor.DynamoDBManager.set_parameter")
    @mock.patch("event_processor.event_processor.DynamoDBManager")
    def test_start(self, mock_db_manager, mock_dbmanager_set_parameter):
        processor = EventProcessor()
        processor.db_manager.set_parameter = mock_dbmanager_set_parameter
        payload = start

        # Case 1: system not locked ------------------------------------------------------------------------------------

        processor.locked = "false"

        result = processor.command_start(payload)
        assert result == respond("LOCK THE SYSTEM FIRST", 403)

        # --------------------------------------------------------------------------------------------------------------

        # Case 2: voting already started -------------------------------------------------------------------------------

        processor.locked = "true"
        processor.started = "true"
        processor.admin_token = payload["administrator_token"]

        response = processor.command_start(payload)
        assert response == respond("VOTING ALREADY STARTED", 403)

        # --------------------------------------------------------------------------------------------------------------

        # Case 3: start normally ---------------------------------------------------------------------------------------

        processor.locked = "true"
        processor.started = "false"
        processor.admin_token = payload["administrator_token"]

        response = processor.command_start(payload)
        processor.db_manager.set_parameter.assert_called()
        processor.db_manager.set_parameter.reset_mock()
        assert response == respond("VOTING STARTED", 200)

        # --------------------------------------------------------------------------------------------------------------

        # Case 4: wrong token, reject command --------------------------------------------------------------------------

        processor.locked = "true"
        processor.started = "false"
        processor.admin_token = "abracadabra"

        response = processor.command_start(payload)
        processor.db_manager.set_parameter.assert_not_called()
        processor.db_manager.set_parameter.reset_mock()
        assert response == respond("WRONG TOKEN, COMMAND REJECTED", 403)

        # --------------------------------------------------------------------------------------------------------------

    @mock.patch("event_processor.event_processor.DynamoDBManager.get_voter")
    @mock.patch("event_processor.event_processor.DynamoDBManager.add_vote")
    @mock.patch("event_processor.event_processor.DynamoDBManager")
    def test_cast_vote(self, mock_db_manager, mock_dbmanager_add_vote, mock_dbmanager_get_voter):
        processor = EventProcessor()
        processor.db_manager.get_voter = mock_dbmanager_get_voter
        processor.db_manager.add_vote = mock_dbmanager_add_vote
        processor.request_id = 1111
        payload = cast_vote

        # Case 1: voting not started -----------------------------------------------------------------------------------

        processor.started = "false"

        result = processor.command_cast_vote(payload)
        assert result == respond("VOTING NOT STARTED YET", 403)
        processor.db_manager.get_voter.assert_not_called()
        processor.db_manager.add_vote.assert_not_called()

        # --------------------------------------------------------------------------------------------------------------

        # Case 2: cast vote normally -----------------------------------------------------------------------------------

        processor.started = "true"

        processor.db_manager.get_voter.return_value = {"voted": "false", "token": payload["voter_token"]}

        processor.command_cast_vote(payload)
        processor.db_manager.get_voter.assert_called_with(id=payload["voter_id"])
        processor.db_manager.add_vote.assert_called_with(voter_id=payload["voter_id"], event_id=processor.request_id,
                                                         candidate=payload["candidate_full_name"])
        processor.db_manager.get_voter.reset_mock()
        processor.db_manager.add_vote.reset_mock()

        # --------------------------------------------------------------------------------------------------------------

        # Case 3: wrong token, rejected --------------------------------------------------------------------------------

        processor.locked = "true"
        processor.started = "true"
        processor.db_manager.get_voter.return_value = {"voted": "false", "token": "actually a different token"}

        response = processor.command_cast_vote(payload)
        processor.db_manager.get_voter.assert_called_with(id=payload["voter_id"])
        processor.db_manager.add_vote.assert_not_called()
        processor.db_manager.get_voter.reset_mock()
        processor.db_manager.add_vote.reset_mock()
        assert response == respond("WRONG TOKEN OR ALREADY VOTED, COMMAND REJECTED", 403)

        # --------------------------------------------------------------------------------------------------------------

        # Case 4: another vote being processed, rejected ---------------------------------------------------------------

        processor.locked = "true"
        processor.started = "true"
        processor.db_manager.get_voter.return_value = {"voted": "pending", "token": payload["voter_token"]}

        response = processor.command_cast_vote(payload)
        processor.db_manager.get_voter.assert_called_with(id=payload["voter_id"])
        processor.db_manager.add_vote.assert_not_called()
        processor.db_manager.get_voter.reset_mock()
        processor.db_manager.add_vote.reset_mock()
        assert response == respond("WRONG TOKEN OR ALREADY VOTED, COMMAND REJECTED", 403)

        # --------------------------------------------------------------------------------------------------------------

        # Case 5: voter already voted ----------------------------------------------------------------------------------

        processor.locked = "true"
        processor.started = "true"
        processor.db_manager.get_voter.return_value = {"voted": "true", "token": payload["voter_token"]}

        response = processor.command_cast_vote(payload)
        processor.db_manager.get_voter.assert_called_with(id=payload["voter_id"])
        processor.db_manager.add_vote.assert_not_called()
        processor.db_manager.get_voter.reset_mock()
        processor.db_manager.add_vote.reset_mock()
        assert response == respond("WRONG TOKEN OR ALREADY VOTED, COMMAND REJECTED", 403)

        # --------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()