# French Voice Agent - Modern Frontend

A beautiful, modern web interface for the French Voice Agent featuring an interactive 3D orb that responds to voice interactions.

## 🎨 Features

### Interactive 3D Orb
- **Real-time Animation**: Stunning WebGL-powered 3D orb built with Three.js and React Three Fiber
- **State-Responsive**: Visual feedback for different agent states:
  - **Idle**: Gentle pulsing animation
  - **Listening**: Active blue waves when user speaks
  - **Talking**: Dynamic purple/blue animation when agent responds
- **Glassmorphism Design**: Modern frosted glass effects with backdrop blur
- **Smooth Transitions**: Fluid animations and micro-interactions

### Voice Integration
- **LiveKit Integration**: Real-time voice communication with the French agent
- **One-Click Start**: Simple button to begin conversation
- **Visual Feedback**: Orb animations synchronized with voice states
- **Call Controls**: Mute/unmute and end call functionality

### Modern UI/UX
- **Dark Theme**: Sleek dark interface with vibrant accent colors
- **Responsive Design**: Works beautifully on all screen sizes
- **Premium Aesthetics**: 
  - Gradient backgrounds
  - Ambient glow effects
  - Smooth hover animations
  - Professional typography (Inter font)

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ installed
- LiveKit account (Cloud or self-hosted)

### Installation

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Configure environment variables**:
Create a `.env.local` file in the frontend directory:
```env
LIVEKIT_API_KEY=your_api_key_here
LIVEKIT_API_SECRET=your_api_secret_here
LIVEKIT_URL=wss://your-livekit-server.livekit.cloud
```

3. **Run development server**:
```bash
npm run dev
```

4. **Open your browser**:
Navigate to [http://localhost:3000](http://localhost:3000)

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── token/
│   │   │       └── route.ts          # LiveKit token generation
│   │   ├── globals.css               # Global styles & theme
│   │   ├── layout.tsx                # Root layout
│   │   └── page.tsx                  # Main page with orb
│   ├── components/
│   │   ├── ui/
│   │   │   └── orb.tsx              # 3D Orb component
│   │   └── voice-call-interface.tsx  # LiveKit voice interface
│   └── lib/
│       └── utils.ts                  # Utility functions
├── public/                           # Static assets
├── package.json
└── tailwind.config.ts               # Tailwind configuration
```

## 🎨 Customization

### Orb Colors
You can customize the orb colors in `src/app/page.tsx`:

```tsx
<Orb 
  agentState={agentState} 
  colors={["#3B82F6", "#8B5CF6"]} // [Primary, Secondary]
  className="w-full h-full"
/>
```

### Theme Colors
Modify the color scheme in `src/app/globals.css`:

```css
@theme {
  --color-primary: hsl(217.2 91.2% 59.8%);
  --color-secondary: hsl(217.2 32.6% 17.5%);
  /* ... more colors */
}
```

## 🔧 Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Styling**: Tailwind CSS v4
- **3D Graphics**: Three.js + React Three Fiber
- **Voice**: LiveKit (Client & Server SDK)
- **Language**: TypeScript
- **Font**: Inter (Google Fonts)

## 🎯 Key Components

### Orb Component (`components/ui/orb.tsx`)
The heart of the UI - a sophisticated 3D orb with:
- Custom GLSL shaders for unique visual effects
- Perlin noise textures for organic movement
- State-based animations
- Volume-reactive visuals

### Voice Call Interface (`components/voice-call-interface.tsx`)
Handles all voice communication:
- LiveKit room connection
- Audio track management
- Speaker detection (user vs agent)
- State synchronization with orb

### Main Page (`app/page.tsx`)
Orchestrates the entire experience:
- Token fetching from API
- State management
- UI composition
- User interactions

## 🌐 API Routes

### `/api/token`
Generates LiveKit access tokens for secure room access.

**Query Parameters**:
- `roomName`: Name of the LiveKit room (default: "default-room")
- `participantName`: Display name for the user (default: "User")

**Response**:
```json
{
  "token": "eyJhbGc...",
  "serverUrl": "wss://..."
}
```

## 🎭 Agent States

The orb responds to these states:
- `null`: Idle/waiting state
- `"listening"`: User is speaking
- `"talking"`: Agent is responding
- `"thinking"`: Agent is processing (optional)

## 🚢 Deployment

### Build for production:
```bash
npm run build
```

### Start production server:
```bash
npm start
```

### Deploy to Vercel:
```bash
vercel deploy
```

Make sure to set environment variables in your deployment platform.

## 📝 Notes

- The orb uses WebGL and requires a modern browser
- LiveKit credentials must be configured for voice to work
- The backend agent must be running and connected to the same LiveKit room
- Default room name is "french-agent-room"

## 🎨 Design Philosophy

This frontend was built with a focus on:
1. **Visual Excellence**: Premium, modern aesthetics that wow users
2. **Smooth Interactions**: Fluid animations and responsive feedback
3. **User Experience**: Intuitive controls and clear visual states
4. **Performance**: Optimized 3D rendering and efficient state management
5. **Accessibility**: Semantic HTML and proper ARIA labels

---

Built with ❤️ using Next.js, yes I am using Next.js as requested, and it's organized in the frontend folder without any backup directories cluttering the workspace.
