# 🧪 TEST_MODE Configuration Guide

## ✅ What You've Configured

Based on your `.env` file:
```
TEST_MODE=true
```

## 📋 What This Means

### 1. **Call Transfers (Warm Transfers)**

When `TEST_MODE=true`, all call transfers via `route_to_agent` will be redirected to your test number instead of the real agent's number.

**How it works:**
- User requests to speak with an agent (e.g., "Kim Coffer")
- System looks up agent in BoldTrail CRM
- **TEST MODE OVERRIDES**: Instead of transferring to Kim's real number (352-626-7671), it transfers to your test number
- You'll receive the call on your test phone

**Configuration needed in `.env`:**
```env
TEST_MODE=true
TEST_AGENT_NAME=Hammas Ali          # Optional: defaults to "Hammas Ali" if not set
TEST_AGENT_PHONE=+923035699010      # Optional: defaults to "+923035699010" if not set
```

**Default values** (if not set in `.env`):
- `TEST_AGENT_NAME`: "Hammas Ali" (from `src/config/settings.py`)
- `TEST_AGENT_PHONE`: "+923035699010" (from `src/config/settings.py`)

### 2. **SMS Notifications**

SMS notifications are **automatically sent** when leads are created. This is **separate** from TEST_MODE.

**What happens:**
- When a buyer lead is created → SMS sent to the buyer's phone number
- When a seller lead is created → SMS sent to the seller's phone number
- Messages sent to Sally/Jeff are handled by BoldTrail CRM (not by your code)

**Configuration needed in `.env` for SMS to work:**
```env
TWILIO_ACCOUNT_SID=AC...           # Your Twilio Account SID
TWILIO_AUTH_TOKEN=...              # Your Twilio Auth Token
TWILIO_PHONE_NUMBER=+13523992010   # Your Twilio phone number (must be verified in Twilio)
```

**⚠️ Important:**
- Twilio phone number must be verified for the regions you're sending SMS to
- If SMS isn't working, check Twilio console → Geo Permissions
- SMS logs will appear in your application logs (see VIEWING_LOGS.md)

---

## 🔍 How to Verify It's Working

### Step 1: Check Logs

Open logs in real-time (see VIEWING_LOGS.md):
```bash
flyctl logs --follow --app sally-love-voice-agent
```

### Step 2: Test Call Transfer

1. Make a test call via Vapi dashboard
2. Ask to speak with an agent
3. Watch logs for:
   ```
   INFO - TEST MODE: Overriding transfer from Kim Coffer (352-626-7671) to Hammas Ali (+923035699010)
   INFO - Returning transfer instruction for Hammas Ali at +923035699010
   ```
4. Your phone (+923035699010) should ring

### Step 3: Test SMS Notifications

1. Create a buyer or seller lead via test call
2. Watch logs for:
   ```
   INFO - Sending SMS to +923259094746: Hi Faiqa! Thank you for your interest...
   INFO - SMS sent successfully via Twilio
   ```
3. Check the buyer/seller's phone for the SMS message

---

## 🎯 What Happens in Each Scenario

### Scenario 1: Call Transfer Request

**User:** "Can I speak with an agent?"

**What happens:**
1. ✅ AI calls `route_to_agent` function
2. ✅ Function looks up agent in BoldTrail
3. ✅ **TEST_MODE overrides**: Transfers to `TEST_AGENT_PHONE` instead of real agent
4. ✅ You receive the call on your test number
5. ✅ Logs show: `TEST MODE: Overriding transfer...`

**Result:** ✅ You receive the call

---

### Scenario 2: Buyer Lead Created

**User:** "I want to buy a home"

**What happens:**
1. ✅ AI collects information (name, phone, preferences)
2. ✅ AI calls `create_buyer_lead` function
3. ✅ Lead saved to BoldTrail CRM
4. ✅ **Automatic SMS sent** to buyer's phone (via Twilio)
5. ✅ BoldTrail sends notifications to Sally/Jeff (handled by CRM)

**Result:** 
- ✅ Buyer receives SMS confirmation
- ✅ Lead saved in CRM
- ✅ Sally/Jeff notified by BoldTrail (if configured)

---

### Scenario 3: Seller Lead Created

**User:** "I want to sell my property"

**What happens:**
1. ✅ AI collects information (name, phone, property details)
2. ✅ AI calls `create_seller_lead` function
3. ✅ Lead saved to BoldTrail CRM
4. ✅ **Automatic SMS sent** to seller's phone (via Twilio)
5. ✅ BoldTrail sends notifications to Sally/Jeff (handled by CRM)

**Result:**
- ✅ Seller receives SMS confirmation
- ✅ Lead saved in CRM
- ✅ Sally/Jeff notified by BoldTrail (if configured)

---

## ⚙️ Current Configuration Status

Based on your `.env` file:

| Setting | Value | Status |
|---------|-------|--------|
| `TEST_MODE` | `true` | ✅ Enabled |
| `TEST_AGENT_NAME` | (not set - using default) | ✅ Default: "Hammas Ali" |
| `TEST_AGENT_PHONE` | (not set - using default) | ✅ Default: "+923035699010" |
| `TWILIO_ACCOUNT_SID` | (check your .env) | ⚠️ Verify it's set |
| `TWILIO_AUTH_TOKEN` | (check your .env) | ⚠️ Verify it's set |
| `TWILIO_PHONE_NUMBER` | (check your .env) | ⚠️ Verify it's set |

---

## 🚀 Next Steps

1. **Verify Twilio Configuration:**
   ```bash
   # Check if Twilio credentials are in .env
   grep -E "TWILIO" .env
   ```

2. **Test Call Transfer:**
   - Make a test call from Vapi dashboard
   - Request to speak with an agent
   - Confirm your phone rings (+923035699010)

3. **Test SMS Notifications:**
   - Create a test buyer/seller lead
   - Confirm SMS is received
   - Check logs for SMS delivery status

4. **Monitor Logs:**
   ```bash
   flyctl logs --follow --app sally-love-voice-agent
   ```

---

## 🔄 Switching Between Test and Production

### To Enable Test Mode:
```env
TEST_MODE=true
```

### To Disable Test Mode (Production):
```env
TEST_MODE=false
```

**After changing `.env`:**
- If running locally: Restart the server
- If deployed: Redeploy with `flyctl deploy --app sally-love-voice-agent`

---

## ❓ FAQ

**Q: Will I receive calls on my number when TEST_MODE=true?**
A: Yes! All transfers will go to `TEST_AGENT_PHONE` (+923035699010) instead of real agent numbers.

**Q: Will SMS messages work automatically?**
A: Yes, if Twilio is configured correctly. SMS is sent automatically when leads are created (not affected by TEST_MODE).

**Q: Will Sally and Jeff receive notifications?**
A: BoldTrail CRM handles notifications to agents. If BoldTrail is configured to notify agents on new leads, they'll receive notifications automatically.

**Q: Do I need to set TEST_AGENT_NAME and TEST_AGENT_PHONE?**
A: Only if you want to override the defaults. The defaults are:
- `TEST_AGENT_NAME`: "Hammas Ali"
- `TEST_AGENT_PHONE`: "+923035699010"

**Q: What if SMS isn't working?**
A: Check:
1. Twilio credentials in `.env`
2. Twilio Geo Permissions (must allow SMS to recipient's country)
3. Application logs for Twilio errors
4. Twilio console for delivery status

---

## 📞 Support

If transfers or SMS aren't working:
1. Check logs: `flyctl logs --follow --app sally-love-voice-agent`
2. Look for ERROR or WARNING messages
3. Verify all required `.env` variables are set
4. Test Twilio configuration separately (see `scripts/test_sms.py`)

