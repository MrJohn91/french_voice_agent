# 🚀 French Voice Agent - Deployment Guide

## 📋 Pre-Deployment Checklist

### 1. **API Keys Setup** (Required)

Update your `.env` file with real credentials:

```bash
# LiveKit (Get from: https://console.livekit.io)
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxx

# Deepgram (Get from: https://console.deepgram.com)
DEEPGRAM_API_KEY=xxxxxxxxxxxxx

# OpenAI (Get from: https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# Google Calendar - Already configured ✅
GOOGLE_CREDENTIALS_FILE=/Users/vee/Desktop/French Voice_Agent/google_credential.json
GOOGLE_CALENDAR_ID=primary

# Email (Optional - for confirmations)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# SMS (Optional - Twilio)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+33xxxxxxxxx
```

### 2. **Install Dependencies**

```bash
cd "/Users/vee/Desktop/French Voice_Agent"
pip install -r requirements.txt
```

### 3. **Test Locally**

```bash
# Test the voice agent
python agent/voice_agent.py dev

# Or use LiveKit CLI
livekit-cli create-token \
  --api-key $LIVEKIT_API_KEY \
  --api-secret $LIVEKIT_API_SECRET \
  --join --room test-room --identity test-user
```

---

## ☁️ Cloud Deployment Options

### **Option 1: LiveKit Cloud (Recommended)**

1. **Build and push Docker image:**
```bash
docker build -t french-voice-agent .
docker tag french-voice-agent your-registry/french-voice-agent:latest
docker push your-registry/french-voice-agent:latest
```

2. **Deploy to LiveKit Cloud:**
```bash
# Using LiveKit CLI
livekit-cli deploy create \
  --name french-voice-agent \
  --image your-registry/french-voice-agent:latest \
  --env-file .env
```

3. **Configure auto-scaling:**
```bash
livekit-cli deploy update french-voice-agent \
  --min-replicas 1 \
  --max-replicas 10
```

### **Option 2: AWS ECS/Fargate**

1. **Create ECR repository:**
```bash
aws ecr create-repository --repository-name french-voice-agent
```

2. **Push image:**
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
docker tag french-voice-agent:latest your-account.dkr.ecr.us-east-1.amazonaws.com/french-voice-agent:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/french-voice-agent:latest
```

3. **Create ECS task definition** with environment variables from `.env`

### **Option 3: Google Cloud Run**

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/your-project/french-voice-agent
gcloud run deploy french-voice-agent \
  --image gcr.io/your-project/french-voice-agent \
  --platform managed \
  --region europe-west1 \
  --env-vars-file .env
```

---

## 🧪 Testing in LiveKit Playground

### **Step 1: Start Your Agent**
```bash
python agent/voice_agent.py dev
```

### **Step 2: Open LiveKit Playground**
1. Go to: https://agents-playground.livekit.io
2. Enter your LiveKit credentials:
   - URL: `wss://your-project.livekit.cloud`
   - API Key: Your key
   - API Secret: Your secret

### **Step 3: Test French Conversation**
Speak in French:
- "Bonjour, je voudrais prendre un rendez-vous"
- "Demain à 14 heures"
- "Marie Dubois"
- "06 12 34 56 78"
- "marie.dubois@email.com"

---

## 📊 Monitoring & Logs

### **View Logs:**
```bash
# Local logs
tail -f logs/voice_agent.log

# Docker logs
docker logs -f french-voice-agent

# LiveKit Cloud logs
livekit-cli logs french-voice-agent
```

### **Monitor Performance:**
- LiveKit Dashboard: https://console.livekit.io
- Check latency metrics
- Monitor concurrent connections
- Track API usage

---

## 🔧 Configuration Tips

### **Optimize Latency:**
```bash
# Use faster TTS model
OPENAI_TTS_MODEL=tts-1  # Instead of tts-1-hd

# Adjust voice speed
OPENAI_TTS_VOICE=alloy
```

### **Business Hours:**
```bash
BUSINESS_HOURS=09:00-17:00  # Adjust as needed
APPOINTMENT_DURATION=30      # Minutes
```

---

## 🚨 Troubleshooting

### **Issue: "Calendar service not available"**
✅ **Fix:** Verify `google_credential.json` path in `.env`

### **Issue: "Deepgram API error"**
✅ **Fix:** Check DEEPGRAM_API_KEY is valid

### **Issue: "High latency (>2s)"**
✅ **Fix:** 
- Use `tts-1` instead of `tts-1-hd`
- Check internet connection
- Deploy closer to users (EU region for French)

### **Issue: "Email/SMS not sending"**
✅ **Fix:** Configure SMTP and Twilio credentials (optional feature)

---

## 💰 Cost Estimates

### **Per 1000 Conversations (~5 min each):**
- LiveKit: $10-20
- Deepgram STT: $15-25
- OpenAI GPT-4o-mini: $5-10
- OpenAI TTS: $15-30
- **Total: ~$45-85/1000 conversations**

### **Monthly (1000 conversations):**
- Infrastructure: $50-100
- APIs: $45-85
- **Total: ~$95-185/month**

---

## ✅ Deployment Checklist

- [ ] All API keys configured in `.env`
- [ ] Google Calendar credentials working
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] FFmpeg installed (for audio processing)
- [ ] Tested locally with `python agent/voice_agent.py dev`
- [ ] Docker image built and pushed
- [ ] Environment variables set in cloud platform
- [ ] Monitoring and logging configured
- [ ] Test call completed successfully

---

## 📞 Support

For issues or questions:
1. Check logs first
2. Verify all API keys are valid
3. Test each component individually
4. Review LiveKit documentation: https://docs.livekit.io

---

**Ready to deploy! 🚀**
