# Sally Love Real Estate Voice Agent System

✅ **AI-powered voice automation system** for real estate operations using Vapi.ai, BoldTrail CRM, and Stellar MLS.

## 🎯 Overview

Intelligent voice agent system for Sally Love Real Estate that handles:
- Property inquiries (listings, availability, details)
- Buyer lead qualification and routing
- Seller lead capture and follow-up
- Agent information and routing
- Appointment scheduling
- Automated notifications and follow-ups

**Office**: 352-399-2010  
**Coverage**: 70+ Real Estate Agents  
**CRM**: BoldTrail  
**MLS**: Stellar MLS

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `VAPI_API_KEY` - Your Vapi.ai API key
- `BOLDTRAIL_API_KEY` - BoldTrail CRM API key
- `STELLAR_MLS_USERNAME` - Stellar MLS username
- `STELLAR_MLS_PASSWORD` - Stellar MLS password
- `TWILIO_ACCOUNT_SID` - Twilio account SID
- `TWILIO_AUTH_TOKEN` - Twilio auth token
- `WEBHOOK_BASE_URL` - Your public server URL

### 3. Run Server

```bash
# Using main.py
python main.py

# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Set Up Vapi Assistants

After deploying your server (with public URL), run:

```bash
python scripts/setup_vapi.py
```

## 📁 Project Structure

```
sally_love_voice_agent/
├── src/
│   ├── config/              # Configuration and settings
│   │   ├── __init__.py
│   │   └── settings.py      # Environment variables and config
│   ├── integrations/        # External service clients
│   │   ├── __init__.py
│   │   ├── boldtrail.py     # BoldTrail CRM client
│   │   ├── stellar_mls.py   # Stellar MLS client
│   │   ├── twilio_client.py # Twilio client
│   │   └── vapi_client.py   # Vapi.ai client
│   ├── functions/           # Vapi function handlers (tools)
│   │   ├── __init__.py
│   │   ├── check_property.py
│   │   ├── get_agent_info.py
│   │   ├── route_to_agent.py
│   │   ├── create_buyer_lead.py
│   │   ├── create_seller_lead.py
│   │   └── send_notification.py
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── vapi_models.py
│   │   ├── crm_models.py
│   │   └── mls_models.py
│   ├── webhooks/            # Webhook handlers
│   │   ├── __init__.py
│   │   ├── vapi_webhooks.py
│   │   └── crm_webhooks.py
│   ├── utils/               # Utilities
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── errors.py
│   │   └── validators.py
│   └── __init__.py
├── scripts/                 # Setup and utility scripts
│   ├── setup_vapi.py
│   ├── test_integrations.py
│   └── verify_setup.py
├── tests/                   # Test files
│   ├── __init__.py
│   ├── test_functions.py
│   └── test_integrations.py
├── logs/                    # Application logs
├── main.py                  # FastAPI application entry point
├── pyproject.toml          # Project dependencies
├── .env.example            # Environment variables template
├── .gitignore
└── README.md
```

## 🔧 Available Functions/Tools (Phase 1)

1. **check_property** - Search and retrieve property details from BoldTrail/MLS
2. **get_agent_info** - Get agent availability and contact information
3. **route_to_agent** - Transfer call to specific agent or escalate to broker
4. **create_buyer_lead** - Capture buyer information and preferences
5. **create_seller_lead** - Capture seller property information
6. **send_notification** - Send SMS/email notifications to Sally & Jeff

**Note:** Appointment scheduling will be added in Phase 2. For now, agents will contact buyers to arrange showings.

## 📚 API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_functions.py
```

## 🚀 Deployment

1. Set `ENVIRONMENT=production` in `.env`
2. Set `WEBHOOK_BASE_URL` to your public server URL
3. Deploy to your hosting platform (Fly.io, Railway, Render, AWS, etc.)
4. Run `scripts/setup_vapi.py` to create assistants
5. Configure phone number in Vapi dashboard

## 📝 Business Rules

- Office hours: 9 AM - 5 PM EST (but agents accept calls anytime)
- Never discuss commission rates
- Never say negative things about people or properties
- Always be professional and helpful
- Collect detailed buyer/seller information
- Route calls to appropriate agents based on expertise

## 🔍 Support

Check logs in `logs/` directory for debugging.

## 📄 License

Proprietary - Sally Love Real Estate

