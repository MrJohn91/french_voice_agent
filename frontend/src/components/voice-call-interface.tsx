"use client";

import { useState, useEffect, useRef } from "react";
import { Room, RoomEvent, RemoteParticipant, Track, ConnectionState, Participant } from "livekit-client";
import { LiveKitRoom, RoomAudioRenderer, useRoomContext } from "@livekit/components-react";
import "@livekit/components-styles";
import { Mic, MicOff, PhoneOff, Loader2 } from "lucide-react";

interface VoiceCallInterfaceProps {
  token: string;
  serverUrl: string;
  roomName: string;
  onDisconnect: () => void;
  onStateChange?: (state: "listening" | "talking" | "thinking" | null) => void;
}

function VoiceCallControls({
  room,
  onDisconnect,
  onStateChange,
}: {
  room: Room;
  onDisconnect: () => void;
  onStateChange?: (state: "listening" | "talking" | "thinking" | null) => void;
}) {
  const [isMuted, setIsMuted] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const userSpeakingRef = useRef(false);
  const agentSpeakingRef = useRef(false);

  const updateOrbState = useRef(() => {
    if (agentSpeakingRef.current) {
      onStateChange?.("talking");
    } else if (userSpeakingRef.current) {
      onStateChange?.("listening");
    } else {
      onStateChange?.(null);
    }
  });

  useEffect(() => {
    if (!room) return;

    const handleConnectionStateChange = (state: ConnectionState) => {
      setIsConnected(state === ConnectionState.Connected);
      if (state === ConnectionState.Connected) {
        onStateChange?.(null);
      }
    };

    const checkUserSpeaking = () => {
      if (!room) return;

      const localParticipant = room.localParticipant;
      const audioTracks = Array.from(localParticipant.audioTrackPublications.values());
      const isMuted = audioTracks.length > 0 && audioTracks[0]?.track?.isMuted;
      const isSpeaking = localParticipant.isSpeaking &&
        localParticipant.isMicrophoneEnabled &&
        !isMuted;

      const previousUserSpeaking = userSpeakingRef.current;
      userSpeakingRef.current = isSpeaking || false;

      if (previousUserSpeaking !== userSpeakingRef.current || !agentSpeakingRef.current) {
        updateOrbState.current();
      }
    };

    const userSpeakingInterval = setInterval(checkUserSpeaking, 100);

    const handleRemoteTrackSubscribed = (track: Track, publication: any, participant: RemoteParticipant) => {
      if (track.kind === "audio" && !participant.isLocal) {
        const isAgent = participant.identity.toLowerCase().includes("agent") ||
          participant.name?.toLowerCase().includes("agent") ||
          participant.identity.toLowerCase().includes("alex");

        if (isAgent && track.mediaStreamTrack) {
          if (!audioRef.current) {
            audioRef.current = new Audio();
            audioRef.current.srcObject = new MediaStream([track.mediaStreamTrack]);
            audioRef.current.play().catch(e => console.error("Error playing audio:", e));
          } else {
            audioRef.current.srcObject = new MediaStream([track.mediaStreamTrack]);
          }

          const checkAgentSpeaking = () => {
            if (audioRef.current) {
              const isPlaying = !audioRef.current.paused &&
                audioRef.current.currentTime > 0 &&
                !audioRef.current.ended;

              agentSpeakingRef.current = isPlaying;
            } else {
              agentSpeakingRef.current = false;
            }
            updateOrbState.current();
          };

          const agentSpeakingInterval = setInterval(checkAgentSpeaking, 100);
          return () => clearInterval(agentSpeakingInterval);
        }
      }
    };

    const handleRemoteTrackUnsubscribed = (track: Track, publication: any, participant: RemoteParticipant) => {
      if (track.kind === "audio" && !participant.isLocal) {
        agentSpeakingRef.current = false;
        updateOrbState.current();
      }
    };

    const handleActiveSpeakersChanged = (speakers: Participant[]) => {
      if (!room) return;

      const remoteSpeakers = speakers.filter(p => !p.isLocal) as RemoteParticipant[];
      const agentIsSpeaking = remoteSpeakers.some(p => {
        const identity = (p.identity || "").toLowerCase();
        const name = (p.name || "").toLowerCase();
        return identity.includes("agent") ||
          name.includes("agent") ||
          identity.includes("alex") ||
          name.includes("alex");
      });

      const localParticipantIsSpeaking = room.localParticipant.isSpeaking;
      const userIsInSpeakers = speakers.some(p => p.isLocal);
      const userIsSpeaking = localParticipantIsSpeaking || userIsInSpeakers;

      agentSpeakingRef.current = agentIsSpeaking;
      userSpeakingRef.current = userIsSpeaking && !agentIsSpeaking;

      updateOrbState.current();
    };

    room.on(RoomEvent.ConnectionStateChanged, handleConnectionStateChange);
    room.on(RoomEvent.TrackSubscribed, handleRemoteTrackSubscribed);
    room.on(RoomEvent.TrackUnsubscribed, handleRemoteTrackUnsubscribed);
    room.on(RoomEvent.ActiveSpeakersChanged, handleActiveSpeakersChanged);

    return () => {
      clearInterval(userSpeakingInterval);
      room.off(RoomEvent.ConnectionStateChanged, handleConnectionStateChange);
      room.off(RoomEvent.TrackSubscribed, handleRemoteTrackSubscribed);
      room.off(RoomEvent.TrackUnsubscribed, handleRemoteTrackUnsubscribed);
      room.off(RoomEvent.ActiveSpeakersChanged, handleActiveSpeakersChanged);
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.srcObject = null;
      }
    };
  }, [room]);

  const toggleMute = async () => {
    if (!room) return;

    await room.localParticipant.setMicrophoneEnabled(isMuted);
    setIsMuted(!isMuted);

    if (isMuted) {
      userSpeakingRef.current = room.localParticipant.isMicrophoneEnabled;
    } else {
      userSpeakingRef.current = false;
    }

    updateOrbState.current();
  };

  const handleEndCall = () => {
    if (room) {
      room.disconnect();
    }
    onDisconnect();
  };

  if (!room) {
    return null;
  }

  return (
    <>
      <audio ref={audioRef} autoPlay playsInline style={{ display: "none" }} />
      <div
        className="fixed bottom-8 left-1/2 transform -translate-x-1/2 pointer-events-auto"
        style={{ zIndex: 99999 }}
      >
        <div className="flex flex-col items-center gap-4 p-6 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 shadow-2xl">
          <div className="flex items-center gap-4">
            <button
              onClick={toggleMute}
              disabled={!isConnected}
              className="bg-white/20 hover:bg-white/30 border-white/30 text-white p-4 rounded-full"
            >
              {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>

            <button
              onClick={handleEndCall}
              className="bg-red-500 hover:bg-red-600 text-white p-4 rounded-full shadow-lg"
            >
              <PhoneOff className="w-5 h-5" />
            </button>
          </div>

          <p className="text-white text-sm font-medium">
            {isConnected ? "Connecté à Alex" : "Connexion..."}
          </p>
        </div>
      </div>
    </>
  );
}

function RoomAccessor({
  onRoomReady,
  onDisconnect,
  onStateChange,
}: {
  onRoomReady: (room: Room) => void;
  onDisconnect: () => void;
  onStateChange?: (state: "listening" | "talking" | "thinking" | null) => void;
}) {
  const room = useRoomContext();
  const roomSentRef = useRef(false);

  useEffect(() => {
    if (room) {
      if (!roomSentRef.current) {
        roomSentRef.current = true;
        onRoomReady(room);
      }

      if (room.state === ConnectionState.Connected) {
        onStateChange?.(null);
      }

      const handleConnected = () => {
        onStateChange?.(null);
      };

      const handleDisconnected = () => {
        onDisconnect();
      };

      room.on(RoomEvent.Connected, handleConnected);
      room.on(RoomEvent.Disconnected, handleDisconnected);

      return () => {
        room.off(RoomEvent.Connected, handleConnected);
        room.off(RoomEvent.Disconnected, handleDisconnected);
      };
    }
  }, [room, onRoomReady, onDisconnect, onStateChange]);

  return null;
}

export function VoiceCallInterface({
  token,
  serverUrl,
  roomName,
  onDisconnect,
  onStateChange,
}: VoiceCallInterfaceProps) {
  const [roomState, setRoomState] = useState<"connecting" | "connected" | "disconnected">("connecting");
  const [room, setRoom] = useState<Room | null>(null);

  const handleRoomReady = (roomInstance: Room) => {
    setRoomState("connected");
    setRoom(roomInstance);
  };

  const handleDisconnect = () => {
    setRoomState("disconnected");
    setRoom(null);
    onDisconnect();
  };

  return (
    <>
      <LiveKitRoom
        video={false}
        audio={true}
        token={token}
        serverUrl={serverUrl}
        connect={true}
        options={{
          adaptiveStream: true,
          dynacast: true,
        }}
        className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none"
        onConnected={() => {
          setRoomState("connected");
        }}
        onDisconnected={handleDisconnect}
      >
        <RoomAccessor
          onRoomReady={handleRoomReady}
          onDisconnect={handleDisconnect}
          onStateChange={onStateChange}
        />
        <RoomAudioRenderer />

        {roomState === "connecting" && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50 z-50 pointer-events-auto">
            <div className="text-center text-white">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
              <p>Connexion à Alex...</p>
            </div>
          </div>
        )}
      </LiveKitRoom>

      {roomState !== "disconnected" ? (
        room ? (
          <VoiceCallControls
            room={room}
            onDisconnect={onDisconnect}
            onStateChange={onStateChange}
          />
        ) : (
          <div
            className="fixed bottom-8 left-1/2 transform -translate-x-1/2 pointer-events-auto z-[99999]"
          >
            <div className="flex flex-col items-center gap-4 p-6 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 shadow-2xl">
              <button
                onClick={handleDisconnect}
                className="bg-red-500 hover:bg-red-600 text-white p-4 rounded-full shadow-lg"
              >
                <PhoneOff className="w-5 h-5" />
              </button>
              <p className="text-white text-sm font-medium">Connexion...</p>
            </div>
          </div>
        )
      ) : null}
    </>
  );
}
