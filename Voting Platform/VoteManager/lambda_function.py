from event_processor.event_processor import EventProcessor
import json
import os

def lambda_handler(event, context):
    # The entry point for the Lambda function
    
    print(json.loads(event["body"]))
    
    processor = EventProcessor(request_id=str(context.aws_request_id))
    response = processor.process_event(json.loads(event["body"]))
    
    print(response)

    return response
