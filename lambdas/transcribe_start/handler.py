# lambdas/transcribe_start/handler.py
import time, uuid, boto3

transcribe = boto3.client("transcribe")

def lambda_handler(event, context):
    # event comes from EventBridge via Step Functions:
    # { "bucket": "...uploads...", "key": "<videoId>/file.mp4", "processedBucket": "..." }
    bucket = event["bucket"]
    key = event["key"]
    video_id = key.split("/", 1)[0]

    # Unique name; avoids "Job already exists" errors
    job_name = f"transcribe-{video_id}-{int(time.time())}-{str(uuid.uuid4())[:8]}"

    media_uri = f"s3://{bucket}/{key}"

    # Start WITHOUT OutputBucketName -> Transcribe will host the JSON for us
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": media_uri},
        MediaFormat="mp4",
        LanguageCode="en-US"
    )

    # Pass downstream
    event.update({
        "videoId": video_id,
        "transcriptionJobName": job_name
    })
    return event
