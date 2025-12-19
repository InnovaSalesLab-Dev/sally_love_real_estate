"""
Twilio API client for SMS and call routing
"""

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from typing import Dict, Any, Optional
from src.config.settings import settings
from src.utils.logger import get_logger
from src.utils.errors import TwilioError

logger = get_logger(__name__)


class TwilioClient:
    """Client for Twilio API"""
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        
        try:
            self.client = Client(self.account_sid, self.auth_token)
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {str(e)}")
            raise TwilioError(
                message=f"Failed to initialize Twilio: {str(e)}",
                details={"error": str(e)}
            )
    
    async def send_sms(
        self,
        to_number: str,
        message: str,
        from_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send an SMS message
        
        Args:
            to_number: Recipient phone number
            message: Message content
            from_number: Sender phone number (defaults to configured number)
            
        Returns:
            Message data
            
        Raises:
            TwilioError: If SMS fails to send
        """
        from_number = from_number or self.phone_number
        
        # Validate configuration
        if not self.account_sid or not self.auth_token:
            raise TwilioError(
                message="Twilio credentials not configured (TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN missing)",
                status_code=500,
                details={"account_sid_set": bool(self.account_sid), "auth_token_set": bool(self.auth_token)}
            )
        
        if not from_number:
            raise TwilioError(
                message="Twilio phone number not configured (TWILIO_PHONE_NUMBER missing)",
                status_code=500,
                details={"from_number": from_number}
            )
        
        if not self.client:
            raise TwilioError(
                message="Twilio client not initialized",
                status_code=500,
                details={}
            )
        
        try:
            logger.info(f"Sending SMS to {to_number} from {from_number}")
            
            message_obj = self.client.messages.create(
                to=to_number,
                from_=from_number,
                body=message,
            )
            
            return {
                "sid": message_obj.sid,
                "status": message_obj.status,
                "to": to_number,
                "from": from_number,
                "message": message,
            }
            
        except TwilioRestException as e:
            error_msg = getattr(e, 'msg', str(e))
            logger.exception(f"Twilio SMS error: {error_msg}")
            raise TwilioError(
                message=f"Failed to send SMS: {error_msg}",
                status_code=getattr(e, 'status', 500),
                details={"code": getattr(e, 'code', None), "error": error_msg}
            )
        except Exception as e:
            error_msg = str(e)
            logger.exception(f"Unexpected error in send_sms: {error_msg}")
            raise TwilioError(
                message=f"Failed to send SMS: {error_msg}",
                status_code=500,
                details={"error": error_msg}
            )
    
    async def make_call(
        self,
        to_number: str,
        from_number: Optional[str] = None,
        twiml_url: Optional[str] = None,
        twiml: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Initiate a phone call
        
        Args:
            to_number: Recipient phone number
            from_number: Caller phone number (defaults to configured number)
            twiml_url: URL to TwiML instructions
            twiml: TwiML instructions as string
            
        Returns:
            Call data
            
        Raises:
            TwilioError: If call fails
        """
        from_number = from_number or self.phone_number
        
        if not twiml_url and not twiml:
            raise TwilioError(
                message="Either twiml_url or twiml must be provided",
                details={"to_number": to_number}
            )
        
        try:
            logger.info(f"Making call to {to_number}")
            
            call_params = {
                "to": to_number,
                "from_": from_number,
            }
            
            if twiml_url:
                call_params["url"] = twiml_url
            elif twiml:
                call_params["twiml"] = twiml
            
            call = self.client.calls.create(**call_params)
            
            return {
                "sid": call.sid,
                "status": call.status,
                "to": to_number,
                "from": from_number,
            }
            
        except TwilioRestException as e:
            logger.exception(f"Twilio call error: {str(e)}")
            raise TwilioError(
                message=f"Failed to make call: {e.msg}",
                status_code=e.status,
                details={"code": e.code, "error": e.msg}
            )
    
    async def transfer_call(
        self,
        call_sid: str,
        to_number: str,
    ) -> Dict[str, Any]:
        """
        Transfer an active call to another number
        
        Args:
            call_sid: Active call SID
            to_number: Number to transfer to
            
        Returns:
            Transfer confirmation
            
        Raises:
            TwilioError: If transfer fails
        """
        try:
            logger.info(f"Transferring call {call_sid} to {to_number}")
            
            # Create TwiML for transfer
            twiml = f'<Response><Dial>{to_number}</Dial></Response>'
            
            call = self.client.calls(call_sid).update(twiml=twiml)
            
            return {
                "sid": call.sid,
                "status": call.status,
                "transferred_to": to_number,
            }
            
        except TwilioRestException as e:
            logger.exception(f"Twilio transfer error: {str(e)}")
            raise TwilioError(
                message=f"Failed to transfer call: {e.msg}",
                status_code=e.status,
                details={"code": e.code, "error": e.msg, "call_sid": call_sid}
            )
    
    async def get_call_status(self, call_sid: str) -> Dict[str, Any]:
        """
        Get status of a call
        
        Args:
            call_sid: Call SID
            
        Returns:
            Call status information
        """
        try:
            call = self.client.calls(call_sid).fetch()
            
            return {
                "sid": call.sid,
                "status": call.status,
                "duration": call.duration,
                "from": call.from_,
                "to": call.to,
                "start_time": call.start_time,
                "end_time": call.end_time,
            }
            
        except TwilioRestException as e:
            logger.exception(f"Failed to get call status: {str(e)}")
            raise TwilioError(
                message=f"Failed to get call status: {e.msg}",
                status_code=e.status,
                details={"code": e.code, "error": e.msg}
            )

