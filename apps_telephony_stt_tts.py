class SpeechService:
    """
    Stub for TTS/STT. In production, integrate Azure Cognitive Services Speech SDK.
    For demo, we rely on Twilio's <Say> for TTS and <Gather input="speech"> for STT.
    """
    def synthesize(self, text: str) -> bytes:
        # Not used directly in this minimal TwiML approach.
        return b""

    def transcribe(self, audio_bytes: bytes) -> str:
        # Not used directly; Twilio returns SpeechResult via webhook form payload.
        return ""
