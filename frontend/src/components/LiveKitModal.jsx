import { useState, useCallback } from "react";
import { LiveKitRoom, RoomAudioRenderer } from "@livekit/components-react";
// Styles are included in @livekit/components-react, no separate package needed
import SimpleVoiceAssistant from "./SimpleVoiceAssistant";

const LiveKitModal = ({ setShowSupport }) => {
  const [isSubmittingName, setIsSubmittingName] = useState(true);
  const [name, setName] = useState("");
  const [token, setToken] = useState(null);

  const getToken = useCallback(async (userName) => {
    try {
      console.log("run")
      const response = await fetch(
        `/api/getToken?name=${encodeURIComponent(userName)}`
      );
      const token = await response.text();
      setToken(token);
      setIsSubmittingName(false);
    } catch (error) {
      console.error(error);
    }
  }, []);

    const handleNameSubmit = (e) => {
     e.preventDefault();
      if (name.trim()) {
        getToken(name);
      }
  };

  // Returns a text field with submit button which will prompt the user
  // to enter their name before initiating a conversation with the Voice Agent
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="support-room">
          {/* The form gets displayed if isSubmittingName is false */}
          {isSubmittingName ? (
            <form onSubmit={handleNameSubmit} className="name-form">
              <h2>Enter your name to connect with support</h2>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your name here"
                required
              />
              <button type="submit">Connect</button>
              <button
                type="button"
                className="cancel-button"
                onClick={() => setShowSupport(false)}
              >
                Cancel
              </button>
            </form>
          ) : token ? (
            <LiveKitRoom
              //serverUrl={import.meta.env.VITE_LIVEKIT_URL}
              serverUrl="wss://hkvoiceagent-ubn89q3a.livekit.cloud"
              //token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjcwMzMwMjMsImlkZW50aXR5IjoiaGsiLCJpc3MiOiJBUEl3RUp5amJObmdaTUoiLCJuYmYiOjE3NjcwMzIxMjMsInN1YiI6ImhrIiwidmlkZW8iOnsiY2FuUHVibGlzaCI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwicm9vbSI6ImhrIiwicm9vbUpvaW4iOnRydWV9fQ.KmmAROYtozrI3Hxzo5VWFQ7jWODCax5IeNmQI3M7Jb8"
              token={token}
              connect={true}
              video={false}
              audio={true}
              onDisconnected={() => {
                // If user disconnects, close support and show the name form again
                setShowSupport(false);
                setIsSubmittingName(true);
              }}
            >
              <RoomAudioRenderer />
              <SimpleVoiceAssistant />
            </LiveKitRoom>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default LiveKitModal;