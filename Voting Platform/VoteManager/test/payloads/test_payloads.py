add_candidates = {  "command": "add_candidates",
                    "administrator_token": "123456",
                    "candidates_to_add":
                        [
                            {"candidate_full_name": "Marvelous Comrade",
                             "candidate_email": "khomchankaa@gmail.com",
                             "candidate_page_link": "www.somewhere.com"
                            },
                            {"candidate_full_name": "Also Marvelous Comrade",
                             "candidate_email": "khomchankaa@gmail.com",
                             "candidate_page_link": "www.somewhere.com"
                            }
                        ]
                }

add_voters = {  "command": "add_voters",
                "administrator_token": "123456",
                "voters_to_add":
                    [
                        {"student_id": "1",
                         "student_email": "kogotinazval@mail.ru"},
                        {"student_id": "2",
                         "student_email": "kogotinazval@mail.ru"},
                        {"student_id": "3",
                         "student_email": "kogotinazval@mail.ru"}
                    ]
            }

cast_vote = {   "command": "cast_vote",
    "voter_token": "some token",
    "voter_id": "some id",
    "candidate_full_name": "Marvelous Comrade"
}

get_candidates = {   "command": "get_candidates"
}

lock = {   "command": "lock",
    "administrator_token": "123456"
}

start = {   "command": "start",
    "administrator_token": "123456"
}
