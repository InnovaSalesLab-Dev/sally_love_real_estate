# Environment Configuration Guide

## 📋 Complete .env File Configuration

Copy this to your `.env` file and fill in your actual values:

```bash
# =============================================================================
# ENVIRONMENT
# =============================================================================
ENVIRONMENT=development

# =============================================================================
# SERVER CONFIGURATION
# =============================================================================
HOST=0.0.0.0
PORT=8000
WEBHOOK_BASE_URL=https://sally-love-voice-agent.fly.dev

# =============================================================================
# VAPI CONFIGURATION
# =============================================================================
VAPI_API_KEY=your_vapi_api_key_here
VAPI_PHONE_NUMBER_ID=your_vapi_phone_number_id_here
VAPI_API_URL=https://api.vapi.ai

# =============================================================================
# BOLDTRAIL CRM CONFIGURATION
# =============================================================================
BOLDTRAIL_API_KEY=your_boldtrail_api_key_here
BOLDTRAIL_API_URL=https://api.kvcore.com/v2/public
BOLDTRAIL_ACCOUNT_ID=your_account_id_here
BOLDTRAIL_ZAPIER_KEY=your_zapier_key_here

# =============================================================================
# STELLAR MLS CONFIGURATION
# =============================================================================
STELLAR_MLS_USERNAME=your_stellar_username
STELLAR_MLS_PASSWORD=your_stellar_password
STELLAR_MLS_API_URL=https://api.stellarmls.com/v1

# =============================================================================
# TWILIO CONFIGURATION (SMS & Phone)
# =============================================================================
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+13523992010

# =============================================================================
# BUSINESS CONFIGURATION
# =============================================================================
BUSINESS_NAME=Sally Love Real Estate
BUSINESS_PHONE=+13523992010
OFFICE_HOURS_START=09:00
OFFICE_HOURS_END=17:00
OFFICE_TIMEZONE=America/New_York

# =============================================================================
# LEAD NOTIFICATION CONFIGURATION
# Who gets notified when buyer/seller leads are created
# =============================================================================
OFFICE_NOTIFICATION_PHONE=+13523992010
JEFF_NOTIFICATION_PHONE=+1XXXXXXXXXX
LEAD_NOTIFICATION_ENABLED=true

# =============================================================================
# TESTING CONFIGURATION
# IMPORTANT: Set TEST_MODE=true during development
# When true, all notifications and transfers go to TEST_AGENT_PHONE
# =============================================================================
TEST_MODE=true
TEST_AGENT_NAME=Hammas Ali
TEST_AGENT_PHONE=+923035699010

# =============================================================================
# LOGGING
# =============================================================================
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

---

## 🔑 Fly.io Secrets (Production)

For production deployment on Fly.io, set these secrets:

```bash
# Core Services
flyctl secrets set VAPI_API_KEY="your_key" --app sally-love-voice-agent
flyctl secrets set BOLDTRAIL_API_KEY="your_key" --app sally-love-voice-agent
flyctl secrets set TWILIO_ACCOUNT_SID="your_sid" --app sally-love-voice-agent
flyctl secrets set TWILIO_AUTH_TOKEN="your_token" --app sally-love-voice-agent

# Twilio Phone
flyctl secrets set TWILIO_PHONE_NUMBER="+13523992010" --app sally-love-voice-agent

# Business Configuration
flyctl secrets set BUSINESS_PHONE="+13523992010" --app sally-love-voice-agent

# Lead Notifications (NEW)
flyctl secrets set OFFICE_NOTIFICATION_PHONE="+13523992010" --app sally-love-voice-agent
flyctl secrets set JEFF_NOTIFICATION_PHONE="+1XXXXXXXXXX" --app sally-love-voice-agent
flyctl secrets set LEAD_NOTIFICATION_ENABLED="true" --app sally-love-voice-agent

# Testing Configuration
flyctl secrets set TEST_MODE="true" --app sally-love-voice-agent
flyctl secrets set TEST_AGENT_NAME="Hammas Ali" --app sally-love-voice-agent
flyctl secrets set TEST_AGENT_PHONE="+923035699010" --app sally-love-voice-agent
```

---

## 📝 Variable Descriptions

### Core Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `development` or `production` |
| `WEBHOOK_BASE_URL` | Base URL for webhooks | `https://sally-love-voice-agent.fly.dev` |

### Vapi Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `VAPI_API_KEY` | Vapi API key for authentication | ✅ Yes |
| `VAPI_PHONE_NUMBER_ID` | Vapi phone number ID | ✅ Yes |

### BoldTrail CRM

| Variable | Description | Required |
|----------|-------------|----------|
| `BOLDTRAIL_API_KEY` | BoldTrail API key | ✅ Yes |
| `BOLDTRAIL_ACCOUNT_ID` | BoldTrail account ID | ✅ Yes |

### Twilio (SMS)

| Variable | Description | Required |
|----------|-------------|----------|
| `TWILIO_ACCOUNT_SID` | Twilio account SID | ✅ Yes |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | ✅ Yes |
| `TWILIO_PHONE_NUMBER` | Twilio phone number (E.164 format) | ✅ Yes |

### Business Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `BUSINESS_NAME` | Business name | Sally Love Real Estate |
| `BUSINESS_PHONE` | Main business phone | +13523992010 |
| `OFFICE_HOURS_START` | Office opening time | 09:00 |
| `OFFICE_HOURS_END` | Office closing time | 17:00 |

### Lead Notifications (NEW)

| Variable | Description | When Used |
|----------|-------------|-----------|
| `OFFICE_NOTIFICATION_PHONE` | Brenda's office line for notifications | Fallback, failed transfers |
| `JEFF_NOTIFICATION_PHONE` | Jeff's mobile for lead notifications | New buyer/seller leads |
| `LEAD_NOTIFICATION_ENABLED` | Enable/disable office notifications | true = send, false = don't send |

### Testing Configuration (NEW)

| Variable | Description | When Used |
|----------|-------------|-----------|
| `TEST_MODE` | Enable test mode | Development/testing |
| `TEST_AGENT_NAME` | Test agent name | When `TEST_MODE=true` |
| `TEST_AGENT_PHONE` | Test phone number | When `TEST_MODE=true` |

---

## 🔄 TEST_MODE Behavior

### When `TEST_MODE=true` (Development)

All notifications and transfers are redirected to `TEST_AGENT_PHONE`:

- ✅ Buyer lead notifications → `TEST_AGENT_PHONE`
- ✅ Seller lead notifications → `TEST_AGENT_PHONE`
- ✅ Failed transfer alerts → `TEST_AGENT_PHONE`
- ✅ Call transfers → `TEST_AGENT_PHONE`
- ✅ Office and Jeff will **NOT** receive any messages
- ✅ Safe for testing

### When `TEST_MODE=false` (Production)

Notifications and transfers go to real numbers:

- Buyer lead notifications → `JEFF_NOTIFICATION_PHONE` or `OFFICE_NOTIFICATION_PHONE`
- Seller lead notifications → `JEFF_NOTIFICATION_PHONE` or `OFFICE_NOTIFICATION_PHONE`
- Failed transfer alerts → `JEFF_NOTIFICATION_PHONE` or `OFFICE_NOTIFICATION_PHONE`
- Call transfers → Actual agent phone numbers
- Real office/Jeff will receive messages

---

## ⚙️ Priority Order for Notifications

When sending notifications, the system uses this priority:

1. **If `TEST_MODE=true`** → Always use `TEST_AGENT_PHONE`
2. **If `TEST_MODE=false` and `JEFF_NOTIFICATION_PHONE` is set** → Use Jeff's number
3. **If Jeff's number not set** → Use `OFFICE_NOTIFICATION_PHONE`

---

## 🚀 Quick Setup for Development

1. **Copy template to .env:**
   ```bash
   cp ENV_CONFIGURATION.md .env
   # Edit .env and fill in your values
   ```

2. **Set required values in .env:**
   ```bash
   TEST_MODE=true
   TEST_AGENT_PHONE=+923035699010
   TEST_AGENT_NAME=Hammas Ali
   TWILIO_ACCOUNT_SID=your_sid
   TWILIO_AUTH_TOKEN=your_token
   TWILIO_PHONE_NUMBER=+13523992010
   # ... other required values
   ```

3. **Deploy to Fly.io:**
   ```bash
   flyctl deploy --app sally-love-voice-agent
   ```

---

## ✅ Verify Configuration

### Check Local .env
```bash
cat .env | grep -E "(TEST_MODE|TEST_AGENT_PHONE|OFFICE_NOTIFICATION_PHONE|JEFF_NOTIFICATION_PHONE)"
```

### Check Fly.io Secrets
```bash
flyctl secrets list --app sally-love-voice-agent
```

---

## 🔧 Update Configuration

### Update Local .env
Edit `.env` file directly and restart the application.

### Update Fly.io Secrets
```bash
# Update a single secret
flyctl secrets set KEY=value --app sally-love-voice-agent

# Update multiple secrets
flyctl secrets set KEY1=value1 KEY2=value2 --app sally-love-voice-agent
```

---

## ⚠️ Important Notes

1. **Never commit `.env` to git** - It contains sensitive credentials
2. **Always set `TEST_MODE=true` during development** - Prevents bothering real people
3. **Verify secrets after deployment** - Use `flyctl secrets list` to confirm
4. **Use E.164 format for phone numbers** - Always include country code with `+`

---

## 📞 Example Phone Number Formats

✅ **Correct:**
- `+13523992010` (US)
- `+923035699010` (Pakistan)

❌ **Incorrect:**
- `352-399-2010` (missing country code)
- `3523992010` (missing + and country code)
- `1-352-399-2010` (has dashes, missing +)

---

## 🐛 Troubleshooting

### Configuration Not Loading?

1. **Check .env file exists:**
   ```bash
   ls -la .env
   ```

2. **Check file format** (no spaces around `=`):
   ```bash
   # ✅ Correct
   TEST_MODE=true
   
   # ❌ Incorrect
   TEST_MODE = true
   ```

3. **Restart application** after changing .env

### Fly.io Secrets Not Working?

1. **List current secrets:**
   ```bash
   flyctl secrets list --app sally-love-voice-agent
   ```

2. **Redeploy after setting secrets:**
   ```bash
   flyctl deploy --app sally-love-voice-agent
   ```

3. **Check logs for errors:**
   ```bash
   flyctl logs --app sally-love-voice-agent | grep -i "error\|warning"
   ```

