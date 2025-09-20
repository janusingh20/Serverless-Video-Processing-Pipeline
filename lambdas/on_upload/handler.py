import os, json, boto3
ddb = boto3.resource("dynamodb")
TABLE = ddb.Table(os.environ["VIDEOS_TABLE"])
SFN = boto3.client("stepfunctions")

def lambda_handler(event, context):
    # S3 event
    rec = event["Records"][0]
    bucket = rec["s3"]["bucket"]["name"]
    key = rec["s3"]["object"]["key"]
    # videoId is the first path segment
    video_id = key.split("/")[0]

    TABLE.update_item(
        Key={"videoId": video_id},
        UpdateExpression="SET #s = :s, sourceBucket = :b, sourceKey = :k",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": "UPLOADED", ":b": bucket, ":k": key}
    )

    # Start state machine
    sfn_arn = os.environ["PIPELINE_STATEMACHINE_ARN"]
    SFN.start_execution(
        stateMachineArn=sfn_arn,
        input=json.dumps({"videoId": video_id, "bucket": bucket, "key": key})
    )
    return {"statusCode": 200, "body": "started"}
