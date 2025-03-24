import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [transferStatus, setTransferStatus] = useState("");
  const [playlistUrl, setPlaylistUrl] = useState("");
  const [playlistTitle, setPlaylistTitle] = useState("");

  const handleTransfer = async () => {
    if (!playlistUrl) {
      setTransferStatus("Please enter a Spotify playlist URL.");
      return;
    }

    try {
      const response = await axios.post("http://localhost:8000/transfer", {
        spotify_url: playlistUrl,
        youtube_playlist_title: playlistTitle,
      });
      setTransferStatus(response.data.message);
    } catch (error) {
      setTransferStatus("Error transferring playlist.");
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h2>Transfer Playlist</h2>
        <input
          type="text"
          placeholder="Enter Spotify Playlist URL"
          value={playlistUrl}
          onChange={(e) => setPlaylistUrl(e.target.value)}
        />
        <br />
        <input
          type="text"
          placeholder="Enter YouTube Playlist Title"
          value={playlistTitle}
          onChange={(e) => setPlaylistTitle(e.target.value)}
        />
        <button onClick={handleTransfer}>Transfer to YouTube</button>
        <p>{transferStatus}</p>
      </div>
    </div>
  );
}

export default App;