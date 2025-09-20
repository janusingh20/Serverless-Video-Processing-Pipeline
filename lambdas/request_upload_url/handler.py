import json, os, uuid, boto3
s3 = boto3.client("s3")
ddb = boto3.resource("dynamodb")
TABLE = ddb.Table(os.environ["VIDEOS_TABLE"])
UPLOADS_BUCKET = os.environ["UPLOADS_BUCKET"]

def lambda_handler(event, context):
    body = json.loads(event.get("body") or "{}")
    filename = body.get("filename", "upload.mp4")
    video_id = str(uuid.uuid4())
    key = f"{video_id}/{filename}"

    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={"Bucket": UPLOADS_BUCKET, "Key": key, "ContentType": "video/mp4"},
        ExpiresIn=3600,
        HttpMethod="PUT"
    )

    TABLE.put_item(Item={
        "videoId": video_id,
        "status": "REQUESTED",
        "sourceKey": key,
    })

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"videoId": video_id, "uploadUrl": url, "s3Key": key})
    }
