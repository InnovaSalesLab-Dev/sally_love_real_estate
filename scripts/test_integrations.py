"""
Script to test integrations (BoldTrail, Stellar MLS, Twilio, Vapi)
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.integrations.vapi_client import VapiClient
from src.integrations.boldtrail import BoldTrailClient
from src.integrations.stellar_mls import StellarMLSClient
from src.integrations.twilio_client import TwilioClient
from src.utils.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)


async def test_vapi():
    """Test Vapi.ai connection"""
    logger.info("\n" + "="*60)
    logger.info("Testing Vapi.ai Integration")
    logger.info("="*60)
    
    if not settings.VAPI_API_KEY:
        logger.error("❌ VAPI_API_KEY not set")
        return False
    
    try:
        client = VapiClient()
        assistants = await client.list_assistants()
        logger.info(f"✅ Vapi connection successful! Found {len(assistants)} assistants")
        return True
    except Exception as e:
        logger.error(f"❌ Vapi connection failed: {str(e)}")
        return False


async def test_boldtrail():
    """Test BoldTrail CRM connection"""
    logger.info("\n" + "="*60)
    logger.info("Testing BoldTrail CRM Integration")
    logger.info("="*60)
    
    if not settings.BOLDTRAIL_API_KEY:
        logger.error("❌ BOLDTRAIL_API_KEY not set")
        return False
    
    try:
        client = BoldTrailClient()
        # Try to get agents (this is a read-only operation)
        agents = await client.get_agents()
        logger.info(f"✅ BoldTrail connection successful! Found {len(agents)} agents")
        return True
    except Exception as e:
        logger.error(f"❌ BoldTrail connection failed: {str(e)}")
        logger.info("Note: This might be expected if API credentials aren't configured yet")
        return False


async def test_stellar_mls():
    """Test Stellar MLS connection"""
    logger.info("\n" + "="*60)
    logger.info("Testing Stellar MLS Integration")
    logger.info("="*60)
    
    if not settings.STELLAR_MLS_USERNAME or not settings.STELLAR_MLS_PASSWORD:
        logger.error("❌ Stellar MLS credentials not set")
        return False
    
    try:
        client = StellarMLSClient()
        # Test authentication
        token = await client._authenticate()
        logger.info(f"✅ Stellar MLS authentication successful!")
        return True
    except Exception as e:
        logger.error(f"❌ Stellar MLS connection failed: {str(e)}")
        logger.info("Note: This might be expected if MLS credentials aren't configured yet")
        return False


async def test_twilio():
    """Test Twilio connection"""
    logger.info("\n" + "="*60)
    logger.info("Testing Twilio Integration")
    logger.info("="*60)
    
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.error("❌ Twilio credentials not set")
        return False
    
    try:
        client = TwilioClient()
        # Just check if client initializes
        logger.info(f"✅ Twilio client initialized successfully!")
        logger.info(f"   Account SID: {settings.TWILIO_ACCOUNT_SID[:10]}...")
        logger.info(f"   Phone Number: {settings.TWILIO_PHONE_NUMBER}")
        return True
    except Exception as e:
        logger.error(f"❌ Twilio initialization failed: {str(e)}")
        return False


async def main():
    """Run all integration tests"""
    logger.info("\n" + "="*80)
    logger.info("SALLY LOVE REAL ESTATE - Integration Tests")
    logger.info("="*80)
    
    results = {
        "Vapi.ai": await test_vapi(),
        "BoldTrail CRM": await test_boldtrail(),
        "Stellar MLS": await test_stellar_mls(),
        "Twilio": await test_twilio(),
    }
    
    logger.info("\n" + "="*80)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*80)
    
    for service, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{service:20} {status}")
    
    logger.info("="*80)
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    logger.info(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        logger.info("\n✅ All integrations are working correctly!")
    else:
        logger.warning("\n⚠️  Some integrations failed. Please check credentials in .env file.")


if __name__ == "__main__":
    asyncio.run(main())

