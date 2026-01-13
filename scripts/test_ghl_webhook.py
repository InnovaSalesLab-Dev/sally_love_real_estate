#!/usr/bin/env python3
"""
Test script to manually trigger the GHL webhook endpoint
"""

import asyncio
import httpx
import json
from datetime import datetime, timezone


async def test_ghl_webhook():
    """Test the GHL form submission webhook"""
    
    webhook_url = "https://sally-love-voice-agent.fly.dev/webhooks/ghl/form-submission"
    phone_number = "+923175379399"
    
    # Simulate GHL form submission payload
    payload = {
        "type": "FormSubmit",
        "locationId": "test_location_123",
        "contactId": "test_contact_456",
        "submittedAt": datetime.now(timezone.utc).isoformat(),
        "contact": {
            "id": "test_contact_456",
            "name": "Test User",
            "email": "test@example.com",
            "phone": phone_number
        },
        "formData": {
            "name": "Test User",
            "phone": phone_number,
            "email": "test@example.com",
            "property_interest": "Test Property Inquiry",
            "budget": "$300k-$400k",
            "timeframe": "1-3 months"
        }
    }
    
    print(f"🚀 Testing GHL webhook endpoint: {webhook_url}")
    print(f"📞 Phone number: {phone_number}")
    print(f"📦 Payload:")
    print(json.dumps(payload, indent=2))
    print("\n" + "="*60 + "\n")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                webhook_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                }
            )
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            print(f"\n📝 Response Body:")
            try:
                response_json = response.json()
                print(json.dumps(response_json, indent=2))
            except:
                print(response.text)
            
            if response.status_code == 200:
                print("\n✅ Webhook triggered successfully!")
                if "vapi_call_id" in response_json:
                    print(f"📞 Vapi call ID: {response_json.get('vapi_call_id')}")
                    print(f"💬 Message: {response_json.get('message')}")
            else:
                print(f"\n❌ Webhook failed with status {response.status_code}")
                
    except httpx.TimeoutException:
        print("❌ Request timed out")
    except httpx.RequestError as e:
        print(f"❌ Request error: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_ghl_webhook())
