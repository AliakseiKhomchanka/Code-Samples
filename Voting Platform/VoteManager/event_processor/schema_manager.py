# This file is responsible for storing schema for incoming events

schema_dict = {}

schema_dict["ADD_VOTERS_SCHEMA"] = {"type": "object",
                                     "properties": {
                                         "command": {"const": "add_voters"},
                                         "administrator_token": {"type": "string"},
                                         "voters_to_add": {"type": "array",
                                                           "items": {"type": "object",
                                                                     "properties": {
                                                                                    "student_id": {"type": "string"},
                                                                                    "student_email": {"type": "string"}
                                                                                   }
                                                                    }
                                                          }
                                                   }
                                    }
                     
schema_dict["ADD_CANDIDATES_SCHEMA"] = {"type": "object",
                                         "properties": {
                                             "command": {"const": "add_candidates"},
                                             "administrator_token": {"type": "string"},
                                             "candidates_to_add": {"type": "array",
                                                                   "items": {"type": "object",
                                                                             "properties": {
                                                                                            "candidate_full_name": {"type": "string"},
                                                                                            "candidate_email": {"type": "string"},
                                                                                            "candidate_page_link": {"type": "string"}
                                                                                           }
                                                                            }
                                                                  }
                                                       }
                                        }
                        
schema_dict["CAST_VOTE_SCHEMA"] = { "type": "object",
                                     "properties": {
                                                     "command": {"const": "cast_vote"},
                                                     "voter_token": {"type": "string"},
                                                     "voter_id": {"type": "string"},
                                                     "candidate_full_name": {"type": "string"}
                                                   }
                                   }

schema_dict["GET_CANDIDATES_SCHEMA"] = {  "type": "object",
                                         "properties": {
                                                         "command": {"const": "get_candidates"}
                                                       }
                                      }
                      
schema_dict["LOCK_SCHEMA"] = {  "type": "object",
                                 "properties": {
                                                 "command": {"const": "lock"},
                                                 "administrator_token": {"type": "string"}
                                               }
                           }
           
schema_dict["START_SCHEMA"] = {  "type": "object",
                                 "properties": {
                                                 "command": {"const": "start"},
                                                 "administrator_token": {"type": "string"}
                                               }
                           }