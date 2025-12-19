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
        logger.error("   Add TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN to your .env file")
        return False
    
    if not settings.TWILIO_PHONE_NUMBER:
        logger.error("❌ TWILIO_PHONE_NUMBER not set in .env")
        return False
    
    # Test phone number - you can change this or pass as command line argument
    # For US numbers, use format: +1XXXXXXXXXX
    # For international, you need to enable Geo Permissions in Twilio Console
    # Default: Use TEST_AGENT_PHONE from settings (Hammas Ali's number)
    test_phone = settings.TEST_AGENT_PHONE if settings.TEST_AGENT_PHONE else "+923035699010"
    
    # Allow override via command line argument
    if len(sys.argv) > 1:
        test_phone = sys.argv[1]
        logger.info(f"Using phone number from command line: {test_phone}")
    
    test_message = "Test SMS from Sally Love Voice Agent - If you receive this, SMS is working! 🎉"
    
    logger.info(f"Configuration:")
    logger.info(f"  Twilio Phone Number: {settings.TWILIO_PHONE_NUMBER}")
    logger.info(f"  Test Recipient: {test_phone}")
    logger.info(f"  Message: {test_message}")
    logger.info("")
    
    # Validate phone format
    if not test_phone.startswith('+'):
        logger.error(f"❌ Phone number must be in E.164 format (start with +)")
        logger.error(f"   Example: +1234567890 (US), +923035699010 (Pakistan)")
        return False
    
    try:
        client = TwilioClient()
        logger.info("✅ Twilio client initialized successfully")
        logger.info(f"   Account SID: {settings.TWILIO_ACCOUNT_SID[:10]}...")
        logger.info("")
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
        logger.info("")
        logger.info("NOTE: If you don't receive the SMS:")
        logger.info("  1. Check Twilio Console > Geo Permissions (for international numbers)")
        logger.info("  2. Verify the phone number is correct and active")
        logger.info("  3. Check Twilio Console > Logs for delivery status")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ SMS sending failed: {str(e)}")
        logger.error(f"   Error type: {type(e).__name__}")
        
        # Provide helpful troubleshooting tips based on error
        error_str = str(e).lower()
        if "permission" in error_str or "geo" in error_str:
            logger.error("")
            logger.error("🔧 TROUBLESHOOTING:")
            logger.error("   This looks like a Geo Permissions issue.")
            logger.error("   Solution:")
            logger.error("   1. Go to: https://console.twilio.com/us1/develop/sms/settings/geo-permissions")
            logger.error(f"   2. Enable SMS for the target country (Pakistan for {test_phone})")
            logger.error("   3. Save and try again")
        elif "authenticate" in error_str or "credentials" in error_str:
            logger.error("")
            logger.error("🔧 TROUBLESHOOTING:")
            logger.error("   This looks like an authentication issue.")
            logger.error("   Solution:")
            logger.error("   1. Verify TWILIO_ACCOUNT_SID in .env")
            logger.error("   2. Verify TWILIO_AUTH_TOKEN in .env")
            logger.error("   3. Check credentials at: https://console.twilio.com")
        elif "from" in error_str or "number" in error_str:
            logger.error("")
            logger.error("🔧 TROUBLESHOOTING:")
            logger.error("   This looks like an issue with the FROM number.")
            logger.error("   Solution:")
            logger.error("   1. Verify TWILIO_PHONE_NUMBER in .env")
            logger.error("   2. Make sure it's your verified Twilio number")
            logger.error("   3. Check at: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming")
        
        logger.error("")
        import traceback
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        return False


if __name__ == "__main__":
    logger.info("")
    logger.info("🧪 Sally Love Voice Agent - SMS Test")
    logger.info("="*60)
    logger.info("")
    logger.info("Usage:")
    logger.info("  python scripts/test_sms.py                    # Uses TEST_AGENT_PHONE from .env")
    logger.info("  python scripts/test_sms.py +1234567890        # Send to specific number")
    logger.info("")
    
    success = asyncio.run(test_sms())
    
    logger.info("")
    logger.info("="*60)
    if success:
        logger.info("✅ SMS Test PASSED")
    else:
        logger.info("❌ SMS Test FAILED")
    logger.info("="*60)
    
    sys.exit(0 if success else 1)

