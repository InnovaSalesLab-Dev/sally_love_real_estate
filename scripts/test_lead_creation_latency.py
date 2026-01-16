#!/usr/bin/env python3
"""
Test latency of lead creation endpoints
"""

import asyncio
import httpx
import json
import time
from datetime import datetime

BASE_URL = "https://sally-love-voice-agent.fly.dev"

async def test_buyer_lead_latency():
    """Test create_buyer_lead endpoint latency"""
    
    payload = {
        "first_name": "Test",
        "last_name": "Buyer",
        "phone": "+13525551234",
        "email": "testbuyer@example.com",
        "property_type": "Villa",
        "location_preference": "The Villages",
        "min_price": 200000,
        "max_price": 400000,
        "bedrooms": 2,
        "bathrooms": 2,
        "timeframe": "1-3 months",
        "special_requirements": "Golf cart garage"
    }
    
    print("="*80)
    print("TESTING create_buyer_lead ENDPOINT LATENCY")
    print("="*80)
    print()
    print(f"URL: {BASE_URL}/functions/create_buyer_lead")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    print("Running test...")
    print()
    
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BASE_URL}/functions/create_buyer_lead",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"⏱️  Total Latency: {latency_ms:,.2f}ms ({latency_ms/1000:.2f}s)")
            print()
            
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    print(f"✅ Response:")
                    print(json.dumps(response_json, indent=2))
                    if response_json.get("success"):
                        print()
                        print(f"✅ Success! Contact ID: {response_json.get('data', {}).get('contact_id')}")
                except:
                    print(f"Response text: {response.text[:500]}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                
    except Exception as e:
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        print(f"❌ Request failed after {latency_ms:,.2f}ms")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_seller_lead_latency():
    """Test create_seller_lead endpoint latency"""
    
    payload = {
        "first_name": "Test",
        "last_name": "Seller",
        "phone": "+13525555678",
        "email": "testseller@example.com",
        "property_address": "123 Test Street",
        "city": "The Villages",
        "state": "FL",
        "zip_code": "32163",
        "property_type": "Villa",
        "bedrooms": 2,
        "bathrooms": 2,
        "timeframe": "1-3 months",
        "reason_for_selling": "Relocating"
    }
    
    print()
    print("="*80)
    print("TESTING create_seller_lead ENDPOINT LATENCY")
    print("="*80)
    print()
    print(f"URL: {BASE_URL}/functions/create_seller_lead")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    print("Running test...")
    print()
    
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BASE_URL}/functions/create_seller_lead",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"⏱️  Total Latency: {latency_ms:,.2f}ms ({latency_ms/1000:.2f}s)")
            print()
            
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    print(f"✅ Response:")
                    print(json.dumps(response_json, indent=2))
                    if response_json.get("success"):
                        print()
                        print(f"✅ Success! Contact ID: {response_json.get('data', {}).get('contact_id')}")
                except:
                    print(f"Response text: {response.text[:500]}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                
    except Exception as e:
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        print(f"❌ Request failed after {latency_ms:,.2f}ms")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all latency tests"""
    print("🚀 LEAD CREATION LATENCY VALIDATION")
    print("="*80)
    print()
    
    # Test buyer lead
    await test_buyer_lead_latency()
    
    # Small delay between tests
    await asyncio.sleep(2)
    
    # Test seller lead
    await test_seller_lead_latency()
    
    print()
    print("="*80)
    print("VALIDATION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
