import json

def generate_response(text, code):
    return {
                'statusCode': code,
                'body': text
           }