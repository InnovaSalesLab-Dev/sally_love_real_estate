# Vapi Dashboard - Tools Configuration Guide

**Complete configuration for all 6 Sally Love Real Estate voice agent functions**

**Base URL:** `https://sally-love-voice-agent.fly.dev`

---

## 📋 Quick Reference

| Tool Name | Endpoint | Method | Purpose |
|-----------|----------|--------|---------|
| `check_property` | `/functions/check_property` | POST | Search property listings |
| `get_agent_info` | `/functions/get_agent_info` | POST | Get agent information |
| `route_to_agent` | `/functions/route_to_agent` | POST | Transfer call to agent |
| `create_buyer_lead` | `/functions/create_buyer_lead` | POST | Create buyer lead |
| `create_seller_lead` | `/functions/create_seller_lead` | POST | Create seller lead |
| `send_notification` | `/functions/send_notification` | POST | Send SMS notifications |

---

## Tool 1: check_property

### Base Configuration

- **Tool Name:** `check_property`
- **Request URL:** `https://sally-love-voice-agent.fly.dev/functions/check_property`
- **Request HTTP Method:** `POST`

### Request Body

Click **"+ Add Property"** and add the following properties:

| Property Name | Type | Required | Description |
|---------------|------|----------|-------------|
| `address` | string | No | Property street address |
| `city` | string | No | City name (e.g., "Ocala", "Dunnellon") |
| `state` | string | No | State abbreviation (default: "FL") |
| `zip_code` | string | No | ZIP code |
| `mls_number` | string | No | MLS listing number |
| `property_type` | string | No | Type of property (single-family, condo, townhouse, land) |
| `min_price` | number | No | Minimum price |
| `max_price` | number | No | Maximum price |
| `bedrooms` | integer | No | Minimum number of bedrooms |
| `bathrooms` | number | No | Minimum number of bathrooms |

### Response Body

Click **"+ Add Property"** and extract:

| Variable | Type | Required | JSON Path | Description |
|----------|------|----------|-----------|-------------|
| `success` | boolean | Yes | `$.success` | Whether the request succeeded |
| `message` | string | Yes | `$.message` | Voice-friendly message for AI |
| `count` | integer | No | `$.data.count` | Number of properties found |
| `properties` | array | No | `$.results` | Array of property listings |

### Description

```
Search for properties in BoldTrail CRM by address, city, price range, bedrooms, bathrooms, or MLS number. Use this when caller asks about specific properties or wants to see what's available.
```

---

## Tool 2: get_agent_info

### Base Configuration

- **Tool Name:** `get_agent_info`
- **Request URL:** `https://sally-love-voice-agent.fly.dev/functions/get_agent_info`
- **Request HTTP Method:** `POST`

### Request Body

Click **"+ Add Property"** and add the following properties:

| Property Name | Type | Required | Description |
|---------------|------|----------|-------------|
| `agent_name` | string | No | Agent's name (e.g., "Sally Love", "Jeff") |
| `agent_id` | string | No | Agent's unique ID from CRM |
| `specialty` | string | No | Agent specialty (buyer_agent, listing_agent, commercial, luxury) |
| `city` | string | No | Service area/city (e.g., "Ocala") |

### Response Body

Click **"+ Add Property"** and extract:

| Variable | Type | Required | JSON Path | Description |
|----------|------|----------|-----------|-------------|
| `success` | boolean | Yes | `$.success` | Whether the request succeeded |
| `message` | string | Yes | `$.message` | Voice-friendly message about agents |
| `agent_count` | integer | No | `$.data.count` | Number of agents found |
| `agents` | array | No | `$.results` | Array of agent objects |
| `agent_name` | string | No | `$.results[0].firstName` | First agent's name |
| `agent_phone` | string | No | `$.results[0].phone` | First agent's phone |
| `agent_id` | string | No | `$.results[0].id` | First agent's ID |

### Description

```
Get information about real estate agents including contact details, specialties, service areas, and availability. Use when caller asks about specific agents or needs help from a specialist.
```

---

## Tool 3: route_to_agent

### Base Configuration

- **Tool Name:** `route_to_agent`
- **Request URL:** `https://sally-love-voice-agent.fly.dev/functions/route_to_agent`
- **Request HTTP Method:** `POST`

### Request Body

Click **"+ Add Property"** and add the following properties:

| Property Name | Type | Required | Description |
|---------------|------|----------|-------------|
| `agent_id` | string | **Yes** | Agent's unique ID from CRM |
| `agent_name` | string | **Yes** | Agent's name (e.g., "Sally Love", "Jeff") |
| `agent_phone` | string | **Yes** | Agent's phone number |
| `caller_name` | string | No | Name of the person calling |
| `reason` | string | No | Reason for transfer (e.g., "property inquiry", "commission question", "urgent request") |

### Response Body

Click **"+ Add Property"** and extract:

| Variable | Type | Required | JSON Path | Description |
|----------|------|----------|-----------|-------------|
| `success` | boolean | Yes | `$.success` | Whether transfer initiated |
| `message` | string | Yes | `$.message` | Voice-friendly transfer message |
| `agent_phone` | string | No | `$.data.agent_phone` | Formatted agent phone for transfer |
| `verified` | boolean | No | `$.data.verified_in_crm` | Whether agent was verified in CRM |

### Description

```
Transfer the call to a specific real estate agent or broker. Use when caller requests to speak with someone, has complex questions, or needs immediate assistance. NEVER discuss commission rates - always transfer to agent.
```

---

## Tool 4: create_buyer_lead

### Base Configuration

- **Tool Name:** `create_buyer_lead`
- **Request URL:** `https://sally-love-voice-agent.fly.dev/functions/create_buyer_lead`
- **Request HTTP Method:** `POST`

### Request Body

Click **"+ Add Property"** and add the following properties:

| Property Name | Type | Required | Description |
|---------------|------|----------|-------------|
| `first_name` | string | **Yes** | Buyer's first name |
| `last_name` | string | **Yes** | Buyer's last name |
| `phone` | string | **Yes** | Phone number (will be validated and formatted) |
| `email` | string | No | Email address |
| `property_type` | string | No | Preferred property type (single-family, condo, townhouse, land) |
| `location_preference` | string | No | Preferred location/area (e.g., "Ocala", "Dunnellon", "Silver Springs") |
| `min_price` | number | No | Minimum budget |
| `max_price` | number | No | Maximum budget |
| `bedrooms` | integer | No | Desired number of bedrooms |
| `bathrooms` | number | No | Desired number of bathrooms |
| `timeframe` | string | No | When they want to buy ("ASAP", "1-3 months", "3-6 months", "6+ months") |
| `pre_approved` | boolean | No | Whether they are pre-approved for a mortgage |
| `notes` | string | No | Additional notes or special requirements |

### Response Body

Click **"+ Add Property"** and extract:

| Variable | Type | Required | JSON Path | Description |
|----------|------|----------|-----------|-------------|
| `success` | boolean | Yes | `$.success` | Whether lead was created |
| `message` | string | Yes | `$.message` | Confirmation message for buyer |
| `contact_id` | string | No | `$.data.contact_id` | Created contact ID in BoldTrail |

### Description

```
Create a buyer lead in BoldTrail CRM. Collect contact information, property preferences, budget, timeline, and pre-approval status. Always get phone number and at least basic preferences before creating the lead.
```

---

## Tool 5: create_seller_lead

### Base Configuration

- **Tool Name:** `create_seller_lead`
- **Request URL:** `https://sally-love-voice-agent.fly.dev/functions/create_seller_lead`
- **Request HTTP Method:** `POST`

### Request Body

Click **"+ Add Property"** and add the following properties:

| Property Name | Type | Required | Description |
|---------------|------|----------|-------------|
| `first_name` | string | **Yes** | Seller's first name |
| `last_name` | string | **Yes** | Seller's last name |
| `phone` | string | **Yes** | Phone number (will be validated and formatted) |
| `email` | string | No | Email address |
| `property_address` | string | **Yes** | Full property address to be sold |
| `city` | string | **Yes** | City |
| `state` | string | **Yes** | State (default: "FL") |
| `zip_code` | string | **Yes** | ZIP code |
| `property_type` | string | No | Property type (single-family, condo, townhouse, land) |
| `bedrooms` | integer | No | Number of bedrooms |
| `bathrooms` | number | No | Number of bathrooms |
| `square_feet` | integer | No | Property square footage |
| `year_built` | integer | No | Year property was built |
| `reason_for_selling` | string | No | Reason for selling (downsizing, relocating, upgrading, etc.) |
| `timeframe` | string | No | When they want to sell ("ASAP", "1-3 months", "3-6 months", "6+ months") |
| `estimated_value` | number | No | Owner's estimated property value |
| `notes` | string | No | Additional notes about property condition or special circumstances |

### Response Body

Click **"+ Add Property"** and extract:

| Variable | Type | Required | JSON Path | Description |
|----------|------|----------|-----------|-------------|
| `success` | boolean | Yes | `$.success` | Whether lead was created |
| `message` | string | Yes | `$.message` | Confirmation message for seller |
| `contact_id` | string | No | `$.data.contact_id` | Created contact ID in BoldTrail |

### Description

```
Create a seller lead in BoldTrail CRM. Collect contact information, property details, condition, timeline, and selling motivation. NEVER discuss commission rates - if asked, transfer to agent immediately.
```

---

## Tool 6: send_notification

### Base Configuration

- **Tool Name:** `send_notification`
- **Request URL:** `https://sally-love-voice-agent.fly.dev/functions/send_notification`
- **Request HTTP Method:** `POST`

### Request Body

Click **"+ Add Property"** and add the following properties:

| Property Name | Type | Required | Description |
|---------------|------|----------|-------------|
| `recipient_phone` | string | **Yes** | Phone number to send SMS to |
| `message` | string | **Yes** | Message content to send |
| `notification_type` | string | No | Type of notification ("sms", "email", "both") - default: "sms" |
| `recipient_email` | string | No | Email address (required if notification_type is "email" or "both") |

### Response Body

Click **"+ Add Property"** and extract:

| Variable | Type | Required | JSON Path | Description |
|----------|------|----------|-----------|-------------|
| `success` | boolean | Yes | `$.success` | Whether notification was sent |
| `message` | string | Yes | `$.message` | Confirmation message |
| `delivery_status` | string | No | `$.data.delivery_status` | Delivery status |

### Description

```
Send SMS or email notifications. Used internally to send confirmations to Sally, Jeff, and customers after creating leads or important events. Do not use this directly unless specifically needed.
```

---

## 🔧 Authorization Configuration

For all tools, you typically don't need special authorization in Vapi if your endpoints are publicly accessible. However, if you're using a server secret:

### Option 1: No Authorization (Public Endpoints)
- Leave Authorization section **collapsed** or set to "None"

### Option 2: Server URL Secret (If Configured)
- **Type:** Bearer Token or Custom Header
- **Header Name:** `Authorization` (if using Bearer)
- **Value:** Your Vapi API key (set in Assistant Settings → Server URL Secret)

---

## 📝 Request Headers (Optional)

You can add custom headers if needed. For most cases, leave this section **collapsed** or empty. The FastAPI endpoints will handle content type automatically.

If you need to add headers:
- Click **"+ Add Header"**
- **Header Name:** `Content-Type`
- **Header Value:** `application/json`

---

## 🎯 Step-by-Step Upload Instructions

### For Each Tool:

1. **Go to Vapi Dashboard** → Your Assistant → Tools/Functions tab
2. **Click "Add Tool"** or "Create Function"
3. **Base Configuration Section:**
   - Enter **Tool Name** (exactly as shown above)
   - Enter **Request URL** (full URL from above)
   - Select **POST** as HTTP Method
4. **Request Body Section:**
   - Click **"+ Add Property"** for each parameter
   - Enter property name, type, required status, and description
   - Mark required fields with checkbox
5. **Response Body Section:**
   - Click **"+ Add Property"** for each variable to extract
   - Enter variable name, type, and JSON path
6. **Add Description:**
   - Copy the description from above into the description field
7. **Save** the tool
8. **Test** with sample data using Vapi's test feature

---

## 🔄 Recommended Upload Order

1. **check_property** - Most commonly used
2. **get_agent_info** - Needed for routing
3. **create_buyer_lead** - Core functionality
4. **create_seller_lead** - Core functionality
5. **route_to_agent** - Escalation
6. **send_notification** - Internal use (optional to expose)

---

## ✅ Validation Checklist

After uploading each tool, verify:

- [ ] Tool name matches exactly (case-sensitive)
- [ ] URL is correct and accessible
- [ ] HTTP method is POST
- [ ] All required parameters are marked as required
- [ ] Response variables have correct JSON paths
- [ ] Description is clear and complete
- [ ] Test call returns expected response

---

## 🧪 Testing in Vapi Dashboard

For each tool, use the **"Test"** button with sample data:

### Test check_property:
```json
{
  "city": "Ocala",
  "state": "FL",
  "min_price": 200000,
  "max_price": 400000,
  "bedrooms": 3
}
```

### Test get_agent_info:
```json
{
  "city": "Ocala"
}
```

### Test create_buyer_lead:
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "phone": "+13525551234",
  "property_type": "single-family",
  "location_preference": "Ocala",
  "min_price": 200000,
  "max_price": 400000
}
```

### Test create_seller_lead:
```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "phone": "+13525559876",
  "property_address": "123 Main St",
  "city": "Ocala",
  "state": "FL",
  "zip_code": "34471"
}
```

### Test route_to_agent:
```json
{
  "agent_id": "1193050",
  "agent_name": "Agent Name",
  "agent_phone": "+13523992010",
  "reason": "property inquiry"
}
```

### Test send_notification:
```json
{
  "recipient_phone": "+13525551234",
  "message": "Test notification from Vapi",
  "notification_type": "sms"
}
```

---

## 🚨 Important Notes

1. **All endpoints use POST method** - Even for queries
2. **Server URL:** Use `https://sally-love-voice-agent.fly.dev` (production) or your local URL for testing
3. **Required fields:** Make sure to mark all required fields in Vapi dashboard
4. **JSON Paths:** Use JSONPath syntax (e.g., `$.success`, `$.data.contact_id`, `$.results[0].id`)
5. **Error Handling:** Vapi will handle errors automatically based on the `success` field in responses
6. **Voice Responses:** The `message` field contains voice-friendly text for the AI to speak

---

## 📊 Response Format (All Tools)

All tools return this standard format:

```json
{
  "success": true,
  "message": "Voice-friendly message for AI to speak",
  "data": {
    // Tool-specific data
  },
  "results": [], // For array responses
  "error": "Error message if failed (optional)"
}
```

---

**Last Updated:** December 14, 2025  
**Production URL:** https://sally-love-voice-agent.fly.dev  
**API Documentation:** https://sally-love-voice-agent.fly.dev/docs

---

## 🎯 Quick Copy-Paste URLs

```
check_property: https://sally-love-voice-agent.fly.dev/functions/check_property
get_agent_info: https://sally-love-voice-agent.fly.dev/functions/get_agent_info
route_to_agent: https://sally-love-voice-agent.fly.dev/functions/route_to_agent
create_buyer_lead: https://sally-love-voice-agent.fly.dev/functions/create_buyer_lead
create_seller_lead: https://sally-love-voice-agent.fly.dev/functions/create_seller_lead
send_notification: https://sally-love-voice-agent.fly.dev/functions/send_notification
```

---

**Status:** ✅ All tools validated and ready for Vapi dashboard upload

