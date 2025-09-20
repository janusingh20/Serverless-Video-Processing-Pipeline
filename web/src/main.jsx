import React, { useState } from 'react'
import { createRoot } from 'react-dom/client'

const API_BASE = import.meta.env.VITE_API_BASE

function App() {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('')
  const [videoId, setVideoId] = useState('')

  async function requestUploadUrl(filename) {
    const res = await fetch(`${API_BASE}/request-upload-url`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ filename })
    })
    return res.json()
  }

  async function handleUpload() {
    if (!file) return
    setStatus('Requesting upload URL...')
    const { uploadUrl, videoId, s3Key } = await requestUploadUrl(file.name)
    setVideoId(videoId)
    setStatus('Uploading to S3...')
    const put = await fetch(uploadUrl, { method: 'PUT', headers: {'Content-Type':'video/mp4'}, body: file })
    if (!put.ok) { setStatus('Upload failed'); return }
    setStatus('Uploaded! Processing has started (transcode/thumbnail/transcribe).')
  }

  return (
    <div style={{maxWidth: 720, margin: '2rem auto', fontFamily:'ui-sans-serif'}}>
      <h1>Serverless Video Pipeline</h1>
      <p>Upload a .mp4 file. The pipeline will transcode, thumbnail, and transcribe it.</p>
      <input type="file" accept="video/mp4" onChange={e => setFile(e.target.files?.[0])} />
      <button onClick={handleUpload} disabled={!file} style={{marginLeft: 12}}>Upload</button>
      <p><strong>Status:</strong> {status}</p>
      {videoId && <p>Video ID: <code>{videoId}</code></p>}
    </div>
  )
}

createRoot(document.getElementById('root')).render(<App />)
