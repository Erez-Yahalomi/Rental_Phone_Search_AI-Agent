
from fastapi import FastAPI
from apps.api.routes_listings import router as listings_router
from apps.api.routes_calls import router as calls_router
from apps.api.routes_dashboard import router as dashboard_router
from apps.telephony.webhooks import router as twilio_router
from apps.storage.repositories import ListingRepository

# Logging configuration import
from apps.logging_config import configure_logging

# Choose development flags here (set True while developing; False in production)
DEBUG_LOGGING = False
ENABLE_FILE_LOG = False

# Configure logging early, before importing modules that emit logs
configure_logging(debug=DEBUG_LOGGING, enable_file=ENABLE_FILE_LOG)

app = FastAPI(title="Rental Outreach API")

# Ensure tables exist at startup (for demo; use Alembic in production)
@app.on_event("startup")
def startup():
    ListingRepository().create_tables()

app.include_router(listings_router, prefix="/listings", tags=["listings"])
app.include_router(calls_router, prefix="/calls", tags=["calls"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
app.include_router(twilio_router, tags=["telephony"])
