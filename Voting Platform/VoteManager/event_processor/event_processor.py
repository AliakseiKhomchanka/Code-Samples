import os
import boto3
from jsonschema import validate
from jsonschema import ValidationError
from event_processor.schema_manager import schema_dict
from voters_manager.voters_manager import VotersManager
from candidates_manager.candidates_manager import CandidatesManager
from db_manager.dynamodb_manager import DynamoDBManager
from response_generator.generator import generate_response as respond

class EventProcessor:

    def __init__(self, request_id="NONE"):
        self.request_id = request_id
        # self.api_root = os.environ.get("api_root")
        self.events_list = ["ADD_VOTERS",
                            "ADD_CANDIDATES",
                            "GET_CANDIDATES",
                            "LOCK",
                            "START",
                            "CAST_VOTE"]
        self.handlers = {"ADD_VOTERS": self.command_add_voters,
                         "ADD_CANDIDATES": self.command_add_candidates,
                         "GET_CANDIDATES": self.command_get_candidates,
                         "LOCK": self.command_lock,
                         "START": self.command_start,
                         "CAST_VOTE": self.command_cast_vote
                        }
        self.db_manager = DynamoDBManager()
        self.admin_token = self.db_manager.get_parameter("admin_token")
        self.locked = self.db_manager.get_parameter("locked")
        self.started = self.db_manager.get_parameter("started")
              
    # EVENT PROCESSING ---------------------------------------------------------  
                            
    def process_event(self, payload):
        event_type = self._determine_event(payload)
        if event_type != "UNKNOWN EVENT TYPE":
            return self._delegate_event(event_type, payload)
        else:
            return respond("EVENT VALIDATION FAILED", 400)

    def _determine_event(self, payload):
        # Determines type of the event, checks validity of the payload according to schema
        # At this stage, validity of the token is not checked, we just determine the type of the event
        
        determined_type = "UNKNOWN EVENT TYPE"
        for event_type in self.events_list:
            try:
                result = validate(instance=payload, schema=schema_dict[event_type + "_SCHEMA"])
                determined_type = event_type
            except ValidationError as e:
                continue
        return determined_type
        
    def _delegate_event(self, event_type, payload):
        # Delegates the event to the handler
        response = self.handlers[event_type](payload)
        return response

    # COMMAND HANDLERS ---------------------------------------------------------

    def command_add_voters(self, payload):
        if self.started == "true":
            return respond("VOTING ALREADY STARTED", 403)
        if payload["administrator_token"] == self.admin_token:
            response = VotersManager.add_voters(payload["voters_to_add"])
            return response
        else:
            return respond("WRONG TOKEN, COMMAND REJECTED", 403)
            
    def command_add_candidates(self, payload):
        if self.started == "true":
            return respond("VOTING ALREADY STARTED", 403)
        if payload["administrator_token"] == self.admin_token:
            response = CandidatesManager.add_candidates(payload["candidates_to_add"])
            return response
        else:
            return respond("WRONG TOKEN, COMMAND REJECTED", 403)
            
    def command_get_candidates(self, payload):
        # Note that no token is required for this command
        if self.started == "false":
            return respond("VOTING NOT STARTED YET", 403)
        return respond(str(self.db_manager.get_candidates()), 200)
            
    def command_lock(self, payload):
        if self.locked == "true":
            return respond("SYSTEM ALREADY LOCKED", 403)
        if payload["administrator_token"] == self.admin_token:
            self.db_manager.set_parameter(parameter="locked", value="true")
            return respond("SYSTEM LOCKED", 200)
        else:
            return respond("WRONG TOKEN, COMMAND REJECTED", 403)
            
    def command_start(self, payload):
        if self.locked == "false":
            return respond("LOCK THE SYSTEM FIRST", 403)
        if self.started == "true":
            return respond("VOTING ALREADY STARTED", 403)
        if payload["administrator_token"] == self.admin_token:
            self.db_manager.set_parameter(parameter="started", value="true")
            return respond("VOTING STARTED", 200)
        else:
            return respond("WRONG TOKEN, COMMAND REJECTED", 403)
            
    def command_cast_vote(self, payload):
        if self.started != "true":
            return respond("VOTING NOT STARTED YET", 403)
        voter = self.db_manager.get_voter(id=payload["voter_id"])
        if voter["token"] == payload["voter_token"] and voter["voted"] == "false":
            response = self.db_manager.add_vote(voter_id=payload["voter_id"], event_id=self.request_id, candidate=payload["candidate_full_name"])
            return response
        else:
            return respond("WRONG TOKEN OR ALREADY VOTED, COMMAND REJECTED", 403)

