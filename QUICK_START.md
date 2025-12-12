# 🚀 Quick Start - Sally Love Real Estate Voice Agent

## ⚡ 3-Minute Setup

### 1. Install Dependencies
```bash
cd sally_love_voice_agent
uv sync
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Start Server
```bash
python main.py
```

Server running at: **http://localhost:8000**

---

## 📌 Essential Commands

```bash
# Verify setup
python scripts/verify_setup.py

# Test integrations  
python scripts/test_integrations.py

# Run tests
pytest

# Create Vapi assistant (after deployment)
python scripts/setup_vapi.py

# View logs
tail -f logs/app.log
```

---

## 🎯 7 Function Endpoints

| Function | Endpoint | Purpose |
|----------|----------|---------|
| check_property | `/functions/check_property` | Search MLS properties |
| get_agent_info | `/functions/get_agent_info` | Get agent details |
| route_to_agent | `/functions/route_to_agent` | Transfer call to agent |
| create_buyer_lead | `/functions/create_buyer_lead` | Capture buyer info |
| create_seller_lead | `/functions/create_seller_lead` | Capture seller info |
| schedule_showing | `/functions/schedule_showing` | Book appointments |
| send_notification | `/functions/send_notification` | Send SMS/email |

---

## 📂 Project Structure

```
sally_love_voice_agent/
├── main.py                      # 🚀 Application entry point
├── src/
│   ├── config/settings.py       # ⚙️ Configuration
│   ├── integrations/            # 🔗 API clients
│   │   ├── vapi_client.py
│   │   ├── boldtrail.py
│   │   ├── stellar_mls.py
│   │   └── twilio_client.py
│   ├── functions/               # 🛠️ 7 Vapi tools
│   │   ├── check_property.py
│   │   ├── get_agent_info.py
│   │   ├── route_to_agent.py
│   │   ├── create_buyer_lead.py
│   │   ├── create_seller_lead.py
│   │   ├── schedule_showing.py
│   │   └── send_notification.py
│   ├── models/                  # 📋 Data models
│   ├── webhooks/                # 🔔 Event handlers
│   └── utils/                   # 🧰 Utilities
├── scripts/                     # 📜 Setup scripts
├── tests/                       # 🧪 Test suite
└── logs/                        # 📝 Application logs
```

---

## 🔑 Required API Keys

Add to `.env` file:

```env
# Vapi.ai
VAPI_API_KEY=your_vapi_key

# BoldTrail CRM  
BOLDTRAIL_API_KEY=your_boldtrail_key
BOLDTRAIL_ACCOUNT_ID=your_account_id

# Stellar MLS
STELLAR_MLS_USERNAME=your_username
STELLAR_MLS_PASSWORD=your_password

# Twilio
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+13523992010
```

---

## 🌐 Deployment Quick Steps

### Fly.io
```bash
flyctl launch
flyctl deploy
```

### Railway
```bash
railway init
railway up
```

### Docker
```bash
docker build -t sally-love-agent .
docker run -p 8000:8000 --env-file .env sally-love-agent
```

---

## 📖 Full Documentation

- **Setup Guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Requirements**: [REQUIREMENTS.md](REQUIREMENTS.md)
- **API Docs**: http://localhost:8000/docs (when running)
- **README**: [README.md](README.md)

---

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Server won't start | Check Python version (need 3.11+) |
| Function errors | Verify `.env` credentials are correct |
| Integration fails | Run `python scripts/test_integrations.py` |
| Vapi not calling | Check webhook URL is publicly accessible |

---

## ✅ Checklist

- [ ] Dependencies installed (`uv sync`)
- [ ] `.env` file configured with API keys
- [ ] Server starts successfully (`python main.py`)
- [ ] All tests pass (`pytest`)
- [ ] Integrations verified (`python scripts/test_integrations.py`)
- [ ] Deployed to production
- [ ] Vapi assistant created (`python scripts/setup_vapi.py`)
- [ ] Phone number configured in Vapi dashboard
- [ ] Test call completed successfully

---

## 📞 Support

**Business**: Sally Love Real Estate  
**Phone**: 352-399-2010  
**CRM**: BoldTrail  
**MLS**: Stellar MLS

Need help? Check logs in `logs/app.log`

