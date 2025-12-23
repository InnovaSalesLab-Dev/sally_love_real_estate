"""
Create Vapi Transfer Tool via API with async: true
This ensures the tool sends the full webhook payload with controlUrl
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

VAPI_API_KEY = os.getenv('VAPI_API_KEY')
WEBHOOK_URL = "https://sally-love-voice-agent.fly.dev/functions/route_to_agent"

def create_transfer_tool():
    """
    Create the route_to_agent tool with async: true via Vapi API
    This is REQUIRED to receive controlUrl in the webhook payload
    """
    url = "https://api.vapi.ai/tool"
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }

    tool_config = {
        "type": "function",
        "async": True,  # ← CRITICAL: This enables controlUrl
        "function": {
            "name": "route_to_agent",
            "description": "Transfer the call to a specific real estate agent based on property listing or customer request. Use this when the caller wants to speak with an agent, has a property inquiry, or needs specialist assistance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Reason for the transfer (e.g., 'property inquiry', 'general inquiry')"
                    },
                    "lead_id": {
                        "type": "string",
                        "description": "CRM contact/lead id returned by create_buyer_lead or create_seller_lead (use data.contact_id)"
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "The BoldTrail CRM ID of the agent"
                    },
                    "agent_name": {
                        "type": "string",
                        "description": "The full name of the agent to transfer to"
                    },
                    "agent_phone": {
                        "type": "string",
                        "description": "The phone number of the agent in E.164 format (e.g., +13523992010)"
                    },
                    "caller_name": {
                        "type": "string",
                        "description": "The name of the caller requesting the transfer"
                    },
                    "caller_phone": {
                        "type": "string",
                        "description": "The caller's phone number (E.164 preferred). Must be collected before transfer."
                    }
                },
                "required": ["agent_phone", "agent_name", "lead_id", "caller_name", "caller_phone"]
            }
        },
        "server": {
            "url": WEBHOOK_URL
        }
    }

    print(f"Creating tool with async: True at {WEBHOOK_URL}...")
    response = requests.post(url, headers=headers, json=tool_config)
    
    if response.status_code in [200, 201]:
        tool = response.json()
        print(f"\n✅ SUCCESS! Tool created with ID: {tool['id']}")
        print(f"\n📋 Tool Details:")
        print(f"   Name: {tool['function']['name']}")
        print(f"   Async: {tool.get('async', False)}")
        print(f"   URL: {tool['server']['url']}")
        print(f"\n🎯 Next Steps:")
        print(f"   1. Copy this Tool ID: {tool['id']}")
        print(f"   2. Go to Vapi Dashboard → Assistants")
        print(f"   3. Edit your assistant")
        print(f"   4. REMOVE the old 'route_to_agent' tool")
        print(f"   5. ADD this new tool by ID: {tool['id']}")
        print(f"   6. Save the assistant")
        print(f"\n⚠️  IMPORTANT: Delete the old tool from the dashboard to avoid conflicts!")
        return tool
    else:
        print(f"\n❌ ERROR: Failed to create tool")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return None


if __name__ == "__main__":
    if not VAPI_API_KEY:
        print("❌ ERROR: VAPI_API_KEY not found in environment variables")
        print("Make sure .env file has VAPI_API_KEY set")
    else:
        create_transfer_tool()

