from twilio.rest import Client
from config.settings import settings

class VoiceGateway:
    """
    Minimal Twilio wrapper for outbound calls. TwiML served by our webhook.
    """
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.caller_id = settings.TWILIO_CALLER_ID

    def place_call(self, to_number: str, webhook_path: str) -> str:
        """
        Place an outbound call to `to_number`. `webhook_path` is the API route path (e.g., "/twilio/voice").
        """
        url = settings.PUBLIC_BASE_URL.rstrip("/") + webhook_path
        call = self.client.calls.create(
            to=to_number,
            from_=self.caller_id,
            url=url,
            record=True,
        )
        return call.sid

    def hangup(self, call_sid: str):
        self.client.calls(call_sid).update(status="completed")
