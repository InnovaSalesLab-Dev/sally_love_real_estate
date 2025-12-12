# Sally Love Real Estate Voice Agent - Setup Guide

## 📋 Prerequisites

- Python 3.11 or higher
- `uv` package manager (recommended) or `pip`
- API credentials for:
  - Vapi.ai
  - BoldTrail CRM
  - Stellar MLS
  - Twilio

## 🚀 Quick Start (5 Minutes)

### 1. Clone and Install

```bash
# Navigate to project
cd sally_love_voice_agent

# Install dependencies
uv sync
# OR
pip install -e .
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

**Required credentials:**
- `VAPI_API_KEY` - From Vapi.ai dashboard
- `BOLDTRAIL_API_KEY` - From BoldTrail CRM
- `STELLAR_MLS_USERNAME` and `STELLAR_MLS_PASSWORD` - Your MLS credentials
- `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` - From Twilio console
- `WEBHOOK_BASE_URL` - Your public server URL (for production)

### 3. Verify Setup

```bash
python scripts/verify_setup.py
```

This checks:
- ✅ All required files are present
- ✅ Environment variables are set
- ✅ Configuration is valid

### 4. Test Integrations

```bash
python scripts/test_integrations.py
```

This tests connections to:
- Vapi.ai API
- BoldTrail CRM
- Stellar MLS
- Twilio

### 5. Start the Server

```bash
# Development mode (with auto-reload)
python main.py

# OR using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`

### 6. Set Up Vapi Assistant

**After deploying to production with a public URL:**

```bash
python scripts/setup_vapi.py
```

This creates the Vapi assistant with all 7 function integrations.

## 📚 API Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Available Functions/Tools

The voice agent has 7 functions:

1. **check_property** - Search MLS listings
   - Endpoint: `/functions/check_property`
   - Use: Find properties by address, price, bedrooms, etc.

2. **get_agent_info** - Get agent details
   - Endpoint: `/functions/get_agent_info`
   - Use: Find agents by name, specialty, or location

3. **route_to_agent** - Transfer call to agent
   - Endpoint: `/functions/route_to_agent`
   - Use: Connect caller to specific agent

4. **create_buyer_lead** - Capture buyer information
   - Endpoint: `/functions/create_buyer_lead`
   - Use: Record buyer preferences and contact info

5. **create_seller_lead** - Capture seller information
   - Endpoint: `/functions/create_seller_lead`
   - Use: Record property details for sellers

6. **schedule_showing** - Book appointments
   - Endpoint: `/functions/schedule_showing`
   - Use: Schedule property viewings

7. **send_notification** - Send SMS/email
   - Endpoint: `/functions/send_notification`
   - Use: Send confirmations and reminders

## 🌐 Deployment

### Option 1: Fly.io (Recommended)

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch app
flyctl launch

# Deploy
flyctl deploy

# Get public URL
flyctl info
```

### Option 2: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

### Option 3: Render

1. Connect your GitHub repository
2. Create a new Web Service
3. Set build command: `pip install -e .`
4. Set start command: `python main.py`
5. Add environment variables

### Option 4: Docker

```bash
# Build image
docker build -t sally-love-voice-agent .

# Run container
docker run -d -p 8000:8000 --env-file .env sally-love-voice-agent
```

## 🔐 Environment Variables

### Required for Production

```env
ENVIRONMENT=production
WEBHOOK_BASE_URL=https://your-domain.com

VAPI_API_KEY=your_vapi_key
BOLDTRAIL_API_KEY=your_boldtrail_key
STELLAR_MLS_USERNAME=your_mls_username
STELLAR_MLS_PASSWORD=your_mls_password
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+13523992010
```

## 📞 Vapi Phone Number Setup

After running `setup_vapi.py`:

1. Go to https://dashboard.vapi.ai
2. Navigate to "Phone Numbers"
3. Click "Buy a phone number" or use existing
4. Assign it to your assistant
5. Test by calling the number

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_functions.py -v
```

## 📊 Monitoring

### Logs

Logs are written to `logs/app.log`

```bash
# Watch logs in real-time
tail -f logs/app.log

# View last 100 lines
tail -n 100 logs/app.log

# Search logs
grep "ERROR" logs/app.log
```

### Health Checks

- Main health: `GET /health`
- Vapi webhooks: `GET /webhooks/vapi/health`
- CRM webhooks: `GET /webhooks/crm/health`

## 🔍 Troubleshooting

### Server won't start

1. Check Python version: `python --version` (need 3.11+)
2. Verify dependencies: `pip list`
3. Check logs: `cat logs/app.log`

### Function calls failing

1. Check webhook URL in Vapi dashboard
2. Verify server is publicly accessible
3. Check function logs in `logs/app.log`
4. Test endpoint manually with curl:
   ```bash
   curl -X POST http://localhost:8000/functions/check_property \
     -H "Content-Type: application/json" \
     -d '{"city":"Ocala","state":"FL"}'
   ```

### Integration errors

1. Run: `python scripts/test_integrations.py`
2. Verify API credentials in `.env`
3. Check service status pages
4. Review error messages in logs

### Vapi assistant not responding

1. Check assistant is active in Vapi dashboard
2. Verify phone number is assigned
3. Check webhook URL is correct and accessible
4. Test webhooks: `curl https://your-domain.com/health`

## 📞 Support

For issues or questions:

1. Check logs: `logs/app.log`
2. Review documentation in this guide
3. Check API documentation: http://localhost:8000/docs
4. Contact Sally Love Real Estate IT team

## 🔄 Updates and Maintenance

### Updating Dependencies

```bash
# Update all packages
uv sync --upgrade

# OR with pip
pip install --upgrade -e .
```

### Updating Vapi Assistant

```bash
# Re-run setup script
python scripts/setup_vapi.py
```

### Backing Up Data

Important files to backup:
- `.env` (API credentials)
- `logs/` (application logs)
- Any custom configurations

## 📈 Performance Tips

1. **Enable caching** for MLS queries (reduces API calls)
2. **Use connection pooling** for database connections
3. **Monitor response times** in logs
4. **Set up alerts** for failed function calls
5. **Regularly review** call transcripts for improvements

## 🎯 Next Steps

After setup:

1. ✅ Test all 7 functions with sample data
2. ✅ Make a test call to verify end-to-end flow
3. ✅ Review transcripts and adjust prompts if needed
4. ✅ Set up monitoring and alerts
5. ✅ Train team on system capabilities
6. ✅ Go live! 🚀

