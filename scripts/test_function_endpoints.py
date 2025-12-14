"""
Script to test all function endpoints via HTTP requests
Tests the actual FastAPI endpoints as they would be called from Vapi
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from src.config.settings import settings
from src.utils.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)

# Base URL for function endpoints
BASE_URL = settings.WEBHOOK_BASE_URL or "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def print_result(test_name: str, success: bool, details: str = "", response: Dict = None):
    """Print formatted test result"""
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"\n{status} - {test_name}")
    if details:
        print(f"   {details}")
    if response and success:
        if isinstance(response, dict):
            # Print key response fields
            if "success" in response:
                print(f"   Success: {response.get('success')}")
            if "message" in response:
                msg = response.get('message', '')[:100]
                print(f"   Message: {msg}...")
            if "data" in response:
                data = response.get('data', {})
                if isinstance(data, dict):
                    if "contact_id" in data:
                        print(f"   Contact ID: {data.get('contact_id')}")
                    if "count" in data:
                        print(f"   Count: {data.get('count')}")


async def test_check_property_endpoint():
    """Test check_property endpoint"""
    print_section("1. Testing /functions/check_property")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Search by city
        print("\n📋 Test 1.1: Search by city")
        payload = {
            "city": "Ocala",
            "state": "FL",
            "min_price": 200000,
            "max_price": 400000
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/functions/check_property",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            print_result("Search by city", data.get("success", False), 
                        f"Status: {response.status_code}", data)
        except Exception as e:
            print_result("Search by city", False, f"Error: {str(e)}")
            return False
        
        # Test 2: Search by bedrooms
        print("\n📋 Test 1.2: Search by bedrooms")
        payload = {
            "bedrooms": 3,
            "bathrooms": 2,
            "state": "FL"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/functions/check_property",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            print_result("Search by bedrooms", data.get("success", False),
                        f"Status: {response.status_code}", data)
            return data.get("success", False)
        except Exception as e:
            print_result("Search by bedrooms", False, f"Error: {str(e)}")
            return False


async def test_get_agent_info_endpoint():
    """Test get_agent_info endpoint"""
    print_section("2. Testing /functions/get_agent_info")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Get all agents
        print("\n📋 Test 2.1: Get all agents")
        payload = {}
        
        try:
            response = await client.post(
                f"{BASE_URL}/functions/get_agent_info",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            print_result("Get all agents", data.get("success", False),
                        f"Status: {response.status_code}", data)
        except Exception as e:
            print_result("Get all agents", False, f"Error: {str(e)}")
            return False
        
        # Test 2: Search by name (if we got agent data)
        if data.get("success") and data.get("results"):
            agents = data.get("results", [])
            if agents and agents[0].get("firstName"):
                print("\n📋 Test 2.2: Search by agent name")
                payload = {
                    "agent_name": agents[0].get("firstName")
                }
                
                try:
                    response = await client.post(
                        f"{BASE_URL}/functions/get_agent_info",
                        json=payload
                    )
                    response.raise_for_status()
                    data = response.json()
                    print_result("Search by name", data.get("success", False),
                                f"Status: {response.status_code}", data)
                except Exception as e:
                    print_result("Search by name", False, f"Error: {str(e)}")
        
        # Test 3: Search by city
        print("\n📋 Test 2.3: Search by city")
        payload = {
            "city": "Ocala"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/functions/get_agent_info",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            print_result("Search by city", data.get("success", False),
                        f"Status: {response.status_code}", data)
            return data.get("success", False)
        except Exception as e:
            print_result("Search by city", False, f"Error: {str(e)}")
            return False


async def test_create_buyer_lead_endpoint():
    """Test create_buyer_lead endpoint"""
    print_section("3. Testing /functions/create_buyer_lead")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n📋 Test 3.1: Create buyer lead")
        payload = {
            "first_name": "Test",
            "last_name": "Buyer",
            "phone": "+13525559999",
            "email": "test.buyer@example.com",
            "property_type": "single-family",
            "location_preference": "Ocala",
            "min_price": 200000,
            "max_price": 400000,
            "bedrooms": 3,
            "bathrooms": 2,
            "timeframe": "1-3 months",
            "pre_approved": True
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/functions/create_buyer_lead",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            print_result("Create buyer lead", data.get("success", False),
                        f"Status: {response.status_code}", data)
            return data.get("success", False)
        except Exception as e:
            print_result("Create buyer lead", False, f"Error: {str(e)}")
            logger.exception(f"create_buyer_lead endpoint test failed: {str(e)}")
            return False


async def test_create_seller_lead_endpoint():
    """Test create_seller_lead endpoint"""
    print_section("4. Testing /functions/create_seller_lead")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n📋 Test 4.1: Create seller lead")
        payload = {
            "first_name": "Test",
            "last_name": "Seller",
            "phone": "+13525558888",
            "email": "test.seller@example.com",
            "property_address": "123 Test Street",
            "city": "Ocala",
            "state": "FL",
            "zip_code": "34471",
            "property_type": "single-family",
            "bedrooms": 3,
            "bathrooms": 2,
            "square_feet": 1800,
            "year_built": 2005,
            "reason_for_selling": "Relocation",
            "timeframe": "ASAP",
            "estimated_value": 350000
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/functions/create_seller_lead",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            print_result("Create seller lead", data.get("success", False),
                        f"Status: {response.status_code}", data)
            return data.get("success", False)
        except Exception as e:
            print_result("Create seller lead", False, f"Error: {str(e)}")
            logger.exception(f"create_seller_lead endpoint test failed: {str(e)}")
            return False


async def test_route_to_agent_endpoint():
    """Test route_to_agent endpoint"""
    print_section("5. Testing /functions/route_to_agent")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # First get an agent to test with
        print("\n📋 Test 5.1: Get agent info first")
        agent_response = await client.post(
            f"{BASE_URL}/functions/get_agent_info",
            json={}
        )
        
        agent_data = agent_response.json()
        agents = agent_data.get("results", [])
        
        if not agents:
            print_result("route_to_agent", False, "No agents found to test with")
            return False
        
        test_agent = agents[0]
        agent_id = test_agent.get("id")
        agent_name = f"{test_agent.get('firstName', '')} {test_agent.get('lastName', '')}"
        agent_phone = test_agent.get("phone", "+13523992010")
        
        print(f"   Using agent: {agent_name} (ID: {agent_id})")
        
        # Now test route_to_agent
        print("\n📋 Test 5.2: Route to agent")
        payload = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "agent_phone": agent_phone,
            "caller_name": "Test Caller",
            "reason": "property inquiry"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/functions/route_to_agent",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            print_result("Route to agent", data.get("success", False),
                        f"Status: {response.status_code}", data)
            return data.get("success", False)
        except Exception as e:
            print_result("Route to agent", False, f"Error: {str(e)}")
            logger.exception(f"route_to_agent endpoint test failed: {str(e)}")
            return False


async def test_health_check():
    """Test health check endpoint"""
    print_section("0. Testing Health Check")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            response.raise_for_status()
            data = response.json()
            print_result("Health check", data.get("status") == "healthy",
                        f"Status: {data.get('status')}")
            return data.get("status") == "healthy"
        except Exception as e:
            print_result("Health check", False, f"Error: {str(e)}")
            return False


async def main():
    """Run all endpoint tests"""
    print("\n" + "="*80)
    print("  SALLY LOVE REAL ESTATE - Function Endpoint Tests")
    print("="*80)
    print(f"\nTesting endpoints at: {BASE_URL}")
    print("Note: Make sure the FastAPI server is running!")
    print("   Run: python main.py")
    
    # Test health check first
    health_ok = await test_health_check()
    if not health_ok:
        print("\n❌ Health check failed. Is the server running?")
        print(f"   Expected server at: {BASE_URL}")
        return
    
    results = {
        "check_property": await test_check_property_endpoint(),
        "get_agent_info": await test_get_agent_info_endpoint(),
        "create_buyer_lead": await test_create_buyer_lead_endpoint(),
        "create_seller_lead": await test_create_seller_lead_endpoint(),
        "route_to_agent": await test_route_to_agent_endpoint(),
    }
    
    print_section("TEST RESULTS SUMMARY")
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:25} {status}")
    
    print("="*80)
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} endpoint tests passed")
    
    if passed_count == total_count:
        print("\n✅ All endpoint tests passed! Functions are working correctly.")
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed.")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        logger.exception("Fatal error in endpoint test script")

