import os, boto3
from botocore.config import Config

def _mc_client():
    mc = boto3.client("mediaconvert")
    endpoint = mc.describe_endpoints(MaxResults=1)["Endpoints"][0]["Url"]
    return boto3.client("mediaconvert", endpoint_url=endpoint, config=Config(retries={"max_attempts": 10, "mode": "standard"}))

def lambda_handler(event, context):
    """
    expects in event:
      mcJobId, videoId, processedBucket
    """
    job_id = event["mcJobId"]
    mc = _mc_client()
    job = mc.get_job(Id=job_id)["Job"]
    status = job["Status"]

    if status in ("SUBMITTED", "PROGRESSING"):
        # Let Step Functions retry this task until complete
        raise Exception("RETRY")

    if status != "COMPLETE":
        # Surface failure; state machine will catch or fail as designed
        event["transcodeStatus"] = status
        return event

    event["transcodeStatus"] = "COMPLETE"
    # Optionally we could list thumbnails or output keys here
    return event
