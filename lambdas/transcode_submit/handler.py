import os, json, time, uuid, boto3
from botocore.config import Config
from botocore.exceptions import ClientError

s3 = boto3.client("s3")
sts = boto3.client("sts")

MEDIACONVERT_ROLE_ARN = os.environ["MEDIACONVERT_ROLE_ARN"]
PROCESSED_BUCKET = os.environ["PROCESSED_BUCKET"]

def _mc_client():
    # MediaConvert requires a per-account endpoint; we discover it each cold start.
    mc = boto3.client("mediaconvert")
    endpoint = mc.describe_endpoints(MaxResults=1)["Endpoints"][0]["Url"]
    return boto3.client("mediaconvert", endpoint_url=endpoint, config=Config(retries={"max_attempts": 10, "mode": "standard"}))

def lambda_handler(event, context):
    """
    event from Step Functions:
      {
        "bucket": "<uploads bucket>",
        "key": "<videoId>/filename.mp4",
        "processedBucket": "<processed bucket>"  # we still pass it through, but use PROCESSED_BUCKET env for authority
      }
    """
    bucket = event["bucket"]
    key = event["key"]
    video_id = key.split("/", 1)[0]
    dest = f"s3://{PROCESSED_BUCKET}/{video_id}"

    mc = _mc_client()

    job_settings = {
        "Inputs": [{
            "FileInput": f"s3://{bucket}/{key}",
        }],
        "OutputGroups": [
            # MP4 output
            {
                "Name": "File Group",
                "OutputGroupSettings": {
                    "Type": "FILE_GROUP_SETTINGS",
                    "FileGroupSettings": {"Destination": f"{dest}/video/"}
                },
                "Outputs": [{
                    "ContainerSettings": {"Container": "MP4"},
                    "VideoDescription": {
                        "CodecSettings": {
                            "Codec": "H_264",
                            "H264Settings": {
                                "RateControlMode": "QVBR",
                                "SceneChangeDetect": "TRANSITION_DETECTION",
                                "MaxBitrate": 5000000
                            }
                        }
                    },
                    "AudioDescriptions": [{
                        "CodecSettings": {
                            "Codec": "AAC",
                            "AacSettings": {"Bitrate": 128000, "CodingMode": "CODING_MODE_2_0", "SampleRate": 48000}
                        }
                    }]
                }]
            },
            # Thumbnails as frame captures (JPEGs)
            {
                "Name": "Thumbnails",
                "OutputGroupSettings": {
                    "Type": "FILE_GROUP_SETTINGS",
                    "FileGroupSettings": {"Destination": f"{dest}/thumbnails/"}  # files will be capture00001.jpg etc.
                },
                "Outputs": [{
                    "ContainerSettings": {"Container": "RAW"},
                    "VideoDescription": {
                        "CodecSettings": {
                            "Codec": "FRAME_CAPTURE",
                            "FrameCaptureSettings": {
                                "FramerateNumerator": 1, "FramerateDenominator": 1,
                                "MaxCaptures": 3, "Quality": 80
                            }
                        }
                    }
                }]
            }
        ]
    }

    job = mc.create_job(
        Role=MEDIACONVERT_ROLE_ARN,
        Settings=job_settings,
        Tags={"videoId": video_id}
    )

    event.update({
        "videoId": video_id,
        "mcJobId": job["Job"]["Id"],
        "processedBucket": PROCESSED_BUCKET
    })
    return event
