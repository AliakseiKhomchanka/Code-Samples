# UNUSED, LEFT FOR HISTORY AND POSSIBLE MODIFICATIONS IN THE FUTURE

import os               # To access environment variables
import psycopg2         # To manage connections to the database
import boto3            # To manage CloudWatch logs

class DB_manager:
    
    def __init__(self):
        # Constructor

        # Load database credentials
        self.rds_host = os.environ.get("RDS_HOST")
        self.rds_db_name = os.environ.get("RDS_DB_NAME")
        self.rds_port = os.environ.get("RDS_PORT")
        self.rds_username = os.environ.get("RDS_USERNAME")
        self.rds_password = os.environ.get("RDS_PASSWORD")

        # Load voter and candidate table names
        self.rds_voter_table_name = os.environ.get("RDS_VOTER_TABLE_NAME")
        self.rds_candidate_table_name = os.environ.get("RDS_CANDIDATE_TABLE_NAME")
        self.rds_vote_stats_table_name = os.environ.get("RDS_VOTE_STATS_TABLE_NAME")

        # Connect to the database
        self.rds_connection = psycopg2.connect(host=self.rds_host,
                                               dbname=self.rds_db_name,
                                               port=self.rds_port,
                                               user=self.rds_username,
                                               password=self.rds_password)
        self.rds_cursor = self.rds_connection.cursor()

    def add_voter_to_the_list(self, voter_student_id, voter_email, voter_token):
        # Adds the specified voter to the voters' table in the database
        command = "INSERT INTO " + self.rds_voter_table_name + " (voter_student_id, voter_email, voter_token, voted) VALUES (%s, %s, %s, %s)"
        self.rds_cursor.execute(command, (voter_student_id, voter_email, voter_token, "False"))
        self.rds_connection.commit()

    def add_candidate_to_the_list(self, candidate_first_name, candidate_last_name, candidate_email, candidate_page_link):
        # Adds the specified candidate to the candidates' table in the database
        command = "INSERT INTO " + self.rds_candidate_table_name + " (candidate_first_name, candidate_last_name, candidate_email, candidate_page_link) VALUES (%s, %s, %s, %s)"
        self.rds_cursor.execute(command, (candidate_first_name, candidate_last_name, candidate_email, candidate_page_link))
        self.rds_connection.commit()

    def verify_voter(self, voter_student_id, voter_token):
        # Verify whether the specified voter is legitimate
        command = "SELECT (voter_student_id, voter_token, voted) FROM {table_name} WHERE voter_student_id = {id};".format(table_name=self.rds_voter_table_name, id=voter_student_id)
        self.rds_cursor.execute(command)
        voter_credentials = self.rds_cursor.fetchone(command)
        if voter_credentials == (voter_student_id, voter_token, "False"):
            return True
        else:
            return False
