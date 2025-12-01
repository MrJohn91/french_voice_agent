# French Voice Agent - Frontend

Frontend components for the French Voice Agent appointment booking system.

## Components

### Orb Component (`components/ui/orb.tsx`)
Animated 3D orb visualization that responds to voice agent states:
- **Idle**: Gentle pulsing animation
- **Listening**: Active listening state when user speaks
- **Talking**: Active talking state when agent responds

### Voice Call Interface (`components/voice-call-interface.tsx`)
LiveKit-powered voice call interface with:
- Real-time audio streaming
- Microphone mute/unmute controls
- Call end functionality
- Connection status display
- Automatic state detection (listening/talking)

## Usage

```tsx
import { Orb } from "@/components/ui/orb"
import { VoiceCallInterface } from "@/components/voice-call-interface"

// In your page component
const [agentState, setAgentState] = useState<"listening" | "talking" | null>(null)

<Orb 
  agentState={agentState}
  colors={["#3B82F6", "#1E40AF"]} // Blue theme for French agent
  className="w-full h-96"
/>

<VoiceCallInterface
  token={livekitToken}
  serverUrl="wss://french-voice-agent-glpfbk7m.livekit.cloud"
  roomName="appointment-room"
  onDisconnect={() => console.log("Call ended")}
  onStateChange={setAgentState}
/>
```

## Dependencies

```json
{
  "dependencies": {
    "@livekit/components-react": "^2.x",
    "@livekit/components-styles": "^1.x",
    "livekit-client": "^2.x",
    "@react-three/fiber": "^8.x",
    "@react-three/drei": "^9.x",
    "three": "^0.160.x",
    "lucide-react": "^0.x"
  }
}
```

## Color Customization

The orb supports custom color schemes:
- Default: `["#CADCFC", "#A0B9D1"]` (Light blue)
- French theme: `["#3B82F6", "#1E40AF"]` (Blue)
- Medical theme: `["#10B981", "#059669"]` (Green)

## Integration

1. Install dependencies
2. Copy components to your Next.js/React project
3. Configure LiveKit credentials
4. Implement token generation endpoint
5. Add orb and voice interface to your page
