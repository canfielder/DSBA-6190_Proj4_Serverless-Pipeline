import boto3
import botocore
import io
import json
import logging
import wikipedia
from pythonjsonlogger import jsonlogger
import pandas as pd


# SETUP LOGGER
LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
LOG.addHandler(logHandler)


# S3
REGION = "us-east-1"
s3_bucket = "dsba-6190-project4-serverless-data-engineering-pipeline"
session = boto3.Session(region_name=REGION)
comprehend = session.client(service_name='comprehend')

def write_s3(race_dict_ent):
    """Write S3 s3_bucket"""
    
    for race in race_dict_ent:
        df = pd.DataFrame.from_dict(race_dict_ent[race])
        
        # Re-order Columns
        df = df[['Text', 'Type', 'Score', 'BeginOffset', 'EndOffset']]
        
        # Convert Daataframe to CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index = False)

        race = race.lower().replace(' ', '_')

        # Send to S3
        s3_resource = session.resource('s3')
        res = s3_resource.Object(s3_bucket, f'entity_{race}.csv').\
            put(Body=csv_buffer.getvalue())
        LOG.info(f"result of write name: {race} to s3_bucket:\
            {s3_bucket} with:\n {res}")
        

### SQS FUNCTIONS ###
def sqs_connection():
    """Creates an SQS Connection which defaults to global var REGION"""

    sqs_client = session.client("sqs")
    log_sqs_client_msg = "Creating SQS connection in Region: [%s]" % REGION
    LOG.info(log_sqs_client_msg)
    
    return sqs_client

def delete_sqs_msg(queue_name, receipt_handle):

    sqs_client = sqs_connection()
    try:
        queue_url = sqs_client.get_queue_url(QueueName=queue_name)["QueueUrl"]
        delete_log_msg = "Deleting msg with ReceiptHandle %s" % receipt_handle
        LOG.info(delete_log_msg)
        response = sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
    except botocore.exceptions.ClientError as error:
        exception_msg = "FAILURE TO DELETE SQS MSG: Queue Name [%s] with error: [%s]" %\
            (queue_name, error)
        LOG.exception(exception_msg)
        return None

    delete_log_msg_resp = "Response from delete from queue: %s" % response
    LOG.info(delete_log_msg_resp)
    
    return response

def races_to_wikipedia(race_list):
    race_dict = {}
    wikipedia_snippit = []
    n = 0
    for race in race_list:
        wikipedia_snippit.append(wikipedia.summary(race, sentences=1))
        race_dict.update({race:wikipedia_snippit[n]})
        n += 1
        LOG.info(f"Grabbed wikipedia entry for {race}")
        
    return race_dict


def entity_detect(race_dict):
    entity_dict = {}
    # Extract Entities from Wikipedia Snippet
    for race in race_dict:
        entry_summary = race_dict[race]
        payload = comprehend.detect_entities(Text = entry_summary, 
                                             LanguageCode = 'en')
        entity = payload['Entities']
        entity_dict.update({race:entity})
        LOG.debug(f"Found Entites: {entity}")
        
    return entity_dict


def lambda_handler(event, context):
    """Entry Point for Lambda"""

    LOG.info(f"SURVEYJOB LAMBDA, event {event}, context {context}")
    receipt_handle  = event['Records'][0]['receiptHandle'] #sqs message
    event_source_arn = event['Records'][0]['eventSourceARN']

    races = [] #Captured from Queue

    # Process Queue
    for record in event['Records']:
        body = json.loads(record['body'])
        race_name = body['Races']

        #Capture for processing
        races.append(race_name)

        extra_logging = {"body": body, "race_name":race_name}
        LOG.info(f"SQS CONSUMER LAMBDA, splitting sqs arn with value: \
            {event_source_arn}",extra=extra_logging)
        qname = event_source_arn.split(":")[-1]
        extra_logging["queue"] = qname
        LOG.info(f"Attemping Deleting SQS receiptHandle {receipt_handle} with \
            queue_name {qname}", extra=extra_logging)
        res = delete_sqs_msg(queue_name=qname, receipt_handle=receipt_handle)
        LOG.info(f"Deleted SQS receipt_handle {receipt_handle} with res {res}",\
            extra=extra_logging)

    # Create Dictionary of Race Name and Wikipedia Snippet
    LOG.info(f"Creating Dictionary with Values: {races}")
    race_dict = races_to_wikipedia(races)

    # Perform Entity Detection Analysis
    race_dict_ent = entity_detect(race_dict)
    LOG.info(f"Entity from select Ultra races: {race_dict_ent}")

    # Write result to S3
    write_s3(race_dict_ent)