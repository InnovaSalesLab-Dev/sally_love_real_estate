# ✅ GHL Form Submission Webhook - Implementation Complete

**Date:** December 22, 2025  
**Pattern:** Based on HVAC and mid-florida-age-management repositories  
**Status:** ✅ Ready to Configure

---

## 🎯 What Was Implemented

A complete GoHighLevel (GHL) form submission webhook that triggers Vapi to make an **outbound call** to the user.

### User Flow:
1. User fills out form on your website
2. User clicks "Submit"
3. GHL receives form submission
4. GHL workflow sends webhook to your system
5. **Your system triggers Vapi to call the user back**
6. User's phone rings (within 10-15 seconds)
7. Vapi AI agent starts conversation with form context

---

## 📁 Files Created/Modified

### 1. **src/webhooks/ghl_webhooks.py** (Complete Rewrite)

**What it does:**
- Handles GHL form submission webhooks
- Validates webhook signatures (security)
- Extracts contact info from GHL payload
- Triggers Vapi outbound call with form context

**Key Functions:**
- `handle_ghl_form_submission()` - Main webhook handler
- `handle_ghl_call_status()` - Handles call status updates
- `handle_ghl_test_webhook()` - Test endpoint
- `verify_ghl_signature()` - Security verification

**Webhook Endpoint:**
```
POST /webhooks/ghl/form-submission
```

**Expected Payload from GHL:**
```json
{
  "type": "FormSubmit",
  "locationId": "abc123",
  "contactId": "contact_xyz",
  "submittedAt": "2025-12-22T10:30:00Z",
  "contact": {
    "id": "contact_xyz",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+13525551234"
  },
  "formData": {
    "name": "John Doe",
    "phone": "+13525551234",
    "email": "john@example.com",
    "property_interest": "1738 Augustine Drive",
    "budget": "$500k-$750k",
    "timeframe": "1-3 months"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Outbound call initiated via Vapi.",
  "vapi_call_id": "call_abc123",
  "ghl_contact_id": "contact_xyz"
}
```

---

### 2. **src/integrations/vapi_client.py** (Enhanced)

**Added Method:**
```python
async def create_outbound_call(
    phone_number: str,
    assistant_id: str,
    customer_name: Optional[str] = None,
    customer_email: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
```

**What it does:**
- Convenience wrapper for creating outbound calls
- Formats phone call configuration for Vapi API
- Attaches customer info and metadata to call
- Returns call data (including call ID)

**Usage Example:**
```python
from src.integrations.vapi_client import VapiClient

vapi_client = VapiClient()

call_data = await vapi_client.create_outbound_call(
    phone_number="+13525551234",
    assistant_id="asst_abc123",
    customer_name="John Doe",
    customer_email="john@example.com",
    metadata={
        "ghl_contact_id": "contact_xyz",
        "property_interest": "1738 Augustine Drive",
        "budget": "$500k-$750k",
        "timeframe": "1-3 months"
    }
)

print(f"Call initiated! Call ID: {call_data['id']}")
```

---

### 3. **main.py** (Updated)

**Change:**
```python
# Import GHL webhook router
from src.webhooks.ghl_webhooks import router as ghl_webhooks_router

# Include in FastAPI app
app.include_router(ghl_webhooks_router, prefix="/webhooks/ghl", tags=["Webhooks"])
```

**What it does:**
- Registers GHL webhook endpoints with FastAPI
- Makes endpoints available at `/webhooks/ghl/*`

---

### 4. **src/config/settings.py** (Already Had GHL Fields)

**Existing Configuration:**
```python
# GoHighLevel (GHL) Configuration
GHL_WEBHOOK_SECRET: str = ""  # Optional - for webhook signature verification
GHL_API_KEY: str = ""  # Optional - if you need to make API calls to GHL
GHL_LOCATION_ID: str = ""  # Optional - your GHL location ID
VAPI_ASSISTANT_ID: str = ""  # Required if using GHL webhooks
```

**No changes needed** - fields were already present!

---

## 📚 Documentation Created

### 1. **docs/webhooks/GHL_FORM_WEBHOOK_SETUP.md**
- Complete step-by-step setup guide
- Form creation instructions
- Workflow configuration
- Troubleshooting guide
- Testing procedures

### 2. **GHL_WEBHOOK_QUICKSTART.md** (Updated)
- Quick start guide
- 4-step setup process
- Configuration checklist

### 3. **docs/webhooks/GHL_FORM_WEBHOOK_IMPLEMENTATION.md** (This File)
- Implementation summary
- Technical details
- Code references

### 4. **docs/INDEX.md** (Updated)
- Added new documentation references
- Updated webhooks section
- Added quick lookup entries

---

## ⚙️ Configuration Required

### Step 1: Update .env File

Add these variables to your `.env` file:

```bash
# Vapi Configuration (if not already set)
VAPI_ASSISTANT_ID=asst_your_assistant_id_here

# GoHighLevel Configuration
GHL_WEBHOOK_SECRET=your_secret_here_for_signature_verification
GHL_API_KEY=your_ghl_api_key_here
GHL_LOCATION_ID=your_ghl_location_id_here
```

**How to get these:**
- `VAPI_ASSISTANT_ID`: Vapi Dashboard → Assistants → (select your assistant) → Copy ID
- `GHL_WEBHOOK_SECRET`: Create your own (e.g., `ghl_secret_abc123xyz`)
- `GHL_API_KEY`: GHL → Settings → Integrations → API Keys
- `GHL_LOCATION_ID`: GHL → Settings → Business Profile

---

### Step 2: Deploy to Production

```bash
cd /Users/mac/Developer/sally_love_voice_agent

# Deploy
flyctl deploy --app sally-love-voice-agent

# Set secrets in production
flyctl secrets set \
  VAPI_ASSISTANT_ID=asst_your_id_here \
  GHL_WEBHOOK_SECRET=your_secret_here \
  GHL_API_KEY=your_api_key_here \
  GHL_LOCATION_ID=your_location_id_here \
  --app sally-love-voice-agent
```

---

### Step 3: Create Form in GHL

1. **Go to:** Sites → Forms
2. **Create new form** with these fields:
   - **Name** (text, required)
   - **Phone** (tel, required) ⚠️ **CRITICAL**
   - **Email** (email, optional)
   - **Property Interest** (text, optional)
   - **Budget** (text, optional)
   - **Timeframe** (select, optional)

**Important:** Phone field is REQUIRED for the system to call the user!

---

### Step 4: Configure Workflow in GHL

1. **Go to:** Automations → Workflows
2. **Click:** Create Workflow
3. **Name:** "Trigger Vapi Call on Form Submit"
4. **Trigger:** Form Submission → (select your form)
5. **Add Action:** Send Outbound Webhook
   - **URL:** `https://sally-love-voice-agent.fly.dev/webhooks/ghl/form-submission`
   - **Method:** POST
   - **Content-Type:** application/json
   - **Body:** (Use the JSON template from `GHL_FORM_WEBHOOK_SETUP.md`)
6. **Activate Workflow**

---

## 🧪 Testing

### Quick Test (After Setup):

1. **Submit your GHL form** with your own phone number
2. **Check logs:**
   ```bash
   flyctl logs --app sally-love-voice-agent -f
   ```
3. **Expected output:**
   ```
   Received GHL form submission webhook.
   Form data: {...}
   Initiating outbound call to +1234567890...
   Vapi outbound call initiated successfully. Call ID: call_abc123
   ```
4. **Your phone should ring within 10-15 seconds**
5. **Answer → Vapi AI agent speaks with form context**

---

### Test Webhook Directly:

```bash
curl -X POST https://sally-love-voice-agent.fly.dev/webhooks/ghl/test \
  -H "Content-Type: application/json" \
  -d '{"test": "hello"}'
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "GHL test webhook received."
}
```

---

## 🔒 Security

### Webhook Signature Verification

**How it works:**
1. GHL sends `X-GHL-Signature` header with each webhook
2. Your system calculates expected signature using `GHL_WEBHOOK_SECRET`
3. If signatures match → webhook is valid
4. If signatures don't match → webhook is rejected (403 Forbidden)

**Code:**
```python
def verify_ghl_signature(request_body: bytes, x_ghl_signature: str) -> bool:
    if not settings.GHL_WEBHOOK_SECRET:
        return True  # Allow if secret not set (dev/testing)
    
    expected_signature = hmac.new(
        settings.GHL_WEBHOOK_SECRET.encode('utf-8'),
        request_body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, x_ghl_signature)
```

**In Production:**
- Always set `GHL_WEBHOOK_SECRET`
- GHL will send signature in header
- Invalid signatures are rejected

---

## 📊 What Gets Passed to Vapi

When Vapi calls the user, the following information is available:

**Call Metadata:**
```json
{
  "ghl_contact_id": "contact_xyz",
  "form_submission_payload": {
    "name": "John Doe",
    "phone": "+13525551234",
    "email": "john@example.com",
    "property_interest": "1738 Augustine Drive",
    "budget": "$500k-$750k",
    "timeframe": "1-3 months"
  }
}
```

**Customer Info:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "number": "+13525551234"
}
```

**Configure Vapi System Prompt to Use This:**

Update your Vapi assistant system prompt to reference the metadata:

```
When you start the call, you have access to form submission data:
- Contact Name: {metadata.form_submission_payload.name}
- Property Interest: {metadata.form_submission_payload.property_interest}
- Budget: {metadata.form_submission_payload.budget}
- Timeframe: {metadata.form_submission_payload.timeframe}

Start with:
"Hi [Name], this is [AI Name] from Sally Love Real Estate. 
I'm calling about your inquiry regarding [Property Interest]..."
```

---

## 🐛 Troubleshooting

### Issue: User Not Receiving Call

**Common Causes:**

1. **Missing Phone Number**
   - ✅ Check form has phone field
   - ✅ Check field name is `phone`
   - ✅ Check phone format (+1234567890)

2. **Invalid Vapi Assistant ID**
   - ✅ Verify `VAPI_ASSISTANT_ID` in .env
   - ✅ Check assistant exists in Vapi dashboard
   - ✅ Check assistant is active

3. **Vapi API Error**
   - ✅ Check logs: `flyctl logs -f`
   - ✅ Look for error messages
   - ✅ Verify `VAPI_API_KEY` is valid

**Test Vapi Directly:**
```bash
curl https://api.vapi.ai/call/phone \
  -H "Authorization: Bearer YOUR_VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "assistantId": "YOUR_ASSISTANT_ID",
    "customer": {
      "number": "+1234567890"
    }
  }'
```

---

### Issue: Webhook Not Triggering

**Check:**
1. ✅ Form submitted successfully?
2. ✅ Workflow status = Active?
3. ✅ Webhook URL correct?
4. ✅ App deployed and running?

**Test:**
```bash
curl https://sally-love-voice-agent.fly.dev/health
```

Should return: `{"status": "healthy"}`

---

### Issue: Signature Verification Failing

**Check:**
1. ✅ `GHL_WEBHOOK_SECRET` set correctly?
2. ✅ GHL workflow configured with same secret?
3. ✅ Header name is `X-GHL-Signature`?

**Temporarily Disable (for testing):**
```bash
# In .env
GHL_WEBHOOK_SECRET=
```

(Empty = verification disabled)

---

## 📈 Monitoring

### View Real-Time Logs:

```bash
# All logs
flyctl logs --app sally-love-voice-agent -f

# GHL webhooks only
flyctl logs --app sally-love-voice-agent -f | grep "GHL"

# Form submissions only
flyctl logs --app sally-love-voice-agent -f | grep "Form submitted"

# Vapi calls only
flyctl logs --app sally-love-voice-agent -f | grep "Vapi outbound call"
```

### Metrics to Track:

- Total form submissions received
- Successful Vapi calls initiated
- Failed calls (with reasons)
- Average time from submit to call
- Call completion rate

---

## 🔄 Flow Diagram

```
┌─────────────────┐
│   User Fills    │
│      Form       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  User Clicks    │
│    "Submit"     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   GHL Receives  │
│   Form Data     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GHL Workflow   │
│    Triggers     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GHL Sends      │
│   Webhook       │───────┐
└─────────────────┘       │
                          │
                          ▼
                 ┌─────────────────┐
                 │  Your System    │
                 │  Receives       │
                 │  Webhook        │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Verify         │
                 │  Signature      │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Extract        │
                 │  Contact Info   │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Call Vapi API  │
                 │  create_phone   │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Vapi Initiates │
                 │  Outbound Call  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  User's Phone   │
                 │     Rings       │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  User Answers   │
                 │                 │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  AI Agent       │
                 │  Speaks with    │
                 │  Form Context   │
                 └─────────────────┘

Timeline: ~10-15 seconds from submit to ring
```

---

## ✅ Implementation Checklist

- [x] Created `src/webhooks/ghl_webhooks.py` with form submission handler
- [x] Added `create_outbound_call()` method to `VapiClient`
- [x] Integrated webhook router in `main.py`
- [x] Verified `settings.py` has GHL configuration fields
- [x] Created comprehensive documentation
- [x] Updated `docs/INDEX.md` with new documentation
- [x] Updated `GHL_WEBHOOK_QUICKSTART.md`
- [x] Passed linting checks (no errors)
- [ ] **User needs to:** Add configuration to `.env`
- [ ] **User needs to:** Deploy to production
- [ ] **User needs to:** Create form in GHL
- [ ] **User needs to:** Configure workflow in GHL
- [ ] **User needs to:** Test end-to-end

---

## 📝 Next Steps

1. **Add configuration to `.env`** (see Step 1 above)
2. **Deploy to production** (see Step 2 above)
3. **Create form in GHL** (see Step 3 above)
4. **Configure workflow** (see Step 4 above)
5. **Test with your phone number**
6. **Go live!**

---

## 📖 Related Documentation

- **Setup Guide:** `docs/webhooks/GHL_FORM_WEBHOOK_SETUP.md`
- **Quick Start:** `GHL_WEBHOOK_QUICKSTART.md`
- **Vapi System Prompt:** `docs/vapi/VAPI_SYSTEM_PROMPT_2.md`
- **General Webhooks:** `docs/webhooks/GHL_WEBHOOK_SETUP.md`

---

**Status:** ✅ Complete - Ready for Configuration  
**Last Updated:** December 22, 2025  
**Pattern Source:** HVAC & mid-florida-age-management repositories

