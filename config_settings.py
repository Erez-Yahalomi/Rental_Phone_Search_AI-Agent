
from pydantic import BaseSettings, AnyUrl

class Settings(BaseSettings):
    DATABASE_URL: AnyUrl
    REDIS_URL: AnyUrl = "redis://localhost:6379/0"

    # Telephony
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_CALLER_ID: str
    PUBLIC_BASE_URL: str

    # Speech
    AZURE_SPEECH_KEY: str = ""
    AZURE_SPEECH_REGION: str = ""
    TTS_VOICE: str = "en-US-JennyNeural"

    # Storage
    S3_ENDPOINT_URL: str = ""
    S3_BUCKET_RECORDINGS: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""

    # RentPath
    RENTPATH_API_KEY: str
    RENTPATH_BASE_URL: str = "https://api.rentpath.com/v1"

    # GPT integration (NEW)
    OPENAI_API_KEY: str   # ← REQUIRED for GPT-powered modules

    # Operational
    MAX_LISTINGS_PER_SEARCH: int = 300
    CALL_CONCURRENCY: int = 10
    CALL_TIMEOUT_SECONDS: int = 600
    JOB_RETRY_LIMIT: int = 3

    class Config:
        env_file = ".env"

settings = Settings()
