# 👋 Welcome to Sally Love Real Estate Voice Agent!

## 🎯 What You Have

A **complete Python FastAPI voice agent system** for Sally Love Real Estate with:

✅ **6 Function Tools** (check property, get agent info, route calls, create leads, send notifications - Phase 1)  
✅ **4 Integrations** (Vapi.ai, BoldTrail CRM, Stellar MLS, Twilio)  
✅ **Full Project Structure** (main.py, src/, scripts/, tests/)  
✅ **Setup Scripts** (verify, test, deploy)  
✅ **Documentation** (README, setup guide, requirements)  
✅ **Deployment Ready** (Docker, Fly.io, Railway)

---

## 🚀 Next Steps (Choose Your Path)

### Option A: Quick Local Test (5 minutes)

```bash
# 1. Install dependencies
uv sync

# 2. Create .env file
cp .env.example .env
# Edit .env with your API keys

# 3. Start server
python main.py

# 4. Visit: http://localhost:8000/docs
```

### Option B: Full Setup (30 minutes)

```bash
# 1. Verify everything
python scripts/verify_setup.py

# 2. Test integrations
python scripts/test_integrations.py

# 3. Run tests
pytest

# 4. Deploy to production

# 5. Configure Vapi assistant in dashboard
# Go to https://dashboard.vapi.ai and configure your assistant manually
# Copy system prompt from VAPI_SYSTEM_PROMPT.md
```

### Option C: Jump to Documentation

- 📖 [QUICK_START.md](QUICK_START.md) - 3-minute guide
- 📚 [SETUP_GUIDE.md](SETUP_GUIDE.md) - Complete setup instructions
- 📋 [REQUIREMENTS.md](REQUIREMENTS.md) - Business requirements & specs
- 📘 [README.md](README.md) - Project overview

---

## 🔑 What You Need

### API Credentials

1. **Vapi.ai** - Get from https://dashboard.vapi.ai
2. **BoldTrail CRM** - Your CRM API key
3. **Stellar MLS** - Your MLS credentials  
4. **Twilio** - Get from https://console.twilio.com

Add them to `.env` file (copy from `.env.example`)

---

## 📁 Project Overview

```
main.py                    ← START HERE (entry point)
│
├── src/functions/         ← 6 Vapi tools (Phase 1)
│   ├── check_property.py
│   ├── get_agent_info.py
│   ├── route_to_agent.py
│   ├── create_buyer_lead.py
│   ├── create_seller_lead.py
│   └── send_notification.py
│
├── src/integrations/      ← API clients
│   ├── vapi_client.py
│   ├── boldtrail.py
│   ├── stellar_mls.py
│   └── twilio_client.py
│
├── src/models/            ← Data models (Pydantic)
├── src/webhooks/          ← Event handlers
├── src/utils/             ← Helpers (logging, errors, validators)
└── scripts/               ← Setup & testing scripts
```

---

## 🎨 Architecture

Based on the HVAC project structure you provided, this follows the same proven pattern:

```
Voice Call → Vapi.ai → Your FastAPI Functions → CRM/MLS/Twilio
                ↓
         Call Recording
         Transcription
         Lead Capture
```

---

## 🛠️ The 6 Functions (Phase 1)

Each function is a separate Python file in `src/functions/`:

| # | Function | File | Purpose |
|---|----------|------|---------|
| 1 | check_property | `check_property.py` | Search MLS listings |
| 2 | get_agent_info | `get_agent_info.py` | Get agent details |
| 3 | route_to_agent | `route_to_agent.py` | Transfer to agent |
| 4 | create_buyer_lead | `create_buyer_lead.py` | Capture buyer |
| 5 | create_seller_lead | `create_seller_lead.py` | Capture seller |
| 6 | send_notification | `send_notification.py` | Send SMS/email |

Each function:
- ✅ Has its own FastAPI router
- ✅ Has request/response models
- ✅ Includes error handling
- ✅ Logs all activity
- ✅ Returns voice-friendly responses

---

## 🧪 Testing

```bash
# Quick test
curl http://localhost:8000/health

# Full test suite
pytest

# Test specific function
curl -X POST http://localhost:8000/functions/check_property \
  -H "Content-Type: application/json" \
  -d '{"city":"Ocala","state":"FL"}'
```

---

## 📊 What's Different from HVAC Project?

### Same Structure ✅
- main.py entry point
- src/ directory organization
- Functions in separate files
- Integration clients
- Webhook handlers

### Real Estate Specific 🏠
- **BoldTrail CRM** instead of GoHighLevel
- **Stellar MLS** integration for property data
- Buyer/seller lead flows
- Property showing scheduling
- 70+ agent routing logic

---

## 🎯 Key Files to Customize

1. **`src/config/settings.py`** - Configuration
2. **`VAPI_SYSTEM_PROMPT.md`** - System prompt for Vapi assistant (copy to dashboard)
3. **`src/functions/*.py`** - Function logic
4. **`.env`** - Your API credentials

---

## 💡 Tips

1. **Start with one function** - Test `check_property` first
2. **Check logs** - Everything is logged to `logs/app.log`
3. **Use API docs** - Visit `/docs` when server is running
4. **Test integrations** - Before full deployment
5. **Read transcripts** - Improve based on real calls

---

## 🆘 Need Help?

1. Check `logs/app.log` for errors
2. Run `python scripts/verify_setup.py`
3. Run `python scripts/test_integrations.py`
4. Visit http://localhost:8000/docs for API documentation
5. Review the Sally Love requirements in `REQUIREMENTS.md`

---

## ✅ Your Action Items

- [ ] **Install**: `uv sync` 
- [ ] **Configure**: Copy `.env.example` to `.env` and add API keys
- [ ] **Verify**: `python scripts/verify_setup.py`
- [ ] **Test**: `python scripts/test_integrations.py`
- [ ] **Run**: `python main.py`
- [ ] **Deploy**: To your production server
- [ ] **Configure Vapi**: Set up assistant in Vapi dashboard (use prompt from `VAPI_SYSTEM_PROMPT.md`)
- [ ] **Test Call**: Make a test call to verify

---

## 🎉 You're Ready!

Everything is set up following the HVAC project pattern you know. The structure is familiar, the code is documented, and you have all 6 Phase 1 functions ready to go.

**Happy coding! 🚀**

_Note: Appointment scheduling (Phase 2) will be added after initial testing._

---

*For detailed information, see [SETUP_GUIDE.md](SETUP_GUIDE.md)*

