#!/usr/bin/env python3
"""
Check Vapi call status
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_API_URL = "https://api.vapi.ai"
CALL_ID = "019bb828-8267-7557-b607-216c1a1b60bf"  # From the webhook test


async def check_call_status():
    """Check the status of a Vapi call"""
    
    if not VAPI_API_KEY:
        print("❌ VAPI_API_KEY not found in environment")
        return
    
    url = f"{VAPI_API_URL}/call/{CALL_ID}"
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json",
    }
    
    print(f"🔍 Checking call status for: {CALL_ID}")
    print(f"🌐 URL: {url}\n")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                call_data = response.json()
                print(f"\n✅ Call Details:")
                print(json.dumps(call_data, indent=2))
                
                # Extract key fields
                status = call_data.get("status")
                customer_number = call_data.get("customer", {}).get("number")
                started_at = call_data.get("startedAt")
                ended_at = call_data.get("endedAt")
                error = call_data.get("error")
                
                print(f"\n📞 Status: {status}")
                print(f"📱 Customer Number: {customer_number}")
                if started_at:
                    print(f"🕐 Started: {started_at}")
                if ended_at:
                    print(f"🕑 Ended: {ended_at}")
                if error:
                    print(f"❌ Error: {error}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
    except Exception as e:
        print(f"❌ Error checking call status: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_call_status())
