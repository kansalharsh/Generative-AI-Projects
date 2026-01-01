import {
  useVoiceAssistant,
  BarVisualizer,
  VoiceAssistantControlBar,
  useTranscriptions, // Use the singular version for your own track
  useLocalParticipant,
} from "@livekit/components-react";
import { useMemo } from "react";
import "./SimpleVoiceAssistant.css";

const SimpleVoiceAssistant = () => {
  // 1. Get Agent state and Agent-only transcriptions
  const { state, audioTrack, agentTranscriptions } = useVoiceAssistant();
  const { localParticipant } = useLocalParticipant();

  // 2. Targeted Hook: Get transcriptions ONLY for your microphone
  // This bypasses the identity issue because it's bound to the track itself
  const { segments: userTranscriptions } = useTranscriptions({
    trackRef: localParticipant.microphoneTrack,
  });

  // 3. Merge and Sort by timestamp
  const messages = useMemo(() => {
    const agentMsgs = (agentTranscriptions || []).map((t) => ({
      id: t.id,
      text: t.text,
      type: "agent",
      timestamp: t.firstReceivedTime,
    }));

    const userMsgs = (userTranscriptions || []).map((t) => ({
      id: t.id,
      text: t.text,
      type: "user",
      timestamp: t.firstReceivedTime,
    }));

    return [...agentMsgs, ...userMsgs].sort((a, b) => a.timestamp - b.timestamp);
  }, [agentTranscriptions, userTranscriptions]);

  return (
    <div className="voice-assistant-container">
      <div className="visualizer-container">
        <BarVisualizer state={state} barCount={7} trackRef={audioTrack} />
      </div>
      <div className="control-section">
        <VoiceAssistantControlBar />
        <div className="conversation">
          {messages.map((msg) => (
            <Message key={msg.id} type={msg.type} text={msg.text} />
          ))}
        </div>
      </div>
    </div>
  );
};

// Message component remains the same
const Message = ({ type, text }) => (
  <div className={`message message-${type}`}>
    <strong className={`message-header-${type}`}>
      {type === "agent" ? "Agent: " : "You: "}
    </strong>
    <span className="message-text">{text}</span>
  </div>
);

export default SimpleVoiceAssistant;