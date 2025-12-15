"""
Test script for route_to_agent function

⚠️ REMOVE THIS FILE BEFORE PRODUCTION ⚠️

This script tests the route_to_agent endpoint using test agent information.
Uses Hammas Ali's contact info as the test transfer destination.

Usage:
    python scripts/test_route_to_agent.py

Test Agent Info:
    Name: Hammas Ali
    Phone: +923035699010
"""

import asyncio
import httpx
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_ENDPOINT = f"{BASE_URL}/functions/test_route_to_agent"

# Test agent information (Hammas Ali - for testing only)
TEST_AGENT_NAME = "Hammas Ali"
TEST_AGENT_PHONE = "+923035699010"
TEST_CALLER_NAME = "Test Caller"
TEST_REASON = "Testing route_to_agent functionality"


async def test_route_to_agent_basic():
    """Test basic route_to_agent with default test agent"""
    print("\n" + "="*80)
    print("TEST 1: Basic Transfer Test (Default Test Agent)")
    print("="*80)
    
    payload = {
        "caller_name": TEST_CALLER_NAME,
        "reason": TEST_REASON
    }
    
    print(f"📞 Testing transfer to: {TEST_AGENT_NAME}")
    print(f"📱 Phone: {TEST_AGENT_PHONE}")
    print(f"👤 Caller: {TEST_CALLER_NAME}")
    print(f"📝 Reason: {TEST_REASON}")
    print(f"\n📍 Endpoint: {TEST_ENDPOINT}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(TEST_ENDPOINT, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            print("\n✅ Response received:")
            print(json.dumps(result, indent=2))
            
            if result.get("success"):
                print("\n✅ TEST PASSED: Transfer request successful")
                print(f"   Agent: {result.get('data', {}).get('agent_name')}")
                print(f"   Phone: {result.get('data', {}).get('agent_phone')}")
            else:
                print("\n❌ TEST FAILED: Transfer request unsuccessful")
                print(f"   Error: {result.get('error')}")
                
            return result.get("success", False)
            
    except httpx.RequestError as e:
        print(f"\n❌ TEST FAILED: Request error - {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        return False


async def test_route_to_agent_custom_agent():
    """Test route_to_agent with custom test agent info"""
    print("\n" + "="*80)
    print("TEST 2: Custom Agent Test")
    print("="*80)
    
    payload = {
        "test_agent_name": "Custom Test Agent",
        "test_agent_phone": "+1234567890",
        "caller_name": "John Doe",
        "reason": "custom test"
    }
    
    print(f"📞 Testing transfer to: {payload['test_agent_name']}")
    print(f"📱 Phone: {payload['test_agent_phone']}")
    print(f"👤 Caller: {payload['caller_name']}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(TEST_ENDPOINT, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            print("\n✅ Response received:")
            print(json.dumps(result, indent=2))
            
            return result.get("success", False)
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        return False


async def test_route_to_agent_with_mock_control_url():
    """Test route_to_agent with mock controlUrl (simulates actual transfer attempt)"""
    print("\n" + "="*80)
    print("TEST 3: Transfer with Mock ControlUrl (Simulated Transfer)")
    print("="*80)
    
    # Note: This will fail because we're using a fake URL, but tests the logic
    payload = {
        "caller_name": TEST_CALLER_NAME,
        "reason": TEST_REASON,
        "mock_control_url": "https://api.vapi.ai/call/test123/control"  # Mock URL
    }
    
    print(f"📞 Testing transfer to: {TEST_AGENT_NAME}")
    print(f"📱 Phone: {TEST_AGENT_PHONE}")
    print(f"🔗 Mock ControlUrl: {payload['mock_control_url']}")
    print("\n⚠️  Note: This will attempt actual HTTP POST to mock URL (will fail, but tests code path)")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(TEST_ENDPOINT, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            print("\n✅ Response received:")
            print(json.dumps(result, indent=2))
            
            print("\n⚠️  Expected: Transfer execution should fail (mock URL doesn't exist)")
            print("✅ Code path tested successfully")
            
            return True  # Code path worked, even if transfer failed
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        return False


async def test_server_health():
    """Check if server is running"""
    print("\n" + "="*80)
    print("Checking Server Health")
    print("="*80)
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            response.raise_for_status()
            print("✅ Server is running")
            return True
    except Exception as e:
        print(f"❌ Server not accessible: {str(e)}")
        print(f"   Make sure server is running: python main.py")
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 ROUTE TO AGENT - TEST SUITE")
    print("="*80)
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 Base URL: {BASE_URL}")
    print("\n⚠️  REMINDER: This uses TEST endpoint with test agent (Hammas Ali)")
    print("⚠️  REMOVE test_route_to_agent endpoint before production!")
    
    # Check server health
    if not await test_server_health():
        print("\n❌ Server not running. Please start the server first:")
        print("   python main.py")
        return
    
    # Run tests
    results = {
        "Basic Transfer": await test_route_to_agent_basic(),
        "Custom Agent": await test_route_to_agent_custom_agent(),
        "Mock ControlUrl": await test_route_to_agent_with_mock_control_url(),
    }
    
    # Summary
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:25} {status}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print("="*80)
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n✅ All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check output above for details.")
    
    print("\n" + "="*80)
    print("⚠️  REMEMBER:")
    print("1. Remove test_route_to_agent endpoint from route_to_agent.py before production")
    print("2. Remove this test script before production")
    print("3. Test agent info (Hammas Ali) is for testing only")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

