# 📞 How to Connect Your Phone Number to Sally Love Assistant

## 🔍 The Problem

You've added the phone number `+1 (813) 733 6160` in Vapi, but calls aren't connecting because **the phone number isn't assigned to your assistant**.

In Vapi, there are two separate steps:
1. ✅ **Add the phone number** (you've done this)
2. ❌ **Assign the phone number to an assistant** (this is missing!)

---

## ✅ Solution: Assign Phone Number to Assistant

### Step 1: Find Your Assistant ID

**Find your assistant in the Vapi Dashboard:**

1. Go to https://dashboard.vapi.ai
2. Click on **"Assistants"** in the left sidebar
3. Find your assistant (e.g., "Riley - Inbound" or "Sally Love Real Estate Assistant")
4. Click on it to see the Assistant ID (it will be displayed at the top, looks like: `abc123-def456-ghi789`)

**If you don't have an assistant yet:**
- Create one in the Vapi dashboard
- Copy the system prompt from `VAPI_SYSTEM_PROMPT.md`
- Configure function endpoints to point to your deployed server URL

---

### Step 2: Assign Phone Number to Assistant in Vapi Dashboard

1. **Go to Vapi Dashboard**: https://dashboard.vapi.ai/

2. **Navigate to Assistants**:
   - Click on **"Assistants"** in the left sidebar
   - Find your assistant: **"Sally Love Real Estate Assistant"**
   - Click on it to open the assistant settings

3. **Go to Phone Numbers Section**:
   - In the assistant settings page, look for **"Phone Numbers"** or **"Inbound Calls"** section
   - You should see a list of available phone numbers

4. **Assign Your Phone Number**:
   - Find `+1 (813) 733 6160` in the list
   - Toggle it **ON** or click **"Assign"**
   - Or use the dropdown to select this phone number

5. **Save Changes**:
   - Click **"Save"** or the changes may auto-save

---

### Alternative Method: From Phone Numbers Page

If the above doesn't work, try this:

1. **Go to Phone Numbers**:
   - Click **"Phone Numbers"** in the left sidebar
   - Click on `+1 (813) 733 6160`

2. **Assign to Assistant**:
   - Look for a field labeled **"Assistant"** or **"Assigned Assistant"**
   - Select **"Sally Love Real Estate Assistant"** from the dropdown
   - Save changes

---

## 🎯 What Should Happen After Assignment

Once the phone number is assigned to your assistant:

1. ✅ **Incoming calls** will route to your assistant
2. ✅ **Assistant will answer** with the configured greeting
3. ✅ **Functions will work** (check_property, create_buyer_lead, etc.)
4. ✅ **Webhooks will be sent** to your server URL

---

## 🔍 Verify the Configuration

### Check 1: Assistant Has Phone Number

In Vapi Dashboard → Assistants → Your Assistant:
- Phone number `+1 (813) 733 6160` should show as **"Assigned"** or **"Active"**

### Check 2: Phone Number Has Assistant

In Vapi Dashboard → Phone Numbers → `+1 (813) 733 6160`:
- Assistant field should show **"Sally Love Real Estate Assistant"**

### Check 3: Test the Connection

1. **Make a test call** to `+1 (813) 733 6160`
2. **You should hear**: "Thank you for calling Sally Love Real Estate! This is your virtual assistant. How can I help you today?"
3. **If you hear this**, the connection is working! ✅

---

## ⚠️ Important Notes About Server URL

The **Server URL** field you see in the phone number settings (`https://api.example.com/function`) is **NOT** what connects the phone to your assistant.

- **Server URL** (in phone number settings): Used for phone-specific webhooks (optional, advanced)
- **Assistant's serverUrl** (in assistant settings): Used for function calls (this is what matters!)

Your assistant should have the `serverUrl` configured in the assistant settings, which should point to your Fly.io deployment (e.g., `https://sally-love-voice-agent.fly.dev`). You don't need to change the phone number's Server URL field.

---

## 🐛 Troubleshooting

### Issue: "Phone number not assigned to any assistant"

**Solution:**
- Follow Step 2 above to assign the phone number to your assistant
- Make sure you're saving the changes

### Issue: "Can't find the assistant"

**Solution:**
1. Create the assistant in the Vapi dashboard:
   - Go to https://dashboard.vapi.ai → Assistants → Create Assistant
   - Copy system prompt from `VAPI_SYSTEM_PROMPT.md`
   - Configure function endpoints to your deployed server URL
2. Note the Assistant ID (shown in the assistant settings)
3. Then assign the phone number to the assistant in the dashboard

### Issue: "Call connects but AI doesn't respond"

**Possible causes:**
1. **Assistant's serverUrl is wrong** - Check that `WEBHOOK_BASE_URL` in your `.env` points to your Fly.io URL
2. **Server is down** - Check `flyctl status --app sally-love-voice-agent`
3. **Functions are failing** - Check logs: `flyctl logs --follow --app sally-love-voice-agent`

### Issue: "Call goes straight to voicemail or doesn't connect"

**Possible causes:**
1. **Phone number not assigned** - Follow Step 2 above
2. **Twilio configuration issue** - Verify the number is active in Twilio Console
3. **Vapi account issue** - Check Vapi billing/account status

---

## 📋 Quick Checklist

- [ ] Assistant exists in Vapi dashboard
- [ ] Phone number added in Vapi
- [ ] Phone number assigned to assistant in Vapi dashboard
- [ ] Assistant's `serverUrl` points to your deployment URL
- [ ] `.env` has correct `WEBHOOK_BASE_URL` (your Fly.io URL)
- [ ] Server is running (`flyctl status --app sally-love-voice-agent`)
- [ ] Test call works

---

## 🆘 Still Not Working?

1. **Check logs** for incoming requests:
   ```bash
   flyctl logs --follow --app sally-love-voice-agent
   ```

2. **Verify assistant configuration**:
   - Go to Vapi Dashboard → Assistants → Your Assistant
   - Check that `serverUrl` matches your Fly.io URL
   - Check that all functions are listed correctly

3. **Verify phone number configuration**:
   - Go to Vapi Dashboard → Phone Numbers → `+1 (813) 733 6160`
   - Check that it shows as assigned to your assistant

4. **Check Vapi call logs**:
   - Go to Vapi Dashboard → Calls
   - Look for recent calls to see if they're being received
   - Check call status and any error messages

---

## 📞 Next Steps After Connection Works

Once calls are connecting:

1. ✅ Test all functions:
   - Property search
   - Agent lookup
   - Buyer lead creation
   - Seller lead creation
   - Call transfers (with TEST_MODE enabled)

2. ✅ Monitor logs during test calls:
   ```bash
   flyctl logs --follow --app sally-love-voice-agent
   ```

3. ✅ Verify CRM integration:
   - Check that leads are being created in BoldTrail
   - Verify SMS notifications are being sent

---

**Last Updated**: Based on current Vapi dashboard interface (December 2025)

