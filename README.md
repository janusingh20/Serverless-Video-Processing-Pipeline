# 🎬 Serverless Video Processing Pipeline (Cloud/Infra)

> A cloud-native pipeline that takes raw video uploads and automatically **transcodes, generates thumbnails, and runs transcription** — making videos ready for streaming at scale.  
> Designed as a **serverless MVP** to showcase AWS architecture, event-driven workflows, and infrastructure-as-code.

---

## 🧱 Architecture

- **S3 (Uploads Bucket)** — raw user uploads  
- **S3 (Processed Bucket)** — H.264/AAC MP4 (or HLS), served via CloudFront  
- **S3 (Thumbnails Bucket)** — extracted preview images  
- **DynamoDB (Videos Table)** — video metadata & job status  
- **API Gateway + Lambda** — issues presigned S3 upload URLs  
- **Step Functions** — orchestrates the full pipeline:
  1. **Transcode** (FFmpeg / MediaConvert) → processed bucket  
  2. **Thumbnail** (FFmpeg) → thumbnails bucket  
  3. **Transcribe** (Amazon Transcribe) → transcript stored & linked  
  4. **DynamoDB Update** → final CloudFront playback URL  

---

## 🛠️ Tech Stack

- **Infra**: AWS SAM (Infrastructure as Code)  
- **Lambdas**: Python 3.11 (boto3, FFmpeg via Lambda Layer)  
- **Frontend**: React (Vite) — upload UI with presigned URL  
- **Delivery**: CloudFront for CDN streaming  

---

## 🚀 How It Works

1. User uploads a video → UI requests presigned S3 URL.  
2. Browser PUTs file → S3 triggers Step Functions workflow.  
3. Workflow executes transcode → thumbnail → transcription tasks.  
4. Metadata is stored in DynamoDB; final assets served via CloudFront.  

---

## 📦 Project Structure

```
infra/template.yaml   # AWS SAM template (S3, DDB, API Gateway, Step Functions, Lambdas)
lambdas/*             # Python Lambda handlers
web/                  # React (Vite) frontend
```

---

## 🧩 Extensions / Next Steps

- Swap FFmpeg Lambda → AWS Elemental MediaConvert (production-grade scalability).  
- Add **HLS packaging** and signed CloudFront URLs.  
- Add list/status API → UI can display job history.  
- Add **CORS + Cognito Auth** for secure multi-user portal.  

---

## 📸 Screenshots (to add)
- Web upload UI  
- Step Functions execution graph  
