"""
Test script for Vapi dynamic call transfer functionality
Tests the route_to_agent function and transfer webhook handling
Based on: https://docs.vapi.ai/calls/call-dynamic-transfers
"""

import asyncio
import httpx
import sys
import os
import json
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import settings
from src.integrations.vapi_client import VapiClient

# =============================================================================
# CONFIGURATION
# =============================================================================

# Test against local or production
USE_PRODUCTION = False

if USE_PRODUCTION:
    BASE_URL = "https://sally-love-voice-agent.fly.dev"
else:
    BASE_URL = f"http://{settings.HOST}:{settings.PORT}"

# Test phone numbers
TEST_CALLER_PHONE = "+923175379399"  # Pakistan number that will receive the call
TEST_TRANSFER_TO = "+923035699010"  # Pakistan number where call will transfer (in TEST_MODE)

# =============================================================================
# TEST PAYLOADS
# =============================================================================

def get_route_to_agent_payload(agent_name: str = "Hammas Ali") -> Dict[str, Any]:
    """Generate test payload that mimics Vapi calling route_to_agent function"""
    return {
        "message": {
            "type": "function-call",
            "functionCall": {
                "name": "route_to_agent",
                "parameters": {
                    "agent_name": agent_name,
                    "reason": "property inquiry - buyer interested in 1738 Augustine Drive",
                    "contact_name": "Test User",
                    "contact_phone": TEST_CALLER_PHONE,
                    "contact_email": "test@example.com"
                }
            },
            "call": {
                "id": "test_call_123",
                "orgId": "test_org",
                "createdAt": "2025-12-22T10:00:00Z",
                "updatedAt": "2025-12-22T10:00:00Z",
                "type": "inboundPhoneCall",
                "status": "in-progress",
                "phoneNumberId": settings.VAPI_PHONE_NUMBER_ID,
                "customer": {
                    "number": TEST_CALLER_PHONE
                },
                "monitor": {
                    "listenUrl": "wss://api.vapi.ai/call/test_call_123/listen",
                    "controlUrl": f"{BASE_URL}/vapi/control/test_call_123"
                }
            },
            "toolWithToolCallList": [
                {
                    "type": "function",
                    "function": {
                        "name": "route_to_agent",
                        "description": "Transfer the call to a specific agent",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "agent_name": {"type": "string"},
                                "reason": {"type": "string"},
                                "contact_name": {"type": "string"},
                                "contact_phone": {"type": "string"},
                                "contact_email": {"type": "string"}
                            }
                        }
                    },
                    "toolCall": {
                        "id": "call_test_123",
                        "type": "function",
                        "function": {
                            "name": "route_to_agent",
                            "arguments": {
                                "agent_name": agent_name,
                                "reason": "property inquiry - buyer interested in 1738 Augustine Drive",
                                "contact_name": "Test User",
                                "contact_phone": TEST_CALLER_PHONE,
                                "contact_email": "test@example.com"
                            }
                        }
                    }
                }
            ]
        }
    }

# =============================================================================
# TEST FUNCTIONS
# =============================================================================

async def test_health_check():
    """Test 1: Check if the app is running"""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    url = f"{BASE_URL}/health"
    print(f"Testing: {url}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            
        if response.status_code == 200:
            print("✅ PASS - App is running")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ FAIL - Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL - Error: {str(e)}")
        return False


async def test_route_to_agent_endpoint():
    """Test 2: Test the route_to_agent function endpoint"""
    print("\n" + "="*70)
    print("TEST 2: Route to Agent Endpoint")
    print("="*70)
    
    url = f"{BASE_URL}/functions/route_to_agent"
    print(f"Testing: {url}")
    
    payload = get_route_to_agent_payload()
    print(f"\nPayload:")
    print(json.dumps(payload["message"]["functionCall"]["parameters"], indent=2))
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                timeout=30.0
            )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("✅ PASS - Route to agent endpoint responding")
            print(f"\nResponse:")
            print(json.dumps(response_data, indent=2))
            return True
        else:
            print(f"❌ FAIL - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL - Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_lookup():
    """Test 3: Test agent lookup functionality"""
    print("\n" + "="*70)
    print("TEST 3: Agent Lookup")
    print("="*70)
    
    # Test with different agent names
    test_agents = [
        "Hammas Ali",  # Test agent
        "Sally Love",  # Owner
        "Jeff Beatty",  # Broker
        "Unknown Agent"  # Should fallback
    ]
    
    results = []
    
    for agent_name in test_agents:
        print(f"\nTesting agent: {agent_name}")
        payload = get_route_to_agent_payload(agent_name)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BASE_URL}/functions/route_to_agent",
                    json=payload,
                    timeout=30.0
                )
            
            if response.status_code == 200:
                data = response.json()
                destination = data.get("destination", {})
                dest_number = destination.get("number", "N/A")
                message = destination.get("message", "N/A")
                
                print(f"  ✅ Success")
                print(f"  📞 Destination: {dest_number}")
                print(f"  💬 Message: {message}")
                results.append(True)
            else:
                print(f"  ❌ Failed - Status: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n{'='*70}")
    print(f"Agent Lookup Results: {passed}/{total} passed")
    print(f"{'='*70}")
    
    return passed == total


async def test_transfer_with_real_call(make_real_call: bool = False):
    """Test 4: Test with real Vapi call (optional)"""
    print("\n" + "="*70)
    print("TEST 4: Real Call Transfer Test")
    print("="*70)
    
    if not make_real_call:
        print("⚠️  SIMULATION MODE - Not making real call")
        print("   Set make_real_call=True to test with actual Vapi call")
        return True
    
    print(f"⚠️  REAL CALL MODE - Will call {TEST_CALLER_PHONE}")
    print(f"📞 {TEST_CALLER_PHONE} will ring!")
    print(f"🎤 When you answer, say: 'I want to speak with an agent'")
    print(f"🔄 TEST_MODE is ON - call will transfer to: {TEST_TRANSFER_TO}")
    
    if not settings.VAPI_ASSISTANT_ID:
        print("❌ VAPI_ASSISTANT_ID not configured")
        return False
    
    try:
        vapi_client = VapiClient()
        
        print(f"\nInitiating outbound call...")
        call_response = await vapi_client.create_outbound_call(
            phone_number=TEST_CALLER_PHONE,
            assistant_id=settings.VAPI_ASSISTANT_ID,
            customer_name="Test User",
            metadata={
                "test_type": "transfer_test",
                "expected_transfer_to": TEST_TRANSFER_TO
            }
        )
        
        call_id = call_response.get("id")
        print(f"✅ Call initiated successfully!")
        print(f"📞 Call ID: {call_id}")
        print(f"\n🎯 Instructions:")
        print(f"   1. Answer the call on {TEST_CALLER_PHONE}")
        print(f"   2. Wait for AI greeting: 'Thank you for calling Sally Love Real Estate...'")
        print(f"   3. Say: 'I want to speak with an agent' or 'Transfer me to an agent'")
        print(f"   4. Provide your info when asked:")
        print(f"      - Name")
        print(f"      - Phone number")
        print(f"      - Email")
        print(f"   5. AI will say: 'I'm connecting you now'")
        print(f"   6. Call will transfer to {TEST_TRANSFER_TO} (TEST_MODE)")
        print(f"   7. {TEST_TRANSFER_TO} should ring!")
        print(f"\n⏰ Initial call should connect in 5-10 seconds...")
        print(f"   After transfer request, {TEST_TRANSFER_TO} rings in ~3-5 seconds")
        
        # Wait a bit for call to establish
        await asyncio.sleep(10)
        
        # Check call status
        call_status = await vapi_client.get_call(call_id)
        status = call_status.get("status")
        
        print(f"\n📊 Call Status: {status}")
        
        if status in ["in-progress", "ended"]:
            print("✅ PASS - Call executed")
            return True
        else:
            print(f"⚠️  Call status: {status}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL - Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def check_configuration():
    """Check if required configuration is present"""
    print("\n" + "="*70)
    print("CONFIGURATION CHECK")
    print("="*70)
    
    checks = []
    
    # Check VAPI_ASSISTANT_ID
    if settings.VAPI_ASSISTANT_ID:
        print(f"✅ VAPI_ASSISTANT_ID: {settings.VAPI_ASSISTANT_ID[:20]}...")
        checks.append(True)
    else:
        print("⚠️  VAPI_ASSISTANT_ID: Not set (required for real call test)")
        checks.append(False)
    
    # Check VAPI_PHONE_NUMBER_ID
    if settings.VAPI_PHONE_NUMBER_ID:
        print(f"✅ VAPI_PHONE_NUMBER_ID: {settings.VAPI_PHONE_NUMBER_ID[:20]}...")
        checks.append(True)
    else:
        print("⚠️  VAPI_PHONE_NUMBER_ID: Not set (required for outbound calls)")
        checks.append(False)
    
    # Check TEST_MODE
    print(f"ℹ️  TEST_MODE: {settings.TEST_MODE}")
    if settings.TEST_MODE:
        print(f"ℹ️  TEST_AGENT_PHONE: {settings.TEST_AGENT_PHONE}")
    
    # Check base URL
    print(f"ℹ️  Testing against: {BASE_URL}")
    
    return all(checks)

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

async def run_all_tests(make_real_call: bool = False):
    """Run all tests"""
    print("="*70)
    print("CALL TRANSFER TEST SUITE")
    print("="*70)
    print(f"Environment: {'PRODUCTION' if USE_PRODUCTION else 'LOCAL'}")
    print(f"Base URL: {BASE_URL}")
    print(f"Real Call: {'YES - PHONE WILL RING!' if make_real_call else 'NO - Simulation only'}")
    print(f"Test Mode: {settings.TEST_MODE}")
    print("="*70)
    
    # Check configuration
    config_ok = await check_configuration()
    if not config_ok and make_real_call:
        print("\n❌ Configuration incomplete for real call test")
        print("   Set make_real_call=False to test endpoints only")
        return
    
    # Run tests
    results = []
    
    # Test 1: Health check
    results.append(await test_health_check())
    
    # Test 2: Route to agent endpoint
    results.append(await test_route_to_agent_endpoint())
    
    # Test 3: Agent lookup
    results.append(await test_agent_lookup())
    
    # Test 4: Real call (optional)
    if make_real_call:
        results.append(await test_transfer_with_real_call(make_real_call))
    else:
        print("\n" + "="*70)
        print("TEST 4: Real Call Transfer Test")
        print("="*70)
        print("⚠️  SKIPPED - Use --real-call to test with actual Vapi call")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED!")
        if not make_real_call:
            print("\n💡 To test with real call:")
            print("   python3 tests/test_call_transfer.py --real-call")
    else:
        print("❌ SOME TESTS FAILED")
    
    print("="*70)

# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Vapi call transfer functionality")
    parser.add_argument(
        "--real-call",
        action="store_true",
        help="Make a real Vapi call to test transfer (your phone will ring!)"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Test against production instead of local"
    )
    
    args = parser.parse_args()
    
    # Update configuration
    if args.production:
        USE_PRODUCTION = True
        BASE_URL = "https://sally-love-voice-agent.fly.dev"
    
    # Warning if real call requested
    if args.real_call:
        print("\n⚠️  WARNING: You are about to make a REAL Vapi call!")
        print(f"📞 Vapi will call: {TEST_CALLER_PHONE} (US number)")
        print(f"   Answer and say: 'I want to speak with an agent'")
        print(f"🔄 Transfer will go to: {TEST_TRANSFER_TO} (Pakistan - TEST_MODE)")
        print(f"💰 This will use your Vapi credits!")
        print(f"\n📋 Flow:")
        print(f"   1. {TEST_CALLER_PHONE} rings → You answer")
        print(f"   2. You talk to AI → Request transfer")
        print(f"   3. {TEST_TRANSFER_TO} rings → Transfer successful!")
        
        # Auto-confirm in non-interactive environments
        if not sys.stdin.isatty():
            print("\nContinue? (yes/no): yes (auto-confirmed in non-interactive mode)")
        else:
            response = input("\nContinue? (yes/no): ")
            if response.lower() != "yes":
                print("Test cancelled.")
                sys.exit(0)
    
    # Run tests
    asyncio.run(run_all_tests(make_real_call=args.real_call))

