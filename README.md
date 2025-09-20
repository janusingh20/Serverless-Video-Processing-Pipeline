# Serverless Video Processing Pipeline (Cloud/Infra)

**Upload a video → pipeline compresses, generates thumbnails, and transcribes → ready to stream.**

## 🧱 Architecture (MVP)
- **S3 (uploads bucket)** — raw user uploads.
- **S3 (processed bucket)** — H.264/AAC MP4 output (or HLS), public-read **via CloudFront**.
- **S3 (thumbnails bucket)** — extracted JPEG/PNG frames.
- **DynamoDB (Videos table)** — video metadata & job status.
- **API Gateway + Lambda** — issue **pre-signed S3 upload URLs**.
- **S3 Event → Lambda** — when an object lands in uploads, start the **Step Functions** workflow.
- **Step Functions** orchestrates:
  1) `transcode` (FFmpeg) → compressed output to processed bucket
  2) `thumbnail` (FFmpeg) → preview image(s) to thumbnails bucket
  3) `transcribe_start` (Amazon Transcribe) → starts job
  4) `transcribe_poll` (polls Transcribe) → on success, store transcript URI
  5) update DynamoDB status + CloudFront URL

> ⚠️ For FFmpeg in Lambda, attach an **FFmpeg Lambda Layer** (see README below). In production, consider **AWS Elemental MediaConvert** for large/long videos.

## 🛠 Stack
- **AWS SAM** (IaC) — template-driven deploys
- **Python 3.11 Lambdas** — boto3, FFmpeg via layer
- **React (Vite)** — simple upload UI using presigned URL
- **CloudFront** — CDN in front of processed output

## 🚀 Quick Start
### 1) Prereqs
- AWS CLI configured
- SAM CLI installed (`sam --version`)
- Node 18+ for the web app

### 2) Deploy Infra
```bash
cd infra
sam build
sam deploy --guided
```
Take note of the output API endpoint (for **request_upload_url**) and the **CloudFront domain**.

### 3) Run Web (local)
```bash
cd ../web
npm i
npm run dev
```
Create `.env` in `web/`:
```
VITE_API_BASE=https://<api-id>.execute-api.<region>.amazonaws.com/Prod
```

### 4) Upload Flow
1. Click **Upload** → UI asks backend for a **presigned PUT URL**.
2. Browser **PUTs** video directly to the **uploads** S3 bucket.
3. S3 **ObjectCreated** event triggers `on_upload` Lambda → starts the **Step Functions** job.
4. State machine runs `transcode` → `thumbnail` → `transcribe_start`/`transcribe_poll` → updates DynamoDB.
5. UI polls DynamoDB via the API (optional extension) to show status and the final **CloudFront playback URL**.

## 🧩 FFmpeg Layer
- Use a Lambda Layer providing static FFmpeg binaries (e.g., `ffmpeg`, `ffprobe` in `/opt/bin`).
- Example public layers exist on GitHub; or build one with AWS SAM/Container. Update the **`FFMPEG_LAYER_ARN`** parameter during `sam deploy --guided`.

## 🔒 IAM Notes
- Lambdas need S3 read/write to specific buckets, DynamoDB CRUD on the Videos table, and Transcribe permissions (`transcribe:StartTranscriptionJob`, `transcribe:GetTranscriptionJob`).
- State Machine needs permission to invoke tasks; `on_upload` needs to `StartExecution` on the state machine.

## 📦 What’s in here
```
infra/template.yaml        # SAM template with S3/DDB/APIGW/StepFunctions/Lambdas
lambdas/*                  # Python Lambda handlers (scaffold)
web/                       # Vite React app (upload UI)
```

## ✅ Next Steps
- Swap FFmpeg-Lambda for **MediaConvert** (robust, scalable) using `AWS::MediaConvert` job.
- Add **HLS packaging** and CloudFront **signed URLs**.
- Add **list/status API** to fetch video statuses from DynamoDB in the UI.
- Add **CORS** + Auth (Cognito) for a production portal.
