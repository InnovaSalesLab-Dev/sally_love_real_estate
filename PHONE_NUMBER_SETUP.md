# Phone Number Setup Guide: 352-399-2010

This guide will help you configure the business phone number `352-399-2010` (+13523992010) for the AI voice agent.

---

## 📋 Current Status

✅ **Code Configuration**: Already set in `settings.py`
- `BUSINESS_PHONE`: `+13523992010`
- `TWILIO_PHONE_NUMBER`: `+13523992010`

❌ **Twilio**: Needs to be purchased/configured
❌ **Vapi**: Needs to be configured as assistant phone number

---

## Step 1: Configure Phone Number in Twilio

### Option A: If You Already Own This Number in Twilio

1. **Go to Twilio Console**: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. **Find your number**: Search for `+13523992010` or `3523992010`
3. **Verify it's active**: Make sure the number shows as "Active"
4. **Note the Phone Number SID**: You'll need this (starts with `PN...`)

### Option B: If You Need to Purchase This Number

1. **Go to Twilio Console**: https://console.twilio.com/us1/develop/phone-numbers/manage/search
2. **Search for the number**: Enter `352-399-2010` or area code `352`
3. **Purchase the number**: If available, click "Buy" and complete purchase
4. **Note the Phone Number SID**: After purchase, note the SID (starts with `PN...`)

### Option C: If Number is Not Available in Twilio

If the number is already owned by someone else or not available:

1. **Purchase a new Twilio number** in the same area code (352)
2. **Update your `.env` file** with the new number:
   ```bash
   TWILIO_PHONE_NUMBER=+1XXXXXXXXXX  # New Twilio number
   BUSINESS_PHONE=+1XXXXXXXXXX        # New Twilio number
   ```
3. **Update Vapi configuration** (see Step 2) with the new number

---

## Step 2: Configure Phone Number in Vapi

### 2.1 Get Your Phone Number SID from Twilio

1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Click on your phone number `+13523992010`
3. Copy the **Phone Number SID** (looks like: `PNxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

### 2.2 Add Phone Number to Vapi Assistant

1. **Go to Vapi Dashboard**: https://dashboard.vapi.ai/
2. **Select your Assistant** (or create a new one)
3. **Go to Phone Numbers section**:
   - Click on **"Phone Numbers"** in the left sidebar
   - Or go to **Settings** → **Phone Numbers**

4. **Add New Phone Number**:
   - Click **"Add Phone Number"** or **"Connect Phone Number"**
   - Select **"Twilio"** as the provider
   - Enter your **Twilio Account SID** (from `.env`: `TWILIO_ACCOUNT_SID`)
   - Enter your **Twilio Auth Token** (from `.env`: `TWILIO_AUTH_TOKEN`)
   - Enter your **Phone Number SID** (from Step 2.1: `PN...`)

5. **Save Configuration**

### 2.3 Assign Phone Number to Assistant

1. **Go to Assistant Settings**:
   - Click on your assistant
   - Go to **Settings** → **Phone Numbers**

2. **Select the Phone Number**:
   - Find `+13523992010` in the list
   - Click **"Assign"** or toggle it **ON**

3. **Configure Call Settings** (if needed):
   - Set **"Inbound Calls"** to **Enabled**
   - Set **"Outbound Calls"** to **Enabled** (if needed)
   - Configure **"Call Recording"** (optional)

4. **Save Changes**

---

## Step 3: Update Environment Variables

Make sure your `.env` file has the correct Twilio credentials:

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+13523992010

# Business Configuration
BUSINESS_PHONE=+13523992010
```

**Note**: The phone number should be in E.164 format: `+13523992010` (no dashes, spaces, or parentheses)

---

## Step 4: Verify Configuration

### Test Twilio Connection

Run the integration test:

```bash
cd /Users/mac/Developer/sally_love_voice_agent
source .venv/bin/activate
python scripts/test_integrations.py
```

You should see:
```
Twilio ✅ PASSED
```

### Test Phone Number in Vapi

1. **Go to Vapi Dashboard** → Your Assistant
2. **Click "Test"** or use the phone number to make a test call
3. **Call the number**: `+13523992010` (or `352-399-2010`)
4. **Verify**: The AI should answer and handle the call

---

## Step 5: Update Vapi Phone Number ID (Optional)

If Vapi provides a Phone Number ID after configuration, you can add it to your `.env`:

```bash
VAPI_PHONE_NUMBER_ID=your_vapi_phone_number_id_here
```

This is optional but can be useful for programmatic management.

---

## 🔍 Troubleshooting

### Issue: "Phone number not found in Twilio"

**Solution**:
- Verify the number exists in your Twilio account
- Check that you're using the correct Account SID and Auth Token
- Make sure the number is active (not suspended)

### Issue: "Cannot assign phone number in Vapi"

**Solution**:
- Verify Twilio credentials are correct in Vapi dashboard
- Check that Phone Number SID is correct (starts with `PN`)
- Ensure the number has SMS/Voice capabilities enabled in Twilio

### Issue: "Calls not connecting"

**Solution**:
- Verify the phone number is assigned to your assistant in Vapi
- Check Vapi assistant is active and published
- Verify webhook URLs are correct (should point to your Fly.io deployment)

### Issue: "SMS not working"

**Solution**:
- Enable SMS capabilities for the number in Twilio Console
- Check Geo Permissions if sending to international numbers
- Verify `TWILIO_PHONE_NUMBER` in `.env` matches the configured number

---

## 📞 Important Notes

1. **Number Format**: Always use E.164 format (`+13523992010`) in code/config
2. **Display Format**: Can display as `352-399-2010` in UI/messages
3. **Twilio Costs**: Phone numbers have monthly costs + per-minute/per-SMS charges
4. **Vapi Costs**: Vapi charges per minute for phone calls
5. **Testing**: Use `TEST_MODE=true` in `.env` to route transfers to your test number

---

## ✅ Checklist

- [ ] Phone number exists in Twilio Console
- [ ] Phone Number SID copied (`PN...`)
- [ ] Twilio credentials added to Vapi
- [ ] Phone number assigned to Vapi assistant
- [ ] `.env` file updated with correct `TWILIO_PHONE_NUMBER`
- [ ] Integration test passes (`python scripts/test_integrations.py`)
- [ ] Test call made successfully
- [ ] SMS test works (if needed)

---

## 🆘 Need Help?

- **Twilio Support**: https://support.twilio.com/
- **Vapi Support**: https://docs.vapi.ai/ or support@vapi.ai
- **Check Logs**: `logs/app.log` for detailed error messages

---

**Last Updated**: December 15, 2025

