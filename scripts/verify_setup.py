"""
Script to verify complete system setup
Checks all configurations, files, and dependencies
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.utils.logger import setup_logger, get_logger

setup_logger()
logger = get_logger(__name__)


def check_env_variables():
    """Check if all required environment variables are set"""
    logger.info("\n" + "="*60)
    logger.info("Checking Environment Variables")
    logger.info("="*60)
    
    required_vars = {
        "VAPI_API_KEY": settings.VAPI_API_KEY,
        "BOLDTRAIL_API_KEY": settings.BOLDTRAIL_API_KEY,
        "STELLAR_MLS_USERNAME": settings.STELLAR_MLS_USERNAME,
        "STELLAR_MLS_PASSWORD": settings.STELLAR_MLS_PASSWORD,
        "TWILIO_ACCOUNT_SID": settings.TWILIO_ACCOUNT_SID,
        "TWILIO_AUTH_TOKEN": settings.TWILIO_AUTH_TOKEN,
    }
    
    all_set = True
    for var_name, var_value in required_vars.items():
        if var_value:
            logger.info(f"✅ {var_name:25} SET")
        else:
            logger.warning(f"❌ {var_name:25} NOT SET")
            all_set = False
    
    return all_set


def check_file_structure():
    """Check if all required files and directories exist"""
    logger.info("\n" + "="*60)
    logger.info("Checking File Structure")
    logger.info("="*60)
    
    project_root = Path(__file__).parent.parent
    
    required_paths = [
        "main.py",
        "src/__init__.py",
        "src/config/settings.py",
        "src/integrations/vapi_client.py",
        "src/integrations/boldtrail.py",
        "src/integrations/stellar_mls.py",
        "src/integrations/twilio_client.py",
        "src/functions/check_property.py",
        "src/functions/get_agent_info.py",
        "src/functions/route_to_agent.py",
        "src/functions/create_buyer_lead.py",
        "src/functions/create_seller_lead.py",
        "src/functions/send_notification.py",
        "src/models/vapi_models.py",
        "src/models/crm_models.py",
        "src/models/mls_models.py",
        "src/webhooks/vapi_webhooks.py",
        "src/webhooks/crm_webhooks.py",
        "src/utils/logger.py",
        "src/utils/errors.py",
        "src/utils/validators.py",
    ]
    
    all_exist = True
    for path in required_paths:
        full_path = project_root / path
        if full_path.exists():
            logger.info(f"✅ {path}")
        else:
            logger.error(f"❌ {path} - NOT FOUND")
            all_exist = False
    
    return all_exist


def check_configuration():
    """Check configuration settings"""
    logger.info("\n" + "="*60)
    logger.info("Checking Configuration")
    logger.info("="*60)
    
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Server: {settings.HOST}:{settings.PORT}")
    logger.info(f"Webhook URL: {settings.WEBHOOK_BASE_URL}")
    logger.info(f"Business: {settings.BUSINESS_NAME}")
    logger.info(f"Phone: {settings.BUSINESS_PHONE}")
    
    issues = []
    
    if settings.WEBHOOK_BASE_URL == "http://localhost:8000" and settings.is_production:
        issues.append("Webhook URL is localhost in production environment")
    
    if not settings.BUSINESS_PHONE.startswith("+"):
        issues.append("Business phone should be in E.164 format (+1...)")
    
    if issues:
        logger.warning("\nConfiguration Issues:")
        for issue in issues:
            logger.warning(f"⚠️  {issue}")
        return False
    
    logger.info("\n✅ Configuration looks good!")
    return True


def main():
    """Run all verification checks"""
    logger.info("\n" + "="*80)
    logger.info("SALLY LOVE REAL ESTATE - System Verification")
    logger.info("="*80)
    
    env_ok = check_env_variables()
    files_ok = check_file_structure()
    config_ok = check_configuration()
    
    logger.info("\n" + "="*80)
    logger.info("VERIFICATION SUMMARY")
    logger.info("="*80)
    
    logger.info(f"Environment Variables: {'✅ PASS' if env_ok else '❌ FAIL'}")
    logger.info(f"File Structure:        {'✅ PASS' if files_ok else '❌ FAIL'}")
    logger.info(f"Configuration:         {'✅ PASS' if config_ok else '⚠️  WARNINGS'}")
    
    logger.info("="*80)
    
    if env_ok and files_ok:
        logger.info("\n✅ System is ready to run!")
        logger.info("\nNext steps:")
        logger.info("1. Run: python main.py")
        logger.info("2. Test integrations: python scripts/test_integrations.py")
        logger.info("3. Set up Vapi: python scripts/setup_vapi.py")
    else:
        logger.error("\n❌ System verification failed. Please fix the issues above.")
        logger.info("\nCommon fixes:")
        logger.info("1. Copy .env.example to .env")
        logger.info("2. Fill in all required API keys and credentials")
        logger.info("3. Ensure all source files are present")


if __name__ == "__main__":
    main()

