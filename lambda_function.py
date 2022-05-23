import json
import boto3
import os

from urllib import parse


def lambda_handler(event, context):
    """Sample Lambda function
       Uses dynamodb and s3 

    """
    s3_client = boto3.client("s3")
    dynamodb_client = boto3.client("dynamodb")

    records = event.get("Records", [])
    if not records:
        raise Exception("records must be provided for successful processing")

    account_id = records[0].get("AccountId")
    if account_id is None:
        raise Exception("records must have an account id")

    filenames = []

    for record in event.get("Records", []):
        filename = parse.unquote_plus(record["s3"]["object"]["key"])
        s3_client.get_object(
            Bucket=os.environ["Bucket"],
            Key=filename
        )
        filenames.append(filename)

    files_table = os.getenv("FILES_TABLE")
    dynamodb_client.describe_table(TableName=files_table)
    res = dynamodb_client.transact_get_items(
        TransactItems=[
            {
                'Get': {
                    'Key': {
                        'account_id': {
                            'S': account_id,
                        }
                    }
                },
                'TableName': files_table
            }])
    items = res.get("Responses", [])
    if not items:
        dynamodb_client.put_item(
            TableName=filename,
            Item={'account_id': {'S': account_id}, 'files': {'L': filenames}})

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Got {len(filenames)} to update",
        }),
    }

