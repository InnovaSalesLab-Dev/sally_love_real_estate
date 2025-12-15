"""
Test SMS functionality via Twilio
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.integrations.twilio_client import TwilioClient
from src.utils.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)


async def test_sms():
    """Test sending SMS via Twilio"""
    logger.info("\n" + "="*60)
    logger.info("Testing SMS Functionality")
    logger.info("="*60)
    
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.error("❌ Twilio credentials not set in .env")
        return False
    
    if not settings.TWILIO_PHONE_NUMBER:
        logger.error("❌ TWILIO_PHONE_NUMBER not set in .env")
        return False
    
    # Test phone number
    # For US numbers, use format: +1XXXXXXXXXX
    # For international, you need to enable Geo Permissions in Twilio Console
    test_phone = "+923035699010"  # Pakistan - requires Geo Permissions enabled
    # test_phone = "+12345678900"  # US number - uncomment and replace for testing
    test_message = "Test SMS from Sally Love Voice Agent - If you receive this, SMS is working! 🎉"
    
    logger.info(f"Twilio Phone Number: {settings.TWILIO_PHONE_NUMBER}")
    logger.info(f"Test Recipient: {test_phone}")
    logger.info(f"Message: {test_message}")
    logger.info("")
    
    try:
        client = TwilioClient()
        logger.info("Sending SMS...")
        
        result = await client.send_sms(
            to_number=test_phone,
            message=test_message
        )
        
        logger.info("✅ SMS sent successfully!")
        logger.info(f"   Message SID: {result.get('sid')}")
        logger.info(f"   Status: {result.get('status')}")
        logger.info(f"   To: {result.get('to')}")
        logger.info(f"   From: {result.get('from')}")
        logger.info("")
        logger.info("📱 Check your phone - you should receive the SMS shortly!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ SMS sending failed: {str(e)}")
        logger.error(f"   Error type: {type(e).__name__}")
        import traceback
        logger.error(f"   Traceback:\n{traceback.format_exc()}")
        return False


if __name__ == "__main__":
    asyncio.run(test_sms())

