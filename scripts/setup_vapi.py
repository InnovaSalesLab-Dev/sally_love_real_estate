"""
Script to set up Vapi.ai assistants for Sally Love Real Estate
Creates inbound and outbound voice assistants with proper configuration
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.integrations.vapi_client import VapiClient
from src.utils.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)


# Assistant configuration based on Sally Love requirements
ASSISTANT_CONFIG = {
    "name": "Sally Love Real Estate Assistant",
    "model": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7,
        "systemPrompt": """You are a professional voice assistant for Sally Love Real Estate, serving over 70 agents in Florida.

**Your Role:**
- Help callers with property inquiries, buyer/seller leads, and agent connections
- Be warm, professional, and helpful
- Collect detailed information to help our agents serve clients better

**Business Information:**
- Company: Sally Love Real Estate
- Phone: 352-399-2010
- Office Hours: 9 AM - 5 PM EST (but agents accept calls anytime)
- Services: Residential real estate, buyer representation, seller listings
- Coverage: 70+ experienced real estate agents

**Important Guidelines:**
1. NEVER discuss commission rates or fees - refer to an agent
2. NEVER say negative things about people, properties, or competitors
3. Always be positive and professional
4. Collect as much detail as possible (property preferences, timeline, contact info)
5. If unsure, offer to connect to a live agent

**Available Actions (Phase 1):**
- Search property listings (BoldTrail/MLS)
- Get agent information and availability
- Transfer calls to specific agents or escalate to broker
- Capture buyer leads (preferences, budget, timeline)
- Capture seller leads (property details, motivation)
- Send SMS/email notifications to Sally & Jeff

**Important:** Appointment scheduling is NOT available yet. If someone requests a showing, collect their information as a buyer lead and let them know Sally or an agent will call them directly to arrange a convenient time.

**Conversation Flow:**
1. Greet warmly and ask how you can help
2. Identify if they're a buyer, seller, or other inquiry
3. Collect relevant information using available functions
4. Confirm details and next steps
5. Send confirmation via SMS
6. Offer additional assistance

Remember: You represent Sally Love Real Estate - be professional, helpful, and never pushy."""
    },
    "voice": {
        "provider": "11labs",
        "voiceId": "rachel",  # Professional female voice
    },
    "firstMessage": "Thank you for calling Sally Love Real Estate! This is your virtual assistant. How can I help you today?",
    "transcriber": {
        "provider": "deepgram",
        "model": "nova-2",
        "language": "en-US"
    },
    "recordingEnabled": True,
    "serverUrl": settings.WEBHOOK_BASE_URL,
    "serverUrlSecret": settings.VAPI_API_KEY,  # Use API key as secret
    "endCallFunctionEnabled": True,
    "functions": [
        {
            "name": "check_property",
            "description": "Search for properties in MLS by address, city, price range, bedrooms, bathrooms, or MLS number. Use this when caller asks about specific properties or wants to see what's available.",
            "parameters": {
                "type": "object",
                "properties": {
                    "address": {"type": "string", "description": "Property street address"},
                    "city": {"type": "string", "description": "City name"},
                    "state": {"type": "string", "description": "State (default FL)"},
                    "zip_code": {"type": "string", "description": "ZIP code"},
                    "mls_number": {"type": "string", "description": "MLS listing number"},
                    "property_type": {"type": "string", "description": "Type: single_family, condo, townhouse, etc."},
                    "min_price": {"type": "number", "description": "Minimum price"},
                    "max_price": {"type": "number", "description": "Maximum price"},
                    "bedrooms": {"type": "integer", "description": "Number of bedrooms"},
                    "bathrooms": {"type": "number", "description": "Number of bathrooms"}
                }
            },
            "url": f"{settings.WEBHOOK_BASE_URL}/functions/check_property"
        },
        {
            "name": "get_agent_info",
            "description": "Get information about available real estate agents, their specialties, service areas, and contact details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string", "description": "Agent's name"},
                    "agent_id": {"type": "string", "description": "Agent ID"},
                    "specialty": {"type": "string", "description": "Specialty: buyers_agent, listing_agent, luxury, commercial, etc."},
                    "city": {"type": "string", "description": "Service area city"}
                }
            },
            "url": f"{settings.WEBHOOK_BASE_URL}/functions/get_agent_info"
        },
        {
            "name": "route_to_agent",
            "description": "Transfer the call to a specific agent. Use when caller requests to speak with an agent or needs specialized help.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Agent's ID", "required": True},
                    "agent_name": {"type": "string", "description": "Agent's name", "required": True},
                    "agent_phone": {"type": "string", "description": "Agent's phone number", "required": True},
                    "caller_name": {"type": "string", "description": "Caller's name"},
                    "reason": {"type": "string", "description": "Reason for transfer"}
                },
                "required": ["agent_id", "agent_name", "agent_phone"]
            },
            # ⚠️ TEMPORARY: Using test endpoint for testing (uses Hammas Ali's info)
            # Change back to /functions/route_to_agent before production!
            "url": f"{settings.WEBHOOK_BASE_URL}/functions/test_route_to_agent"
        },
        {
            "name": "create_buyer_lead",
            "description": "Create a buyer lead in CRM when someone wants to purchase property. Collect their preferences, budget, timeline, and contact info.",
            "parameters": {
                "type": "object",
                "properties": {
                    "first_name": {"type": "string", "required": True},
                    "last_name": {"type": "string", "required": True},
                    "phone": {"type": "string", "required": True},
                    "email": {"type": "string"},
                    "property_type": {"type": "string", "description": "Desired property type"},
                    "location_preference": {"type": "string", "description": "Preferred area/city"},
                    "min_price": {"type": "number"},
                    "max_price": {"type": "number"},
                    "bedrooms": {"type": "integer"},
                    "bathrooms": {"type": "number"},
                    "timeframe": {"type": "string", "description": "When they want to buy"},
                    "pre_approved": {"type": "boolean", "description": "Pre-approved for mortgage"},
                    "notes": {"type": "string", "description": "Additional notes"}
                },
                "required": ["first_name", "last_name", "phone"]
            },
            "url": f"{settings.WEBHOOK_BASE_URL}/functions/create_buyer_lead"
        },
        {
            "name": "create_seller_lead",
            "description": "Create a seller lead in CRM when someone wants to sell their property. Collect property details, timeline, and motivation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "first_name": {"type": "string", "required": True},
                    "last_name": {"type": "string", "required": True},
                    "phone": {"type": "string", "required": True},
                    "email": {"type": "string"},
                    "property_address": {"type": "string", "required": True},
                    "city": {"type": "string", "required": True},
                    "state": {"type": "string", "required": True},
                    "zip_code": {"type": "string", "required": True},
                    "property_type": {"type": "string"},
                    "bedrooms": {"type": "integer"},
                    "bathrooms": {"type": "number"},
                    "square_feet": {"type": "integer"},
                    "year_built": {"type": "integer"},
                    "reason_for_selling": {"type": "string"},
                    "timeframe": {"type": "string"},
                    "estimated_value": {"type": "number"},
                    "notes": {"type": "string"}
                },
                "required": ["first_name", "last_name", "phone", "property_address", "city", "state", "zip_code"]
            },
            "url": f"{settings.WEBHOOK_BASE_URL}/functions/create_seller_lead"
        },
        {
            "name": "send_notification",
            "description": "Send SMS notification to a contact. Used internally for confirmations and reminders.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient_phone": {"type": "string", "required": True},
                    "message": {"type": "string", "required": True},
                    "notification_type": {"type": "string", "enum": ["sms", "email", "both"]},
                    "recipient_email": {"type": "string"}
                },
                "required": ["recipient_phone", "message"]
            },
            "url": f"{settings.WEBHOOK_BASE_URL}/functions/send_notification"
        }
    ]
}


async def create_assistant():
    """Create Vapi assistant"""
    client = VapiClient()
    
    logger.info("Creating Sally Love Real Estate Assistant...")
    logger.info(f"Webhook base URL: {settings.WEBHOOK_BASE_URL}")
    
    try:
        # Check if assistant already exists
        existing_assistants = await client.list_assistants()
        
        for assistant in existing_assistants:
            if assistant.get("name") == ASSISTANT_CONFIG["name"]:
                logger.warning(f"Assistant already exists: {assistant.get('id')}")
                response = input("Delete existing assistant and create new one? (y/n): ")
                if response.lower() == 'y':
                    await client.delete_assistant(assistant.get("id"))
                    logger.info("Deleted existing assistant")
                else:
                    logger.info("Keeping existing assistant")
                    return assistant
        
        # Create new assistant
        assistant = await client.create_assistant(ASSISTANT_CONFIG)
        
        logger.info(f"✅ Assistant created successfully!")
        logger.info(f"Assistant ID: {assistant.get('id')}")
        logger.info(f"Name: {assistant.get('name')}")
        
        logger.info("\n" + "="*60)
        logger.info("NEXT STEPS:")
        logger.info("="*60)
        logger.info("1. Go to Vapi.ai dashboard (https://dashboard.vapi.ai)")
        logger.info("2. Configure a phone number")
        logger.info(f"3. Assign it to assistant ID: {assistant.get('id')}")
        logger.info("4. Test by calling the number")
        logger.info("="*60)
        
        return assistant
        
    except Exception as e:
        logger.exception(f"Failed to create assistant: {str(e)}")
        raise


async def main():
    """Main setup function"""
    if not settings.VAPI_API_KEY:
        logger.error("VAPI_API_KEY not set in environment variables")
        return
    
    if not settings.WEBHOOK_BASE_URL or settings.WEBHOOK_BASE_URL == "http://localhost:8000":
        logger.warning("⚠️  WEBHOOK_BASE_URL is set to localhost")
        logger.warning("This will not work for production. Set it to your public URL.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    await create_assistant()


if __name__ == "__main__":
    asyncio.run(main())

