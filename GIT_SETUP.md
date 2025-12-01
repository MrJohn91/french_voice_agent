# 🔗 Git Repository Setup

## Repository: https://github.com/MrJohn91/french_voice_agent.git

## 🚀 Quick Setup

### **Option 1: Fresh Clone (Recommended if starting fresh)**
```bash
cd ~/Desktop
rm -rf "French Voice_Agent"  # Remove local copy
git clone https://github.com/MrJohn91/french_voice_agent.git
cd french_voice_agent
```

### **Option 2: Connect Existing Project**
```bash
cd "/Users/vee/Desktop/French Voice_Agent"

# Initialize git if not already
git init

# Add remote
git remote add origin https://github.com/MrJohn91/french_voice_agent.git

# Pull existing content (if any)
git pull origin main --allow-unrelated-histories

# Or force push your local version
git add .
git commit -m "Initial commit: French Voice Agent with appointment booking"
git branch -M main
git push -u origin main --force
```

## 📤 Push Your Code

```bash
cd "/Users/vee/Desktop/French Voice_Agent"

# Stage all files
git add .

# Commit
git commit -m "Add French Voice Agent with LiveKit, Deepgram, and Google Calendar"

# Push to GitHub
git push origin main
```

## 🔐 Important: Protect Sensitive Files

Your `.gitignore` is already configured to exclude:
- ✅ `.env` (API keys)
- ✅ `google_credential.json` (Google credentials)
- ✅ `__pycache__/` (Python cache)
- ✅ `venv/` (Virtual environment)

**Never commit these files!**

## 📋 Recommended Commit Structure

```bash
# Initial setup
git add README.md requirements.txt .env.example .gitignore
git commit -m "docs: Add project documentation and dependencies"

# Core agent
git add agent/ config/
git commit -m "feat: Add French voice agent with LiveKit integration"

# Deployment
git add Dockerfile DEPLOYMENT.md start.sh
git commit -m "deploy: Add Docker and deployment configuration"

# Push all
git push origin main
```

## 🌿 Branch Strategy

```bash
# Create development branch
git checkout -b development
git push -u origin development

# Create feature branches
git checkout -b feature/calendar-integration
git checkout -b feature/sms-notifications
```

## 🔄 Sync with Remote

```bash
# Pull latest changes
git pull origin main

# Push your changes
git push origin main
```

## 📊 Check Status

```bash
# See what's changed
git status

# See commit history
git log --oneline

# See remote URL
git remote -v
```

## ⚠️ Before First Push

1. **Verify .gitignore is working:**
```bash
git status
# Should NOT see: .env, google_credential.json, __pycache__
```

2. **Remove sensitive files if accidentally staged:**
```bash
git rm --cached .env
git rm --cached google_credential.json
```

3. **Update .env.example with placeholder values** (already done ✅)

## 🎯 Ready to Push!

```bash
cd "/Users/vee/Desktop/French Voice_Agent"
git add .
git commit -m "Initial commit: French Voice Agent for appointment booking"
git push -u origin main
```
