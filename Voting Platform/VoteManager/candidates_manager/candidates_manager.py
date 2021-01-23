from db_manager.dynamodb_manager import DynamoDBManager

class CandidatesManager:

    @classmethod
    def add_candidates(cls, candidates_list):
        """
        This method adds specified candidates to the database.
        """
        for candidate in candidates_list:
            database = DynamoDBManager()
            response = database.add_candidate(candidate["candidate_full_name"], candidate["candidate_email"], candidate["candidate_page_link"])
        return response