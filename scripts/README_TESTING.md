# Testing BoldTrail Functions

This directory contains test scripts to validate all BoldTrail API integrations.

## 📋 Test Scripts

### 1. `test_functions_boldtrail.py`
**Purpose:** Tests BoldTrail API integration directly (without FastAPI server)

**What it tests:**
- ✅ Direct API calls to BoldTrail
- ✅ All integration methods in `boldtrail.py`
- ✅ Response validation
- ✅ Helper methods (add_note, log_call)

**How to run:**
```bash
# Make sure you're in the project root
cd /Users/mac/Developer/sally_love_voice_agent

# Activate virtual environment
source .venv/bin/activate

# Run the test
python scripts/test_functions_boldtrail.py
```

**Requirements:**
- ✅ `.env` file with `BOLDTRAIL_API_KEY` configured
- ✅ No server needed (direct API calls)

---

### 2. `test_function_endpoints.py`
**Purpose:** Tests FastAPI function endpoints (as called from Vapi)

**What it tests:**
- ✅ HTTP endpoints (`/functions/check_property`, etc.)
- ✅ Full request/response flow
- ✅ End-to-end function validation
- ✅ As Vapi would call them

**How to run:**
```bash
# Terminal 1: Start the FastAPI server
python main.py

# Terminal 2: Run the tests
source .venv/bin/activate
python scripts/test_function_endpoints.py
```

**Requirements:**
- ✅ `.env` file with `BOLDTRAIL_API_KEY` configured
- ✅ FastAPI server running (`python main.py`)
- ✅ Server accessible at `http://localhost:8000` (or configured `WEBHOOK_BASE_URL`)

---

## 🎯 What Gets Tested

### ✅ Function: `check_property`
- Search listings by city
- Search by price range
- Search by bedrooms/bathrooms
- Get property types

### ✅ Function: `get_agent_info`
- Get all active agents
- Search agents by name
- Search agents by city
- Get agent by ID

### ✅ Function: `create_buyer_lead`
- Create buyer contact in BoldTrail
- Set leadType to "Buyer"
- Store preferences in notes
- Return contact ID

### ✅ Function: `create_seller_lead`
- Create seller contact in BoldTrail
- Set leadType to "Seller"
- Store property details in notes
- Return contact ID

### ✅ Function: `route_to_agent`
- Verify agent exists in BoldTrail
- Get agent phone from CRM
- Get agent name from CRM
- Prepare transfer data

### ✅ Helper Methods
- `add_note()` - Add notes to contacts
- `log_call()` - Log call activities

---

## 📊 Expected Results

### ✅ Success Indicators:
- All tests show "✅ PASSED"
- Response data contains expected fields
- Contact IDs are returned
- No API errors

### ⚠️ Common Issues:

**1. API Key Not Set**
```
❌ ERROR: BOLDTRAIL_API_KEY not set in .env file
```
**Fix:** Add `BOLDTRAIL_API_KEY=your_key_here` to `.env`

---

**2. Server Not Running** (for endpoint tests)
```
❌ Health check failed. Is the server running?
```
**Fix:** Start server with `python main.py` in another terminal

---

**3. API Authentication Failed**
```
❌ BoldTrail connection failed: 401 Unauthorized
```
**Fix:** Check your `BOLDTRAIL_API_KEY` is correct and active

---

**4. No Data Found**
```
⚠️ No agents found - skipping agent ID test
```
**Note:** This is OK if your BoldTrail account doesn't have agents/listings yet

---

## 🔍 Understanding Test Output

### Sample Output:
```
================================================================================
  1. Testing check_property (Manual Listings)
================================================================================

📋 Test 1.1: Search listings by city (Ocala)

✅ PASSED - Search by city
   Found 3 listings
   Sample listing: 123 Main St - $350000

📋 Test 1.2: Search listings by price range

✅ PASSED - Search by price range
   Found 2 listings in price range

================================================================================
  TEST RESULTS SUMMARY
================================================================================
check_property          ✅ PASSED
get_agent_info          ✅ PASSED
create_buyer_lead       ✅ PASSED
create_seller_lead      ✅ PASSED
route_to_agent          ✅ PASSED
add_note                ✅ PASSED
log_call                ✅ PASSED
================================================================================

Total: 7/7 tests passed

✅ All function tests passed! BoldTrail integration is working correctly.
```

---

## 🚀 Quick Start

### Test BoldTrail Integration Directly:
```bash
source .venv/bin/activate
python scripts/test_functions_boldtrail.py
```

### Test Function Endpoints:
```bash
# Terminal 1
python main.py

# Terminal 2
source .venv/bin/activate
python scripts/test_function_endpoints.py
```

---

## 📝 Notes

1. **Test Data:** The scripts create test contacts in your BoldTrail account. You may want to clean these up later.

2. **Rate Limits:** BoldTrail may have rate limits. If tests fail due to rate limiting, wait a few minutes and try again.

3. **Environment:** Make sure your `.env` file is properly configured:
   ```
   BOLDTRAIL_API_KEY=your_key_here
   BOLDTRAIL_API_URL=https://api.kvcore.com/v2/public
   BOLDTRAIL_ACCOUNT_ID=your_account_id
   ```

4. **Validation:** These tests verify:
   - ✅ Correct API endpoints are used
   - ✅ Request payloads are properly formatted
   - ✅ Responses are correctly parsed
   - ✅ Error handling works
   - ✅ All required fields are present

---

**Last Updated:** December 12, 2025

