# Route to Agent - Full Implementation Guide

## ✅ Implementation Complete

The `route_to_agent.py` function has been fully implemented using **Vapi's Live Call Control API** for dynamic call transfers.

**Reference:** [Vapi Dynamic Call Transfers Documentation](https://docs.vapi.ai/calls/call-dynamic-transfers)

---

## 🎯 How It Works

### 1. **Vapi Calls Your Function**
   - When the AI decides to transfer a call, Vapi sends a webhook to your function endpoint
   - The webhook includes:
     - `message.call.monitor.controlUrl` - The URL to POST to for executing the transfer
     - `message.toolWithToolCallList[0].toolCall.function.arguments` - Function parameters (agent_id, agent_name, agent_phone, etc.)

### 2. **Your Function Executes Transfer**
   - Extracts the `controlUrl` from the webhook
   - Verifies agent in BoldTrail CRM (optional but recommended)
   - Formats phone number to E.164 format (`+1...`)
   - POSTs transfer request to `{controlUrl}/control` with:
     ```json
     {
       "type": "transfer",
       "destination": {
         "type": "number",
         "number": "+1234567890"
       },
       "content": "Transferring you to Agent Name now. Please hold."
     }
     ```

### 3. **Vapi Transfers the Call**
   - Vapi receives the transfer request
   - Connects the caller to the specified phone number
   - Call is transferred ✅

---

## 📋 Function Parameters

The function accepts parameters from Vapi in this format:

```json
{
  "agent_id": "string",      // Required: Agent's BoldTrail ID
  "agent_name": "string",    // Required: Agent's name
  "agent_phone": "string",   // Required: Agent's phone number
  "caller_name": "string",   // Optional: Caller's name
  "reason": "string"         // Optional: Reason for transfer
}
```

---

## ✅ What the Implementation Does

1. **Extracts Control URL**
   - Reads `message.call.monitor.controlUrl` from Vapi webhook
   - Handles both Vapi webhook format and direct parameter format (backward compatible)

2. **Extracts Function Parameters**
   - Parses from `message.toolWithToolCallList[0].toolCall.function.arguments`
   - Handles both JSON string and object formats

3. **Verifies Agent in CRM**
   - Calls `crm_client.get_agent(agent_id)` to verify agent exists
   - Uses CRM phone number if available and provided phone is missing
   - Updates agent name from CRM if available

4. **Formats Phone Number**
   - Converts to E.164 format (`+1XXXXXXXXXX`)
   - Handles various input formats (with/without dashes, parentheses, etc.)

5. **Executes Transfer**
   - POSTs to `{controlUrl}/control` with transfer payload
   - Uses Vapi's Live Call Control API format
   - Includes transfer message for caller

6. **Returns Response**
   - Success: Returns confirmation with agent details
   - Failure: Returns error message with graceful fallback

---

## 🔧 Vapi Dashboard Configuration

### Tool Configuration

In Vapi Dashboard → Tools → `route_to_agent`:

**Tool Type:** Custom Function

**Function Name:** `route_to_agent`

**Description:**
```
Transfer the call to a specific real estate agent. Use when caller requests to speak with someone, has complex questions, or needs immediate assistance. NEVER discuss commission rates - always transfer to agent.
```

**Parameters:**
```json
{
  "type": "object",
  "properties": {
    "agent_id": {
      "type": "string",
      "description": "Agent's unique ID from BoldTrail CRM"
    },
    "agent_name": {
      "type": "string",
      "description": "Agent's name (e.g., 'Kim Coffer', 'Sally Love')"
    },
    "agent_phone": {
      "type": "string",
      "description": "Agent's phone number for transfer"
    },
    "caller_name": {
      "type": "string",
      "description": "Name of the person calling (optional)"
    },
    "reason": {
      "type": "string",
      "description": "Reason for transfer (e.g., 'property inquiry', 'listing agent', 'general question')"
    }
  },
  "required": ["agent_id", "agent_name", "agent_phone"]
}
```

**Server URL:** `https://sally-love-voice-agent.fly.dev/functions/route_to_agent`

**HTTP Method:** `POST`

### Important: Async Tool Setting

Make sure the tool is configured as **async** in Vapi:
- This allows Vapi to send the `controlUrl` in the webhook
- Required for Live Call Control API to work

---

## 📝 System Prompt Instructions

Add to your `VAPI_SYSTEM_PROMPT.md`:

```
When transferring calls:
1. Collect caller's name and phone number FIRST
2. Use route_to_agent function with:
   - agent_id (if available from check_property or get_agent_info)
   - agent_name (full name)
   - agent_phone (phone number in any format - function will format it)
   - caller_name (name of person calling)
   - reason (brief reason: "property inquiry", "listing agent", etc.)
3. The function will automatically execute the transfer
4. Announce: "Transferring you to [Agent Name] now. Please hold."
```

---

## 🔍 Example Flow

```
Caller: "Can I speak to Kim Coffer about the property?"

AI: "Of course! Let me connect you with Kim. Can I get your name first?"

Caller: "John Smith"

AI: "Perfect, John. One moment while I transfer you."
[Calls route_to_agent function]

Function receives:
{
  "message": {
    "call": {
      "monitor": {
        "controlUrl": "https://api.vapi.ai/call/abc123/control"
      }
    },
    "toolWithToolCallList": [{
      "toolCall": {
        "function": {
          "arguments": {
            "agent_id": "2013895",
            "agent_name": "Kim Coffer",
            "agent_phone": "352-626-7671",
            "caller_name": "John Smith",
            "reason": "property inquiry"
          }
        }
      }
    }]
  }
}

Function:
1. Extracts controlUrl: "https://api.vapi.ai/call/abc123/control"
2. Verifies agent in CRM (optional)
3. Formats phone: "+13526267671"
4. POSTs to controlUrl:
   {
     "type": "transfer",
     "destination": {
       "type": "number",
       "number": "+13526267671"
     },
     "content": "Transferring you to Kim Coffer now. Please hold."
   }

Vapi transfers the call → Caller connected to Kim ✅
```

---

## 🛠️ Error Handling

The function handles errors gracefully:

1. **No controlUrl**: Returns error but doesn't crash
2. **CRM verification fails**: Still attempts transfer with provided phone
3. **Invalid phone format**: Attempts to clean and format
4. **Transfer execution fails**: Returns error with helpful message
5. **Missing parameters**: Validates and returns clear error

---

## ✅ Testing

### Test 1: Direct Function Call (Development)

```bash
curl -X POST https://sally-love-voice-agent.fly.dev/functions/route_to_agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "call": {
        "monitor": {
          "controlUrl": "TEST_CONTROL_URL"
        }
      },
      "toolWithToolCallList": [{
        "toolCall": {
          "function": {
            "arguments": {
              "agent_id": "2013895",
              "agent_name": "Hammas",
              "agent_phone": "+923035699010",
              "caller_name": "Test User",
              "reason": "property inquiry"
            }
          }
        }
      }]
    }
  }'
```

### Test 2: Via Vapi (Production)

1. Make a test call to your Vapi number
2. Ask AI to transfer to an agent
3. Monitor logs to see:
   - Function called ✅
   - Control URL extracted ✅
   - Transfer executed ✅
   - Call connected ✅

---

## 📊 Logging

The function logs:
- Transfer requests with agent details
- CRM verification status
- Phone number formatting
- Transfer execution status
- Any errors with full context

Check logs at: Your deployment platform (Fly.io) logs

---

## 🎯 Success Criteria

✅ Function receives Vapi webhook with controlUrl  
✅ Extracts function parameters correctly  
✅ Verifies agent in BoldTrail CRM  
✅ Formats phone number to E.164  
✅ Executes transfer via POST to controlUrl  
✅ Returns success response  
✅ Handles all error cases gracefully  

---

## 📚 References

- [Vapi Dynamic Call Transfers](https://docs.vapi.ai/calls/call-dynamic-transfers)
- [Vapi Live Call Control API](https://docs.vapi.ai/api-reference/call-control)
- [E.164 Phone Number Format](https://en.wikipedia.org/wiki/E.164)

