# GoHighLevel Form Submission Webhook - Trigger Vapi Outbound Call

**Purpose:** When a user submits a form in GHL, automatically trigger Vapi to call them back

**Date:** December 22, 2025  
**Status:** ✅ Ready to configure

---

## 🎯 How This Works

**User Journey:**
1. User fills out form on your website (property inquiry, contact form, etc.)
2. User clicks "Submit" button
3. GHL receives the form submission
4. GHL sends webhook to your system
5. Your system triggers Vapi to make an **OUTBOUND CALL**
6. Vapi AI calls the user back within seconds
7. AI agent handles the conversation automatically

---

## 📋 Prerequisites

### 1. **Vapi Assistant ID**

**How to get it:**
1. Log into [Vapi Dashboard](https://dashboard.vapi.ai)
2. Go to "Assistants"
3. Select your Sally Love Real Estate assistant
4. Copy the Assistant ID (looks like: `asst_xxx...`)

### 2. **Your Webhook URL**

**Production URL:**
```
https://sally-love-voice-agent.fly.dev/webhooks/ghl/form-submission
```

**Local Testing (with ngrok):**
```bash
ngrok http 8000
# Use: https://xxx.ngrok.io/webhooks/ghl/form-submission
```

---

## ⚙️ Step 1: Update .env File

Add these variables to your `.env` file:

```bash
# GoHighLevel Configuration
GHL_WEBHOOK_SECRET=your_webhook_secret_here
GHL_API_KEY=your_ghl_api_key_here
GHL_LOCATION_ID=your_ghl_location_id_here

# Vapi Assistant Configuration
VAPI_ASSISTANT_ID=asst_your_assistant_id_here
VAPI_API_KEY=your_existing_vapi_key
```

---

## 🔧 Step 2: Create Form in GHL

### 2.1 Create Your Form

1. **Log into GoHighLevel**
2. **Go to:** Sites → Forms (or Funnels → Forms)
3. **Click:** "Create Form"
4. **Add Form Fields:**
   - Name (required)
   - Phone Number (required) ⚠️ **CRITICAL**
   - Email (optional)
   - Property Interest (optional)
   - Budget Range (optional)
   - Timeline (optional)

**Important:** The phone number field is REQUIRED for Vapi to call back!

### 2.2 Form Field Names

Use these exact field names for best results:

| Field Name | GHL Field ID | Required |
|------------|--------------|----------|
| Name | `name` | ✅ Yes |
| Phone | `phone` | ✅ Yes |
| Email | `email` | ❌ No |
| Property Interest | `property_interest` | ❌ No |
| Budget | `budget` | ❌ No |
| Timeframe | `timeframe` | ❌ No |

---

## 📡 Step 3: Configure Webhook in GHL

### 3.1 Access Workflow Automation

1. **Go to:** Automations → Workflows
2. **Click:** "+ Create Workflow"
3. **Name:** "Trigger Vapi Call on Form Submit"

### 3.2 Configure Workflow Trigger

**Trigger:**
- **Type:** Form Submission
- **Form:** Select your form (created in Step 2)

### 3.3 Add Webhook Action

1. **Click:** "+" to add action
2. **Select:** "Webhooks" → "Send Outbound Webhook"
3. **Configure:**

| Setting | Value |
|---------|-------|
| **Webhook URL** | `https://sally-love-voice-agent.fly.dev/webhooks/ghl/form-submission` |
| **Method** | POST |
| **Content Type** | application/json |

**Request Body (JSON):**
```json
{
  "type": "FormSubmit",
  "locationId": "{{location.id}}",
  "contactId": "{{contact.id}}",
  "submittedAt": "{{timestamp}}",
  "contact": {
    "id": "{{contact.id}}",
    "name": "{{contact.name}}",
    "email": "{{contact.email}}",
    "phone": "{{contact.phone}}"
  },
  "formData": {
    "name": "{{contact.name}}",
    "phone": "{{contact.phone}}",
    "email": "{{contact.email}}",
    "property_interest": "{{custom_values.property_interest}}",
    "budget": "{{custom_values.budget}}",
    "timeframe": "{{custom_values.timeframe}}"
  }
}
```

**Headers:**
```
Content-Type: application/json
X-GHL-Signature: {{signature}}
```

### 3.4 Test the Workflow

1. **Click:** "Test Workflow"
2. **Fill out test form data**
3. **Check response:** Should see success message
4. **Check logs:**
   ```bash
   flyctl logs --app sally-love-voice-agent -f
   ```

---

## 🧪 Step 4: Test End-to-End

### Test Sequence:

1. **Fill out your GHL form**
2. **Click "Submit"**
3. **GHL workflow triggers**
4. **Webhook sent to your system**
5. **Your system triggers Vapi**
6. **Vapi calls the phone number from the form**
7. **AI agent speaks with the user**

### Expected Timeline:

```
Form Submit → 1-2 seconds → Webhook received
             ↓
Webhook received → 2-3 seconds → Vapi call initiated
             ↓
Vapi call initiated → 5-10 seconds → User's phone rings
             ↓
User answers → AI agent starts conversation
```

**Total time:** ~10-15 seconds from form submit to phone ringing

---

## 📊 Webhook Payload Example

**What GHL sends:**

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
    "property_interest": "1738 Augustine Drive, The Villages",
    "budget": "$500k-$750k",
    "timeframe": "1-3 months"
  }
}
```

**What your system returns:**

```json
{
  "status": "success",
  "message": "Outbound call initiated - user will receive a call shortly",
  "ghl_contact_id": "contact_xyz",
  "vapi_call_id": "call_abc123",
  "user": {
    "phone": "+13525551234",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "form_data": {
    "property_interest": "1738 Augustine Drive, The Villages",
    "budget": "$500k-$750k",
    "timeframe": "1-3 months"
  }
}
```

---

## 🎙️ Step 5: Configure Vapi Assistant Context

Your Vapi assistant will receive the form data in the call metadata. Update your system prompt to use this context:

**Example Vapi System Prompt Addition:**

```
When you start the call, you have access to the following information from the form:

- Contact Name: {metadata.contact_name}
- Email: {metadata.contact_email}
- Property Interest: {metadata.form_data.property_interest}
- Budget: {metadata.form_data.budget}
- Timeframe: {metadata.form_data.timeframe}

Start the conversation by acknowledging their form submission:
"Hi [Name], this is [AI Agent Name] from Sally Love Real Estate. 
I'm calling about your inquiry regarding [Property Interest]. 
I see you're looking in the [Budget] range and hoping to move within [Timeframe]. 
Let me help you with that..."
```

---

## 🔒 Security

### Webhook Signature Verification

The webhook automatically verifies GHL signatures if `GHL_WEBHOOK_SECRET` is set.

**To enable:**
```bash
# In .env
GHL_WEBHOOK_SECRET=your_secret_here
```

**In GHL workflow:**
- Add secret to webhook configuration
- GHL will send `X-GHL-Signature` header
- Your system verifies it matches

---

## 🐛 Troubleshooting

### Issue: Webhook Not Triggering

**Check:**
1. ✅ Form submitted successfully in GHL?
2. ✅ Workflow status = Active?
3. ✅ Webhook URL correct (include `/form-submission` path)?
4. ✅ App deployed and running?

**Test webhook directly:**
```bash
curl -X POST https://sally-love-voice-agent.fly.dev/webhooks/ghl/test \
  -H "Content-Type: application/json" \
  -d '{"test": "hello"}'
```

---

### Issue: User Not Receiving Call

**Common causes:**

1. **Missing Phone Number**
   - Check form includes phone field
   - Check phone field name is `phone`
   - Check phone number format (+1xxxxxxxxxx)

2. **Invalid Vapi Assistant ID**
   - Verify `VAPI_ASSISTANT_ID` in .env
   - Check assistant exists in Vapi dashboard
   - Check assistant is active

3. **Vapi API Error**
   - Check logs: `flyctl logs --app sally-love-voice-agent -f`
   - Look for error messages
   - Verify `VAPI_API_KEY` is valid

**Test Vapi directly:**
```bash
curl https://api.vapi.ai/call \
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

### Issue: Call Made But Context Missing

**Check:**
- Form field names match expected names
- GHL workflow passes all fields in request body
- Vapi assistant prompt configured to use metadata

**View what was sent:**
```bash
flyctl logs --app sally-love-voice-agent -f | grep "Form data"
```

---

## 📈 Monitoring

### View Webhook Activity:

```bash
# Real-time logs
flyctl logs --app sally-love-voice-agent -f

# Filter for form submissions
flyctl logs --app sally-love-voice-agent -f | grep "Form submitted"

# Check Vapi calls
flyctl logs --app sally-love-voice-agent -f | grep "Vapi outbound call"
```

### Metrics to Track:

- Total form submissions
- Successful Vapi calls triggered
- Failed calls (with reasons)
- Average time from submit to call
- Call completion rate

---

## 🚀 Deployment

1. **Add configuration to `.env`**
2. **Deploy:**
   ```bash
   cd /Users/mac/Developer/sally_love_voice_agent
   flyctl deploy --app sally-love-voice-agent
   ```
3. **Create form in GHL**
4. **Configure workflow with webhook**
5. **Test with real form submission**

---

## 📝 Example Form HTML (if embedding on website)

```html
<!-- GHL Form Embed -->
<iframe 
  src="https://link.msgsndr.com/form/YOUR_FORM_ID"
  style="width:100%;height:600px;border:none;"
  scrolling="yes">
</iframe>

<!-- Or use GHL form shortcode in your page builder -->
```

---

## ✅ Configuration Checklist

- [ ] Vapi Assistant ID obtained
- [ ] Configuration added to `.env`:
  - [ ] `VAPI_ASSISTANT_ID`
  - [ ] `GHL_WEBHOOK_SECRET`
  - [ ] `GHL_API_KEY`
  - [ ] `GHL_LOCATION_ID`
- [ ] App deployed to production
- [ ] Form created in GHL with phone field
- [ ] Workflow created with form trigger
- [ ] Webhook action configured in workflow
- [ ] Workflow activated
- [ ] Test form submitted
- [ ] User received call from Vapi
- [ ] AI agent had correct context
- [ ] Verified in logs

---

## 🔗 Related Documentation

- `GHL_WEBHOOK_QUICKSTART.md` - Quick start guide
- `docs/vapi/VAPI_SYSTEM_PROMPT_2.md` - Configure AI behavior
- `src/webhooks/ghl_webhooks.py` - Webhook code

---

## 💡 Tips & Best Practices

### 1. **Form Field Best Practices**
- Always require phone number
- Use phone validation
- Use proper field types (tel for phone)
- Include helpful placeholder text

### 2. **Call Timing**
- Add small delay in workflow (5-10 seconds) to give user time to prepare
- Don't call during off-hours (configure in Vapi assistant)
- Consider timezone of the user

### 3. **User Experience**
- Show "Thank you" message after form submit
- Tell user "You'll receive a call shortly"
- Set expectations: "within the next minute"

### 4. **Testing**
- Always test in TEST_MODE first
- Use your own phone number for initial tests
- Test with different form data variations

---

**Status:** ✅ Ready to configure  
**Last Updated:** December 22, 2025  
**Pattern:** Based on HVAC repository implementation

