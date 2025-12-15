# Route to Agent - Implementation Guide

## 🎯 Understanding Vapi Call Transfers

In Vapi.ai, call transfers are handled through **Server Actions** or by returning transfer instructions in the function response. The backend function prepares the transfer data, and Vapi executes the actual transfer.

---

## ✅ Current Implementation Status

Your `route_to_agent.py` function is **correctly implemented** for Vapi. It:
1. ✅ Verifies agent in BoldTrail CRM
2. ✅ Formats phone number correctly
3. ✅ Returns transfer data in the response
4. ✅ Handles errors gracefully

**What it does:** Prepares all the data Vapi needs to perform the transfer.

---

## 🔧 How to Configure in Vapi Dashboard

### Step 1: Configure the Function Tool

1. Go to your Vapi Assistant → **Tools** → Add/Edit `route_to_agent`

2. **Tool Configuration:**
   - **Tool Name:** `route_to_agent`
   - **Request URL:** `https://sally-love-voice-agent.fly.dev/functions/route_to_agent`
   - **Method:** `POST`

3. **Request Body Parameters:**
   ```
   agent_id (string, required)
   agent_name (string, required)
   agent_phone (string, required)
   caller_name (string, optional)
   reason (string, optional)
   ```

4. **Response Body Variables to Extract:**
   ```
   success ($.success)
   message ($.message)
   agent_phone ($.data.agent_phone)
   verified ($.data.verified_in_crm)
   ```

---

## 🔄 Two Approaches for Call Transfer in Vapi

### **Approach 1: Server Action (Recommended)**

Vapi has a built-in **Server Action** for call transfers. Configure it like this:

1. **In Vapi Dashboard → Server Actions → Add New:**

   **Action Name:** `transfer_call`
   
   **Type:** `Transfer Call`
   
   **Configuration:**
   ```json
   {
     "type": "transfer",
     "phoneNumber": "{{agent_phone}}",
     "announcement": "Transferring you to {{agent_name}} now. Please hold."
   }
   ```

2. **Update System Prompt:**
   Add to your `VAPI_SYSTEM_PROMPT.md`:
   ```
   When you need to transfer a call:
   1. First call route_to_agent function with agent details
   2. If successful, use the Server Action "transfer_call" with the agent_phone from the response
   ```

### **Approach 2: Return Transfer Instructions (Alternative)**

If Vapi doesn't have a direct Server Action, modify your function response to include transfer instructions that Vapi can act on:

**Option A: Update Function Response Format**

Modify `route_to_agent.py` to return Vapi-specific transfer format:

```python
return VapiResponse(
    success=True,
    message=message,
    data={
        "action": "transfer",  # Tells Vapi this is a transfer request
        "phoneNumber": agent_phone,  # Phone number to transfer to
        "announcement": f"Transferring you to {agent_name} now. Please hold.",
        "agent_id": request.agent_id,
        "agent_name": agent_name,
        "caller_name": caller_name,
        "reason": transfer_reason,
        "verified_in_crm": bool(agent_data)
    }
)
```

**Option B: Use Vapi's Function Response Format**

Check Vapi documentation for their specific transfer response format. They might expect:
- `transferPhoneNumber` field
- `transferAction` field
- Or specific TwiML in the response

---

## 📝 Implementation Steps

### Step 1: Test Current Function (Already Done ✅)

Your function returns:
- ✅ Formatted phone number
- ✅ Agent verification status
- ✅ Transfer message
- ✅ All context needed

### Step 2: Configure in Vapi Dashboard

1. **Add/Update Tool Configuration** (as shown above)

2. **Add Server Action** for transfer:
   - Create a Server Action named `transfer_call`
   - Use `agent_phone` from function response
   - Configure announcement message

3. **Update System Prompt:**
   ```
   To transfer a call:
   1. Call route_to_agent with agent details
   2. Extract agent_phone from response
   3. Use transfer_call Server Action with that phone number
   ```

### Step 3: Test the Flow

**Test Scenario:**
```
1. AI: "I'll transfer you to Kim Coffer now."
2. AI calls route_to_agent function
3. Function returns: { agent_phone: "+13526267671", ... }
4. AI uses transfer_call Server Action with that phone
5. Vapi transfers the call
```

---

## 🔍 Alternative: Direct Twilio Transfer (If Needed)

If Vapi doesn't support automatic transfers, you can use Twilio directly via a Server Action:

### Create Twilio Transfer Server Action

**Action Type:** `Make HTTP Request`

**URL:** Your backend endpoint (you'd need to create)
**Method:** `POST`
**Body:**
```json
{
  "call_sid": "{{call.id}}",
  "transfer_to": "{{agent_phone}}"
}
```

**Backend Endpoint (if needed):**
```python
@router.post("/transfer_call")
async def transfer_call_via_twilio(request: TransferRequest):
    """Server Action endpoint for Vapi to call for transfers"""
    call_sid = request.call_sid
    transfer_to = request.transfer_to
    
    # Use Twilio to transfer
    result = await twilio_client.transfer_call(call_sid, transfer_to)
    
    return {"success": True, "transfer_initiated": True}
```

---

## ✅ Recommended Solution

**Best approach for Vapi:**

1. **Keep your current `route_to_agent.py` function** ✅ (It's correct!)

2. **Create a Server Action in Vapi:**
   - Name: `transfer_call`
   - Type: `Transfer Call` (if available) or `Make HTTP Request`
   - Use `{{agent_phone}}` from function response

3. **Update System Prompt:**
   ```
   When transferring calls:
   1. Use route_to_agent function first
   2. Get agent_phone from response
   3. Then execute transfer_call Server Action
   ```

4. **In Vapi Dashboard → Tools:**
   - The AI will automatically use the function, get the phone number
   - Then use the Server Action to transfer

---

## 🎯 Current Code Status

Your `route_to_agent.py` is **ready to use**. It:
- ✅ Validates agent in CRM
- ✅ Formats phone correctly  
- ✅ Returns all needed data
- ✅ Handles errors

**What you need:**
1. Configure the tool in Vapi dashboard (already documented in VAPI_TOOLS_CONFIGURATION.md)
2. Create a Server Action for the actual transfer
3. Update system prompt to use both in sequence

---

## 📞 Example Flow

```
Caller: "Can I speak to Kim Coffer?"

AI: "Of course! Let me connect you with Kim now."
[Calls route_to_agent function]

Function Response:
{
  "success": true,
  "message": "Great! I'm transferring you to Kim Coffer now...",
  "data": {
    "agent_phone": "+13526267671",
    "agent_name": "Kim Coffer",
    "verified_in_crm": true
  }
}

AI: "Great! I'm transferring you to Kim Coffer now. Please hold."
[Uses transfer_call Server Action with +13526267671]

→ Call transfers to Kim
```

---

## 🚨 Important Notes

1. **Phone Format:** Your code already formats to `+1...` format ✅
2. **CRM Verification:** Always verifies agent exists before transfer ✅
3. **Error Handling:** Falls back gracefully if CRM lookup fails ✅
4. **Data Returned:** All transfer info is in the response ✅

**Your code is production-ready!** You just need to configure the Server Action in Vapi dashboard.

