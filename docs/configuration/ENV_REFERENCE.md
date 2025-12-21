# Environment Variables Reference

**All configuration values MUST be set in `.env` file or environment variables.**

`settings.py` has been updated to remove hardcoded defaults - it now requires all values to be explicitly set in environment variables. This ensures consistency between local development and production.

## 📋 Current Configuration

### ✅ Already Set in .env

```bash
# Environment
ENVIRONMENT=development

# Server Configuration
HOST=0.0.0.0
PORT=8000
WEBHOOK_BASE_URL=https://sally-love-voice-agent.fly.dev

# Vapi Configuration
VAPI_API_KEY=bf42985a-a53c-4b6f-b274-64db55cf57df
VAPI_PHONE_NUMBER_ID=

# BoldTrail CRM Configuration
BOLDTRAIL_API_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjIwMzM0MTQsImlhdCI6MTc2NTUwMDU2MCwiZXhwIjoxNzk3MDM2NTYwLCJuYmYiOjE3NjU1MDA1NjAsImF1ZCI6IioiLCJhY3QiOjE0Mjc1LCJqdGkiOiI5MWE2MjBjODc4YmFjOGQ0MjRhMTM2MWRmYTY3ZmVkZSJ9.g5mib7RvGkfjLikiY5uE1CxeqSmxHPJ-XgNkbIxQCgI
BOLDTRAIL_API_URL=https://api.kvcore.com/v2/public
BOLDTRAIL_ACCOUNT_ID=14275
BOLDTRAIL_ZAPIER_KEY=OTg3NjlhMWU0M2M0MDgzZTIzYmE5YzU0MDYxMjZlNzM6by0y

# Stellar MLS Configuration
STELLAR_MLS_USERNAME=
STELLAR_MLS_PASSWORD=
STELLAR_MLS_API_URL=https://api.stellarmls.com/v1

# Twilio Configuration
TWILIO_ACCOUNT_SID=AC303e887452079b47f0f8fcb156929c90
TWILIO_AUTH_TOKEN=12b059e917154b4c6e5d001363f3b633
TWILIO_PHONE_NUMBER=+18137336160

# Business Configuration
BUSINESS_NAME="Sally Love Real Estate"
BUSINESS_PHONE=+13523992010
OFFICE_HOURS_START=09:00
OFFICE_HOURS_END=17:00
OFFICE_TIMEZONE=America/New_York

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

TEST_MODE=true

# Lead Notification Configuration
OFFICE_NOTIFICATION_PHONE=+13523992010
JEFF_NOTIFICATION_PHONE=
LEAD_NOTIFICATION_ENABLED=true

# Testing Configuration (Full)
TEST_AGENT_NAME=Hammas Ali
TEST_AGENT_PHONE=+923035699010

```

## 🔑 Key Variables for New Features

### Lead Notifications (Option A Implementation)

| Variable | Current Value | Description |
|----------|---------------|-------------|
| `OFFICE_NOTIFICATION_PHONE` | `+13523992010` | Brenda's office line for notifications and fallback |
| `JEFF_NOTIFICATION_PHONE` | (empty) | Jeff's mobile for SMS alerts - **ADD BEFORE PRODUCTION** |
| `LEAD_NOTIFICATION_ENABLED` | `true` | Enable/disable office notifications |

### Test Mode Configuration

| Variable | Current Value | Description |
|----------|---------------|-------------|
| `TEST_MODE` | `true` | When true, all notifications/transfers go to TEST_AGENT_PHONE |
| `TEST_AGENT_NAME` | `Hammas Ali` | Name shown in test transfers |
| `TEST_AGENT_PHONE` | `+923035699010` | Your test number for all notifications |

## 🔄 How It Works

### Development (TEST_MODE=true)
```
Buyer Lead Created → Notification SMS → +923035699010 (your number)
Seller Lead Created → Notification SMS → +923035699010 (your number)
Transfer Request → Call goes to → +923035699010 (your number)
Transfer Fails → Alert SMS → +923035699010 (your number)
```

### Production (TEST_MODE=false)
```
Buyer Lead Created → Notification SMS → JEFF_NOTIFICATION_PHONE or OFFICE_NOTIFICATION_PHONE
Seller Lead Created → Notification SMS → JEFF_NOTIFICATION_PHONE or OFFICE_NOTIFICATION_PHONE
Transfer Request → Call goes to → Actual agent phone
Transfer Fails → Alert SMS → JEFF_NOTIFICATION_PHONE or OFFICE_NOTIFICATION_PHONE
                → Fallback transfer → OFFICE_NOTIFICATION_PHONE
```

## ✏️ To Update a Value

### Local Development (.env file)
Simply edit `/Users/mac/Developer/sally_love_voice_agent/.env`

### Production (Fly.io)
Use Fly.io secrets:

```bash
# Add Jeff's number
flyctl secrets set JEFF_NOTIFICATION_PHONE="+1XXXXXXXXXX" --app sally-love-voice-agent

# Switch to production mode
flyctl secrets set TEST_MODE=false --app sally-love-voice-agent

# Disable notifications temporarily
flyctl secrets set LEAD_NOTIFICATION_ENABLED=false --app sally-love-voice-agent
```

## 📝 Before Going Live Checklist

- [ ] Add Jeff's phone number to `.env` locally for testing
- [ ] Test with TEST_MODE=true (verify you receive all notifications)
- [ ] Set `JEFF_NOTIFICATION_PHONE` in Fly.io secrets
- [ ] Set `TEST_MODE=false` in Fly.io secrets
- [ ] Monitor first few real calls closely

## 🔒 Security Note

The `.env` file is in `.gitignore` and should **never be committed** to version control.  
Sensitive API keys and tokens are kept secure locally and in Fly.io secrets only.

## ⚙️ Settings.py Changes

**Updated:** `src/config/settings.py` now requires all configuration values to be set in environment variables. 

**What changed:**
- ❌ Removed hardcoded defaults for required values
- ✅ Only static values (like API URLs) have defaults
- ✅ All business logic values must come from .env
- ✅ Clear comments indicate which values are required vs optional

**Why this matters:**
- Prevents confusion about where values come from
- Forces explicit configuration in both dev and prod
- Makes it obvious if a required value is missing

## 🆘 Troubleshooting

### Not receiving notifications?
1. Check `TEST_MODE` value in `.env`
2. Check `LEAD_NOTIFICATION_ENABLED` is `true`
3. Verify phone numbers are in E.164 format (+country code)

### Wrong number receiving notifications?
1. If `TEST_MODE=true`: Check `TEST_AGENT_PHONE`
2. If `TEST_MODE=false`: Check `JEFF_NOTIFICATION_PHONE` and `OFFICE_NOTIFICATION_PHONE`

### Need to add more test numbers?
Just update `TEST_AGENT_PHONE` in `.env` to any number you want to use for testing.

