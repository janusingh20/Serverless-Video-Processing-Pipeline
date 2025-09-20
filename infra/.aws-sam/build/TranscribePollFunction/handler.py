# lambdas/transcribe_poll/handler.py
import os, time, json, urllib.request, boto3

s3 = boto3.client("s3")
transcribe = boto3.client("transcribe")

# Optional env var; we also accept event["processedBucket"]
PROCESSED_BUCKET_ENV = os.environ.get("PROCESSED_BUCKET", "")

def lambda_handler(event, context):
    job_name = event["transcriptionJobName"]
    video_id = event["videoId"]

    resp = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    status = resp["TranscriptionJob"]["TranscriptionJobStatus"]

    if status in ("QUEUED", "IN_PROGRESS"):
        # Let Step Functions Retry re-invoke us
        raise Exception("States.TaskFailed")

    # If Transcribe finished but not successfully, just return the status
    if status != "COMPLETED":
        event["transcribeStatus"] = status
        return event

    # Download the JSON that Transcribe hosted for us
    uri = resp["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
    with urllib.request.urlopen(uri) as r:
        data = r.read()

    out_bucket = event.get("processedBucket") or PROCESSED_BUCKET_ENV
    out_key = f"{video_id}/transcripts/transcript.json"

    s3.put_object(
        Bucket=out_bucket,
        Key=out_key,
        Body=data,
        ContentType="application/json"
    )

    event["transcribeStatus"] = "COMPLETED"
    event["transcriptS3Key"] = out_key
    return event
