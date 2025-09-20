import os, json, urllib.request, boto3
transcribe = boto3.client("transcribe")
s3 = boto3.client("s3")

def lambda_handler(event, context):
    job_name = event["transcriptionJobName"]
    video_id = event["videoId"]
    out_bucket = event["processedBucket"]

    resp = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    status = resp["TranscriptionJob"]["TranscriptionJobStatus"]

    if status in ("QUEUED", "IN_PROGRESS"):
        raise Exception("RETRY")

    event["transcribeStatus"] = status
    if status != "COMPLETED":
        return event

    # Whether Transcribe wrote to our bucket or hosted the file, copy it into a fixed key
    uri = resp["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
    with urllib.request.urlopen(uri) as r:
        data = r.read()
    out_key = f"{video_id}/transcripts/transcript.json"
    s3.put_object(Bucket=out_bucket, Key=out_key, Body=data, ContentType="application/json")
    event["transcriptS3Key"] = out_key
    return event
