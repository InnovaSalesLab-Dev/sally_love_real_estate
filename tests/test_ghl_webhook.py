"""
Test script for GHL webhook integration
Tests the form submission webhook that triggers Vapi outbound calls
"""

import asyncio
import httpx
import sys
import os

# Add parent directory to path to import src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import settings

# =============================================================================
# CONFIGURATION
# =============================================================================

# Test against local or production
USE_PRODUCTION = False  # Change to True to test production

if USE_PRODUCTION:
    BASE_URL = "https://sally-love-voice-agent.fly.dev"
else:
    BASE_URL = f"http://{settings.HOST}:{settings.PORT}"

# Test phone number (USE YOUR OWN PHONE FOR REAL TEST)
TEST_PHONE = "+923035699010"  # Replace with your phone number
TEST_NAME = "Hammas Ali"
TEST_EMAIL = "hamsimirza1@gmail.com"

# =============================================================================
# TEST PAYLOAD (Simulates GHL form submission)
# =============================================================================

def get_test_payload():
    """Generate test payload that mimics GHL form submission"""
    return {
        "type": "FormSubmit",
        "locationId": "test_location_123",
        "contactId": "test_contact_456",
        "submittedAt": "2025-12-22T10:30:00Z",
        "contact": {
            "id": "test_contact_456",
            "name": TEST_NAME,
            "email": TEST_EMAIL,
            "phone": TEST_PHONE
        },
        "formData": {
            "name": TEST_NAME,
            "phone": TEST_PHONE,
            "email": TEST_EMAIL,
            "property_interest": "1738 Augustine Drive, The Villages",
            "budget": "$500k-$750k",
            "timeframe": "1-3 months"
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
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL - Error: {str(e)}")
        return False


async def test_ghl_test_endpoint():
    """Test 2: Test the GHL test endpoint"""
    print("\n" + "="*70)
    print("TEST 2: GHL Test Endpoint")
    print("="*70)
    
    url = f"{BASE_URL}/webhooks/ghl/test"
    print(f"Testing: {url}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={"test": "hello"},
                timeout=10.0
            )
        
        if response.status_code == 200:
            print("✅ PASS - Test endpoint responding")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ FAIL - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL - Error: {str(e)}")
        return False


async def test_form_submission_webhook(trigger_real_call=False):
    """Test 3: Test the form submission webhook (triggers Vapi call)"""
    print("\n" + "="*70)
    print("TEST 3: Form Submission Webhook")
    print("="*70)
    
    if not trigger_real_call:
        print("⚠️  SIMULATION MODE - Not triggering real Vapi call")
        print("   Set trigger_real_call=True to make a real call")
        return True
    
    url = f"{BASE_URL}/webhooks/ghl/form-submission"
    print(f"Testing: {url}")
    print(f"Phone number: {TEST_PHONE}")
    print(f"⚠️  YOUR PHONE WILL RING IN 10-15 SECONDS!")
    
    payload = get_test_payload()
    print(f"\nPayload:")
    import json
    print(json.dumps(payload, indent=2))
    
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
            print("✅ PASS - Webhook processed successfully")
            print(f"\nResponse:")
            print(json.dumps(response_data, indent=2))
            
            if "vapi_call_id" in response_data:
                print(f"\n🎉 SUCCESS! Vapi call initiated!")
                print(f"Call ID: {response_data['vapi_call_id']}")
                print(f"\n⏰ Your phone ({TEST_PHONE}) should ring in 10-15 seconds...")
                print("   Answer the call to test the AI agent!")
            
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


async def check_configuration():
    """Check if required configuration is present"""
    print("\n" + "="*70)
    print("CONFIGURATION CHECK")
    print("="*70)
    
    checks_passed = True
    
    # Check VAPI_ASSISTANT_ID
    if settings.VAPI_ASSISTANT_ID:
        print(f"✅ VAPI_ASSISTANT_ID: {settings.VAPI_ASSISTANT_ID[:20]}...")
    else:
        print("❌ VAPI_ASSISTANT_ID: NOT SET")
        print("   Add VAPI_ASSISTANT_ID to your .env file")
        checks_passed = False
    
    # Check VAPI_API_KEY
    if settings.VAPI_API_KEY:
        print(f"✅ VAPI_API_KEY: {settings.VAPI_API_KEY[:10]}...")
    else:
        print("❌ VAPI_API_KEY: NOT SET")
        checks_passed = False
    
    # Check TEST_MODE
    print(f"ℹ️  TEST_MODE: {settings.TEST_MODE}")
    
    # Check base URL
    print(f"ℹ️  Testing against: {BASE_URL}")
    
    return checks_passed

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

async def run_all_tests(trigger_real_call=False):
    """Run all tests"""
    print("="*70)
    print("GHL WEBHOOK TEST SUITE")
    print("="*70)
    print(f"Environment: {'PRODUCTION' if USE_PRODUCTION else 'LOCAL'}")
    print(f"Base URL: {BASE_URL}")
    print(f"Real Call: {'YES - PHONE WILL RING!' if trigger_real_call else 'NO - Simulation only'}")
    print("="*70)
    
    # Check configuration first
    config_ok = await check_configuration()
    if not config_ok:
        print("\n❌ Configuration issues detected. Fix them before testing.")
        return
    
    # Run tests
    results = []
    
    # Test 1: Health check
    results.append(await test_health_check())
    
    # Test 2: Test endpoint
    results.append(await test_ghl_test_endpoint())
    
    # Test 3: Form submission (optional real call)
    results.append(await test_form_submission_webhook(trigger_real_call))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED!")
        if trigger_real_call:
            print("\n⏰ Check your phone - you should receive a call!")
    else:
        print("❌ SOME TESTS FAILED")
    
    print("="*70)

# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test GHL webhook integration")
    parser.add_argument(
        "--real-call",
        action="store_true",
        help="Trigger a real Vapi call (your phone will ring!)"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Test against production instead of local"
    )
    
    args = parser.parse_args()
    
    # Update configuration based on arguments
    if args.production:
        USE_PRODUCTION = True
        BASE_URL = "https://sally-love-voice-agent.fly.dev"
    
    # Warning if real call requested
    if args.real_call:
        print("\n⚠️  WARNING: You are about to trigger a REAL Vapi call!")
        print(f"Phone number: {TEST_PHONE}")
        print(f"Your phone will ring in 10-15 seconds after the test runs.")
        response = input("\nContinue? (yes/no): ")
        if response.lower() != "yes":
            print("Test cancelled.")
            sys.exit(0)
    
    # Run tests
    asyncio.run(run_all_tests(trigger_real_call=args.real_call))

