# 📊 Viewing Real-Time Logs

This guide shows you how to monitor logs in real-time when testing from the Vapi dashboard.

## 🚀 Quick Start

### Option 1: Fly.io Production Logs (Recommended)

If your app is deployed on Fly.io, use this command to see logs in real-time:

```bash
flyctl logs --follow --app sally-love-voice-agent
```

**What you'll see:**
- All incoming requests from Vapi
- Tool call executions (`route_to_agent`, `create_buyer_lead`, etc.)
- API responses to BoldTrail and Twilio
- Error messages and stack traces
- Detailed request/response payloads

**Tips:**
- Press `Ctrl+C` to stop following logs
- Add `| grep "route_to_agent"` to filter specific functions
- Logs show timestamps, log levels, and full request data

### Option 2: Local Development Logs

If running locally:

```bash
# Start the server with logging
cd /Users/mac/Developer/sally_love_voice_agent
source .venv/bin/activate
python main.py
```

Logs will appear directly in your terminal.

### Option 3: Log File

Logs are also saved to: `logs/app.log`

View in real-time:
```bash
tail -f logs/app.log
```

Or view recent logs:
```bash
tail -n 100 logs/app.log
```

---

## 🔍 What to Look For When Testing

When you test from Vapi dashboard, watch for these log entries:

### 1. **Function Call Received**
```
INFO - VAPI WEBHOOK RECEIVED - route_to_agent
INFO - Full payload: {...}
```

### 2. **Agent Transfer**
```
INFO - Routing call to agent: Hammas Ali (+923035699010)
INFO - TEST MODE: Overriding transfer from ... to Hammas Ali (+923035699010)
INFO - Returning transfer instruction for Hammas Ali at +923035699010
```

### 3. **Lead Creation**
```
INFO - Creating buyer lead for: Faiqa
INFO - BoldTrail API Response: {...}
INFO - Contact ID extracted: 123456
INFO - Note added successfully for contact: 123456
```

### 4. **SMS Notifications**
```
INFO - Sending SMS to +13523992010: New buyer lead: Faiqa...
INFO - SMS sent successfully via Twilio
```

### 5. **Errors**
```
ERROR - Failed to add note for contact 123456: ...
WARNING - Could not verify agent in BoldTrail: ...
```

---

## 🎯 Filtering Logs

### Filter by Function Name
```bash
flyctl logs --follow --app sally-love-voice-agent | grep "route_to_agent"
flyctl logs --follow --app sally-love-voice-agent | grep "create_buyer_lead"
```

### Filter by Log Level
```bash
flyctl logs --follow --app sally-love-voice-agent | grep "ERROR"
flyctl logs --follow --app sally-love-voice-agent | grep "WARNING"
```

### Filter by Contact ID or Phone
```bash
flyctl logs --follow --app sally-love-voice-agent | grep "+923259094746"
```

---

## 📱 Testing Checklist

When testing from Vapi dashboard:

1. ✅ **Open logs** before starting the test
   ```bash
   flyctl logs --follow --app sally-love-voice-agent
   ```

2. ✅ **Start test call** in Vapi dashboard

3. ✅ **Watch for:**
   - Function being called (`route_to_agent`, `create_buyer_lead`, etc.)
   - Request payload received
   - API responses (BoldTrail, Twilio)
   - Success/error messages

4. ✅ **Verify:**
   - Contact ID was extracted
   - Note was added
   - SMS was sent (if applicable)
   - Transfer destination was returned correctly

---

## 🔧 Log Levels

Current log level: `INFO` (set in `src/config/settings.py`)

Available levels:
- `DEBUG` - Most verbose (includes all details)
- `INFO` - Standard logging (current setting)
- `WARNING` - Warnings only
- `ERROR` - Errors only

To change log level, update `LOG_LEVEL` in `.env`:
```
LOG_LEVEL=DEBUG
```

---

## 🐛 Troubleshooting

### No logs appearing?
1. Check if app is running: `flyctl status --app sally-love-voice-agent`
2. Restart the app: `flyctl machines restart --app sally-love-voice-agent`
3. Check log file exists: `ls -la logs/app.log`

### Logs are too verbose?
- Filter by specific function names (see Filtering Logs above)
- Change `LOG_LEVEL` to `WARNING` or `ERROR` in `.env`

### Missing request details?
- Set `LOG_LEVEL=DEBUG` in `.env` for more verbose logging
- Redeploy: `flyctl deploy --app sally-love-voice-agent`

---

## 📞 Testing Call Transfers

When testing `route_to_agent`:

1. **Watch for TEST_MODE override:**
   ```
   INFO - TEST MODE: Overriding transfer from Kim Coffer (352-626-7671) to Hammas Ali (+923035699010)
   ```

2. **Verify destination format:**
   ```
   INFO - Returning transfer instruction for Hammas Ali at +923035699010
   ```

3. **Check response format:**
   The logs will show the exact response being returned to Vapi. It should have `destination` at the root level.

---

## 💡 Pro Tips

1. **Use two terminals:**
   - Terminal 1: `flyctl logs --follow` (watch logs)
   - Terminal 2: Test in Vapi dashboard

2. **Save logs to file:**
   ```bash
   flyctl logs --app sally-love-voice-agent > test_logs.txt
   ```

3. **Search saved logs:**
   ```bash
   grep "contact_id" test_logs.txt
   grep "ERROR" test_logs.txt
   ```

4. **Real-time error monitoring:**
   ```bash
   flyctl logs --follow --app sally-love-voice-agent | grep -E "(ERROR|WARNING|Failed)"
   ```

