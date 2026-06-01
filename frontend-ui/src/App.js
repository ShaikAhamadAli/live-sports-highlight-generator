import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [clips, setClips] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");

  const fetchClips = () => {
    fetch("http://localhost:5000/api/clips")
      .then(res => res.json())
      .then(data => {
        if (data.clips.length > 0) {
          setClips(data.clips);
          setUploading(false);
          setMessage("Highlights generated successfully!");
        }
      })
      .catch(err => console.error(err));
  };

  useEffect(() => {
    fetchClips();
  }, []);

  const uploadVideo = async (e) => {
    e.preventDefault();
    const file = e.target.video.files[0];
    if (!file) return;

    setUploading(true);
    setMessage("Processing video, please wait...");

    const formData = new FormData();
    formData.append("video", file);

    await fetch("http://localhost:5000/upload", {
      method: "POST",
      body: formData
    });

    // Start polling every 3 seconds
    const interval = setInterval(() => {
      fetchClips();
    }, 3000);

    // Stop polling after 2 minutes (safety)
    setTimeout(() => clearInterval(interval), 120000);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Sports Highlight Generator</h1>
        <p>Upload a sports video and get AI-generated highlights</p>
      </header>

      <form className="upload-box" onSubmit={uploadVideo}>
        <input type="file" name="video" accept="video/*" required />
        <button type="submit" disabled={uploading}>
          {uploading ? "Processing..." : "Upload & Generate"}
        </button>
      </form>

      {message && <p style={{ marginTop: "10px" }}>{message}</p>}

      <div className="grid">
        {clips.map((clip, i) => (
          <div className="card" key={i}>
            <video
              controls
              src={`http://localhost:5000/clips/${clip}`}
            />
            <div className="card-footer">Highlight {i + 1}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
