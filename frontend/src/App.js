import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [transferStatus, setTransferStatus] = useState("");
  const [playlistUrl, setPlaylistUrl] = useState("");
  const [playlistTitle, setPlaylistTitle] = useState("");

  const handleTransfer = async () => {
    if (!playlistUrl) {
      setTransferStatus("Please enter a valid Spotify playlist URL.");
      return;
    }

    try {
      const response = await axios.post("http://localhost:8000/transfer", {
        spotify_url: playlistUrl,
        youtube_playlist_title: playlistTitle,
      });
      setTransferStatus(response.data.message);

      if (response.status === 200) {
        setPlaylistUrl("");
        setPlaylistTitle("");
        setTransferStatus("Spotify playlist transferred successfully. Redirecting to YouTube playlist...");
        await new Promise((resolve) => setTimeout(resolve, 3000));
        // open a new tab and redirect to the YouTube playlist
        window.open("https://www.youtube.com/feed/playlists", "_blank");

        setTimeout(() => {
          setTransferStatus("");
        }, 5000);
      }

    } catch (error) {
      setTransferStatus("Error transferring playlist. Check your URL and try again.");
    }
  };

  return (
    <div>
      <div className="container">
        <div className="card">
          <h2>Spotify -> YouTube = SpoYT </h2>
          <p>Duplicate your Spotify playlist to YouTube.</p>

          <h3>Spotify Playlist URL*</h3>
          <p>Enter the URL of the Spotify playlist you want to transfer to YouTube.</p>
          <input
            type="text"
            placeholder="Enter Spotify Playlist URL"
            value={playlistUrl}
            onChange={(e) => setPlaylistUrl(e.target.value)}
          />
          <br />
          <h3>YouTube Playlist Title (optional)</h3>
          <p>Enter the title of the new YouTube playlist.</p>
          <input
            type="text"
            placeholder="Enter YouTube Playlist Title"
            value={playlistTitle}
            onChange={(e) => setPlaylistTitle(e.target.value)}
          />
          <button onClick={handleTransfer}>Transfer to YouTube</button>
          <h2>{transferStatus}</h2>
        </div>

      </div>

      <div className='footer'><center>SpoYT © 2025 Created by: Aditi Killedar
        <br></br>Find me on <a href='https://www.linkedin.com/in/aditikilledar'>LinkedIn!</a> </center></div>
    </div>

  );
}

export default App;