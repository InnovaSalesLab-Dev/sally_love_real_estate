# GoHighLevel (GHL) Webhook Setup Guide

**Purpose:** Configure GHL to trigger your Vapi AI agent for inbound calls

**Date:** December 22, 2025  
**Status:** ✅ Ready to configure

---

## 🎯 What This Does

When someone calls your GHL phone number:
1. GHL receives the inbound call
2. GHL sends a webhook to your system
3. Your system triggers the Vapi AI agent
4. Vapi answers the call with AI
5. Call is handled automatically!

---

## 📋 Prerequisites

### 1. **Vapi Assistant ID**

You need your Vapi assistant ID:

**How to get it:**
1. Log into [Vapi Dashboard](https://dashboard.vapi.ai)
2. Go to "Assistants"
3. Select your assistant (Sally Love Voice Agent)
4. Copy the Assistant ID (looks like: `asst_xxx...`)

### 2. **Your Webhook URL**

**Production URL:**
```
https://sally-love-voice-agent.fly.dev/webhooks/ghl/inbound-call
```

**Local Testing:**
```
http://localhost:8000/webhooks/ghl/inbound-call
```

**For local testing, use ngrok:**
```bash
ngrok http 8000
# Use the ngrok URL: https://xxx.ngrok.io/webhooks/ghl/inbound-call
```

---

## ⚙️ Step 1: Update .env File

Add these variables to your `.env` file:

```bash
# GoHighLevel (GHL) Configuration
GHL_WEBHOOK_SECRET=your_webhook_secret_here
GHL_API_KEY=your_ghl_api_key_here
GHL_LOCATION_ID=your_ghl_location_id_here
VAPI_ASSISTANT_ID=asst_your_assistant_id_here
```

### How to get these values:

**GHL_WEBHOOK_SECRET:**
- You create this yourself (e.g., `ghl_webhook_secret_12345`)
- Use it to verify webhooks are from GHL
- Share it with GHL when configuring the webhook

**GHL_API_KEY:**
- Log into GoHighLevel
- Settings → Integrations → API Keys
- Create new API key or copy existing

**GHL_LOCATION_ID:**
- In GHL dashboard
- Settings → Business Profile
- Copy the Location ID

**VAPI_ASSISTANT_ID:**
- From Vapi Dashboard (see Prerequisites above)

---

## 🔧 Step 2: Configure Webhook in GHL

### 2.1 Access GHL Webhook Settings

1. Log into **GoHighLevel**
2. Go to **Settings** → **Integrations** → **Webhooks**
3. Click **"+ Add Webhook"** or **"Create Webhook"**

### 2.2 Configure Webhook

**Fill in these details:**

| Field | Value |
|-------|-------|
| **Webhook Name** | Sally Love Vapi Inbound Calls |
| **Webhook URL** | `https://sally-love-voice-agent.fly.dev/webhooks/ghl/inbound-call` |
| **Method** | POST |
| **Event Type** | Inbound Call |
| **Secret** | (Use your `GHL_WEBHOOK_SECRET` value) |
| **Status** | Active |

**Events to Subscribe:**
- ☑️ Inbound Call Started
- ☑️ Call Ringing

**Optional events** (for tracking):
- ☑️ Call Answered
- ☑️ Call Completed
- ☑️ Call Failed

### 2.3 Test the Webhook

GHL usually has a "Test Webhook" button:

1. Click **"Test Webhook"**
2. Check the response (should see success message)
3. Check your logs:

```bash
flyctl logs --app sally-love-voice-agent -f
```

---

## 🧪 Step 3: Test End-to-End

### Test Sequence:

1. **Call your GHL phone number**
2. **GHL receives the call**
3. **GHL sends webhook to your system**
4. **Your system triggers Vapi**
5. **Vapi AI answers the call**

### Expected Flow:

```
Caller dials GHL number
    ↓
GHL receives call
    ↓
GHL POST /webhooks/ghl/inbound-call
    ↓
Your system receives webhook
    ↓
System calls Vapi API to create call
    ↓
Vapi calls back the incoming caller
    ↓
AI agent handles the call
```

### Check Logs:

**Your system logs:**
```bash
flyctl logs --app sally-love-voice-agent -f

# Should see:
# "Received GHL inbound call webhook"
# "Inbound call from +1xxxyyy"
# "Successfully triggered Vapi call: xxx"
```

**Vapi Dashboard:**
- Go to Vapi Dashboard → Calls
- You should see the new call appear

---

## 📊 Webhook Endpoints

Your system now has these GHL webhook endpoints:

### 1. **Inbound Call Handler** (Main)

```
POST /webhooks/ghl/inbound-call
```

**Purpose:** Triggers Vapi AI for inbound calls

**Payload Example:**
```json
{
  "type": "InboundCall",
  "locationId": "xxx",
  "contactId": "xxx",
  "phone": "+13525551234",
  "callId": "xxx",
  "direction": "inbound",
  "callStatus": "ringing",
  "contact": {
    "id": "xxx",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+13525551234"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Vapi agent triggered successfully",
  "ghl_call_id": "xxx",
  "vapi_call_id": "xxx",
  "caller": {
    "phone": "+13525551234",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

---

### 2. **Call Status Updates** (Optional)

```
POST /webhooks/ghl/call-status
```

**Purpose:** Track call status updates

**Payload Example:**
```json
{
  "type": "CallStatus",
  "callId": "xxx",
  "status": "completed",
  "duration": 120,
  "recordingUrl": "https://..."
}
```

---

### 3. **Test Webhook** (Development)

```
POST /webhooks/ghl/test
```

**Purpose:** Test webhook connectivity

**Usage:**
```bash
curl -X POST https://sally-love-voice-agent.fly.dev/webhooks/ghl/test \
  -H "Content-Type: application/json" \
  -d '{"test": "hello"}'
```

---

## 🔒 Security

### Webhook Signature Verification

The webhook automatically verifies GHL signatures if `GHL_WEBHOOK_SECRET` is set.

**How it works:**
1. GHL sends webhook with `X-GHL-Signature` header
2. Your system calculates expected signature
3. If signatures match → Process webhook
4. If signatures don't match → Reject (401)

**To enable:**
```bash
# In .env
GHL_WEBHOOK_SECRET=your_secret_here
```

**To disable** (not recommended for production):
```bash
# Leave empty or don't set
GHL_WEBHOOK_SECRET=
```

---

## 📝 Webhook Headers

GHL sends these headers:

```
Content-Type: application/json
X-GHL-Signature: sha256=xxx...
X-GHL-Location-ID: xxx
X-GHL-Timestamp: 1234567890
```

---

## 🐛 Troubleshooting

### Issue: Webhook Not Triggering

**Check:**
1. ✅ Webhook URL correct in GHL?
2. ✅ Webhook status = Active in GHL?
3. ✅ Events subscribed (Inbound Call)?
4. ✅ App deployed and running?

**Test:**
```bash
# Check app is running
curl https://sally-love-voice-agent.fly.dev/health

# Check webhook endpoint
curl -X POST https://sally-love-voice-agent.fly.dev/webhooks/ghl/test
```

---

### Issue: Signature Verification Failing

**Symptoms:** Webhook returns 401 error

**Solutions:**
1. Check `GHL_WEBHOOK_SECRET` matches what's in GHL
2. Temporarily disable signature check:
   ```bash
   GHL_WEBHOOK_SECRET=
   ```
3. Check GHL is sending `X-GHL-Signature` header

---

### Issue: Vapi Not Answering Call

**Check:**
1. ✅ `VAPI_ASSISTANT_ID` correct in .env?
2. ✅ `VAPI_API_KEY` valid?
3. ✅ Vapi assistant configured correctly?

**Test Vapi directly:**
```bash
curl https://api.vapi.ai/call \
  -H "Authorization: Bearer YOUR_VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "assistant_id": "YOUR_ASSISTANT_ID"
  }'
```

---

### Issue: Call Coming From Wrong Number

**Check webhook payload:**
```bash
flyctl logs --app sally-love-voice-agent -f | grep "Payload"
```

Ensure `phone` field in payload is correct.

---

## 📈 Monitoring

### View Webhook Logs:

```bash
# Real-time logs
flyctl logs --app sally-love-voice-agent -f

# Filter for GHL webhooks
flyctl logs --app sally-love-voice-agent -f | grep "GHL"

# Filter for specific call
flyctl logs --app sally-love-voice-agent | grep "call_id_here"
```

### Metrics to Track:

- Total webhooks received
- Successful Vapi triggers
- Failed triggers
- Average response time
- Call durations

---

## 🚀 Deployment

After making changes, deploy:

```bash
cd /Users/mac/Developer/sally_love_voice_agent
flyctl deploy --app sally-love-voice-agent
```

---

## 📚 Related Documentation

- `docs/vapi/VAPI_SYSTEM_PROMPT_2.md` - Vapi assistant configuration
- `docs/technical/ROUTE_TO_AGENT_GUIDE.md` - Call transfer guide
- `src/webhooks/ghl_webhooks.py` - Webhook implementation code

---

## ✅ Quick Setup Checklist

- [ ] Get Vapi Assistant ID
- [ ] Add configuration to `.env`:
  - [ ] `VAPI_ASSISTANT_ID`
  - [ ] `GHL_WEBHOOK_SECRET`
  - [ ] `GHL_API_KEY`
  - [ ] `GHL_LOCATION_ID`
- [ ] Deploy updated app
- [ ] Configure webhook in GHL dashboard
- [ ] Test webhook with GHL test button
- [ ] Make test call to GHL number
- [ ] Verify Vapi answers the call
- [ ] Check logs for any errors

---

**Status:** ✅ Ready to configure  
**Last Updated:** December 22, 2025  
**Deployment:** Production ready

