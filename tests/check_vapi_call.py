"""
Check the status of a Vapi call
"""

import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.integrations.vapi_client import VapiClient

async def check_call_status(call_id):
    """Check the status of a Vapi call"""
    print("="*70)
    print("VAPI CALL STATUS CHECK")
    print("="*70)
    print(f"Call ID: {call_id}")
    print()
    
    vapi_client = VapiClient()
    
    try:
        call_data = await vapi_client.get_call(call_id)
        
        print("✅ Call found in Vapi!")
        print()
        print("Call Details:")
        print("-" * 70)
        
        # Import json for pretty printing
        import json
        print(json.dumps(call_data, indent=2))
        
        print()
        print("-" * 70)
        
        # Extract key information
        status = call_data.get("status")
        started_at = call_data.get("startedAt")
        ended_at = call_data.get("endedAt")
        customer = call_data.get("customer", {})
        
        print(f"Status: {status}")
        print(f"Customer Number: {customer.get('number')}")
        print(f"Started At: {started_at}")
        print(f"Ended At: {ended_at}")
        
        if "endedReason" in call_data:
            print(f"Ended Reason: {call_data.get('endedReason')}")
        
        if "error" in call_data:
            print(f"❌ Error: {call_data.get('error')}")
        
    except Exception as e:
        print(f"❌ Error checking call: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        call_id = sys.argv[1]
    else:
        # Use the call ID from the last test
        call_id = "019b4685-10eb-733f-90f5-b26ba449f256"
    
    asyncio.run(check_call_status(call_id))

