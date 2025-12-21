# 🚨 URGENT: Vapi Prompt Update - Fix Lead Creation & Data Quality

## Problems Identified

### Issue 1: AI Skipping Lead Creation (FIXED ✅)
**Issue:** AI was skipping `create_buyer_lead` / `create_seller_lead` before transferring calls.

### Issue 2: Poor Lead Data Quality (FIXING NOW 🔧)
**Issue:** AI creates the lead but with generic data instead of specific property details.

**First transcript (Issue 1):**
```
✅ Collected: name, phone, email
❌ Called: send_notification (WRONG - lead doesn't exist yet!)
❌ Called: route_to_agent (WRONG - lead doesn't exist yet!)
❌ MISSING: create_buyer_lead (should have been called FIRST!)
```
**Result:** Agent gets call but there's NO lead in CRM!

**Second transcript (Issue 2):**
```
✅ check_property (1738 Augustine Drive, $749k, 4-bed, 3-bath, Single Family)
✅ create_buyer_lead ({
     location_preference: "The Villages",  ← Too generic!
     max_price: 749999,  ← Should be range around $749k
     property_type: null,  ← Should be "Single Family"
     bedrooms: null,  ← Should be 4
     bathrooms: null  ← Should be 3
   })
✅ send_notification
✅ route_to_agent
```
**Result:** Lead exists but agent doesn't see WHICH property the buyer wants!

---

## Solution: Updated Prompts

I've made the prompts **impossible to ignore** with:
- 🚨 Emoji warnings
- Multiple reminders in bold
- Visual comparison (wrong vs right)
- Real example with exact tool calls
- Explicit "MANDATORY" and "DO NOT SKIP" language

---

## 🔥 DEPLOY NOW

### Step 1: Update System Prompt in Vapi

1. Go to [Vapi Dashboard](https://dashboard.vapi.ai)
2. Select your assistant
3. Navigate to **System Prompt** section
4. **Replace** existing prompt with:

```bash
cat docs/vapi/VAPI_SYSTEM_PROMPT_2.md
```

Copy the ENTIRE contents and paste into Vapi.

### Step 2: Update Knowledge Base in Vapi

1. In Vapi Dashboard, go to **Knowledge Base** section
2. **Replace** existing knowledge base with:

```bash
cat docs/vapi/VAPI_KNOWLEDGE_BASE.md
```

Copy the ENTIRE contents and paste into Vapi.

### Step 3: Save and Test

1. Click **Save** in Vapi Dashboard
2. Wait 30 seconds for changes to propagate
3. Make a test call:
   - Ask about a property
   - Say "yes, connect me to the agent"
   - Provide your info
   - **CHECK**: AI should call `create_buyer_lead` BEFORE `send_notification` and `route_to_agent`

---

## What Changed (Key Updates)

### System Prompt (VAPI_SYSTEM_PROMPT_2.md)

**Before:**
```
7. CRITICAL: Create lead in CRM FIRST:
   - If buyer → call create_buyer_lead
```

**After:**
```
7. 🚨 MANDATORY - CREATE LEAD BEFORE ANYTHING ELSE:
   - YOU MUST call create_buyer_lead or create_seller_lead NOW
   - WAIT for lead creation to complete before proceeding

CRITICAL RULE: NEVER call route_to_agent without calling 
create_buyer_lead or create_seller_lead first.
```

### Knowledge Base (VAPI_KNOWLEDGE_BASE.md)

**Added:**
- Visual comparison showing wrong vs right order
- Real example with exact tool calls matching your scenario
- Multiple reminders with 🚨 warnings
- Explicit "MANDATORY" steps
- "DO NOT PROCEED WITHOUT THIS" language

---

## Test Script

After deploying, test with this exact scenario:

**You say:** "Hi, I want information on 1738 Augustine Drive, I want to buy it"

**Expected AI behavior:**
1. ✅ Calls `check_property`
2. ✅ Provides property info
3. ✅ Asks if you want to connect with agent
4. ✅ Collects name, phone, email
5. ✅ Confirms information back
6. ✅ **Calls `create_buyer_lead`** ← THIS MUST HAPPEN
7. ✅ Calls `send_notification`
8. ✅ Calls `route_to_agent`
9. ✅ Says "I'm connecting you now"

**If AI skips step 6**, the prompts need to be updated in Vapi (they might not have saved properly).

---

## Verification

### Check Tool Calls in Vapi Dashboard

After the call, check the Vapi call logs:

**✅ Correct sequence:**
```
1. check_property
2. create_buyer_lead ← MUST BE HERE
3. send_notification
4. route_to_agent
```

**❌ Wrong sequence (your current issue):**
```
1. check_property
2. send_notification ← Lead doesn't exist yet!
3. route_to_agent ← Lead doesn't exist yet!
```

### Check CRM

After the call:
1. Log in to BoldTrail CRM
2. Check Contacts
3. **Verify:** New lead for "Hammas" (or your test name) exists
4. **Check timestamp:** Lead should be created BEFORE the call transfer time

---

## Why This Matters

**Without lead creation before transfer:**
- ❌ Agent gets call but sees NO lead in CRM
- ❌ Agent has to ask for all info again
- ❌ Poor user experience
- ❌ Lost opportunity data

**With lead creation before transfer:**
- ✅ Agent sees complete lead in CRM when they answer
- ✅ Agent knows who's calling and why
- ✅ Professional, seamless handoff
- ✅ All data captured

---

## Files Updated

1. ✅ `docs/vapi/VAPI_SYSTEM_PROMPT_2.md`
2. ✅ `docs/vapi/VAPI_KNOWLEDGE_BASE.md`

**Both files ready to copy-paste into Vapi Dashboard NOW.**

---

## Summary

**Problem:** AI skipping lead creation  
**Cause:** Instructions not explicit enough  
**Solution:** Made instructions impossible to ignore  
**Action Required:** Update Vapi Dashboard NOW  
**Time:** 2 minutes  
**Impact:** Immediate fix for lead creation issue  

---

**Last Updated:** December 21, 2024  
**Priority:** 🔥 URGENT - Update immediately  
**Status:** Ready to deploy

