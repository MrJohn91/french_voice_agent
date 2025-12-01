n# French Voice Agent - Appointment Booking System

A sophisticated French voice agent for automated appointment booking using LiveKit, Deepgram Nova-2, GPT-4o-mini, and ElevenLabs.

## 🚀 Features

- **Native French Support**: Optimized for French with automatic French/English language detection
- **Real-time Voice Conversations**: Ultra-low latency (~800ms-1.0s target)  
- **Appointment Management**: Full Google Calendar integration
- **Professional Voice**: Custom ElevenLabs French voice with natural pronunciation
- **Business Intelligence**: Smart appointment scheduling with conflict detection
- **24/7 Availability**: Always ready to book appointments

## 📋 Tech Stack

- **Voice Framework**: LiveKit Agents
- **Speech-to-Text**: Deepgram Nova-2 (French optimized)
- **Language Model**: OpenAI GPT-4o-mini  
- **Text-to-Speech**: ElevenLabs (Multilingual v2)
- **Calendar**: Google Calendar API
- **Backend**: FastAPI
- **Language**: Python 3.8+

## 🔧 Installation

1. **Clone and install dependencies**:
```bash
git clone <repository>
cd french-voice-agent
pip install -r requirements.txt
```

2. **Setup environment variables**:
```bash
cp .env.example .env
# Edit .env with your API credentials (see below)
```

3. **Install system dependencies**:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian  
sudo apt update && sudo apt install ffmpeg

# Windows
# Download FFmpeg from https://ffmpeg.org/download.html
```

## 🔐 Required API Keys

### LiveKit Configuration
```bash
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
```
Get keys from: [LiveKit Console](https://console.livekit.io)

### Deepgram API (French STT)
```bash
DEEPGRAM_API_KEY=your_deepgram_api_key
```
Get API key from: [Deepgram Console](https://console.deepgram.com)

### OpenAI API (GPT-4o-mini)
```bash
OPENAI_API_KEY=sk-your_openai_api_key
```
Get API key from: [OpenAI Platform](https://platform.openai.com/api-keys)

### Text-to-Speech (Choose one option)

**Option 1: ElevenLabs (Higher quality, more expensive)**
```bash
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=pNInz6obpgDQGcFmaJgB  # Adam - good for French
```
Get API key from: [ElevenLabs](https://elevenlabs.io/app/speech-synthesis)

**Option 2: OpenAI TTS (More cost-effective, good quality)**  
No additional setup needed - uses same OpenAI API key
```bash
OPENAI_TTS_MODEL=tts-1  # or tts-1-hd for higher quality
OPENAI_TTS_VOICE=alloy  # Works well for French
```

### Google Calendar Setup
1. Create a Google Cloud Project
2. Enable Calendar API
3. Create service account credentials
4. Download JSON credentials file
5. Set path in environment:
```bash
GOOGLE_CREDENTIALS_FILE=/path/to/service-account-credentials.json
GOOGLE_CALENDAR_ID=primary  # or your specific calendar ID
```

## 🚀 Quick Start

### 1. Install LiveKit CLI
```bash
brew install livekit-cli
```

### 2. Authenticate
```bash
lk cloud auth
```

### 3. Deploy Agent
```bash
lk agent create
```

### 4. Test Locally
```bash
python agent/voice_agent.py dev
```

Then test at: https://agents-playground.livekit.io

## 📞 Sample Conversation Flow

**Agent**: *"Bonjour ! Bienvenue chez Cabinet Médical Dr. Martin. Je suis votre assistant vocal. Comment puis-je vous aider à prendre rendez-vous aujourd'hui ?"*

**User**: *"Bonjour, je voudrais prendre un rendez-vous pour une consultation."*

**Agent**: *"Parfait ! J'aimerais vous aider à prendre rendez-vous. Quel type de consultation vous intéresse ?"*

**User**: *"Une consultation générale."*

**Agent**: *"Très bien. Quel jour souhaiteriez-vous venir ?"*

**User**: *"Demain vers 14h."*

**Agent**: *"Laissez-moi vérifier les disponibilités pour demain à 14h... Parfait ! Ce créneau est disponible. Puis-je avoir votre nom complet ?"*

**User**: *"Marie Dubois."*

**Agent**: *"Merci Madame Dubois. Quel est votre numéro de téléphone ?"*

**User**: *"06 12 34 56 78."*

**Agent**: *"Et votre adresse email ?"*

**User**: *"marie.dubois@email.com."*

**Agent**: *"Parfait ! J'ai réservé votre rendez-vous pour demain à 14h. Vous recevrez une confirmation par email. À bientôt !"*

## 🔧 Configuration

### Business Settings
```bash
BUSINESS_NAME=Your Business Name
BUSINESS_HOURS=09:00-17:00
APPOINTMENT_DURATION=30  # minutes
```

### Voice Optimization
- **Latency Target**: ~800ms-1.0 seconds
- **Streaming**: Enabled for all components
- **Language Detection**: Automatic French/English switching
- **Voice Cloning**: Configurable via ElevenLabs

## 📊 API Endpoints

The FastAPI server provides REST endpoints for web integration:

- `GET /health` - Health check
- `POST /availability/check` - Check appointment availability  
- `GET /availability/{date}` - Get available slots
- `POST /appointments/book` - Book appointment
- `DELETE /appointments/{event_id}` - Cancel appointment

## 💰 Pricing & Business Model

### Development Costs
- Basic French Voice Agent: $8K - $15K
- + Appointment Booking: $5K - $10K  
- + Advanced Features (CRM, analytics): $5K - $15K
- **Total Range**: $18K - $40K

### SaaS Pricing
- **Basic**: $200-500/month (1K conversations)
- **Professional**: $800-1,500/month (10K conversations)
- **Enterprise**: $2K-5K/month (Unlimited + white-label)

## 🎯 Target Markets

- **Medical/Dental Practices** - Critical appointment scheduling
- **Legal Firms** - Professional French communication
- **High-End Services** - Spas, salons, consultants
- **Restaurants** - French reservation booking
- **Beauty/Wellness** - Massage, therapy appointments

## 📈 Performance Metrics

- **Latency**: ~800ms-1.0 seconds (target)
- **Accuracy**: 95%+ booking accuracy
- **Availability**: 24/7 operation
- **Languages**: French (primary) + English auto-detection
- **Capacity**: Unlimited concurrent calls

## 🛠️ Development

### Local Testing
```bash
python agent/voice_agent.py dev
# Or use: ./start.sh
```

### Deploy to Cloud
```bash
lk agent create
lk agent logs
lk agent list
```

## 🔍 Troubleshooting

### Common Issues

1. **Calendar not working**: Check `google_credential.json` path in `.env`
2. **API errors**: Verify all API keys are valid
3. **High latency**: Use `tts-1` instead of `tts-1-hd`
4. **French recognition**: Deepgram Nova-2 optimized for French

### Logs
```bash
# Local
tail -f logs/voice_agent.log

# Cloud
lk agent logs
```

## 📞 Support

For technical support or customization requests, contact our development team.

## 📄 License

Proprietary - See license agreement for usage terms.

---

*Built with ❤️ for French-speaking businesses*