from config.settings import settings

def create_provider():
    """
    Factory to produce a listings provider adapter based on LISTING_PROVIDER.
    Supported: zillow, zumper, rentcom, rentpath (legacy).
    Use this function across the codebase instead of importing provider modules directly.
    """
    provider = (settings.LISTING_PROVIDER or "zillow").strip().lower()

    if provider == "zillow":
        from .zillow_provider import ZillowProvider
        return ZillowProvider()
    if provider == "zumper":
        from .zumper_provider import ZumperProvider
        return ZumperProvider()
    if provider == "rentcom":
        from .rentcom_provider import RentComProvider
        return RentComProvider()
    if provider == "rentpath":
        # keep legacy provider available but prefer centralized config
        from .rentpath_provider import RentPathProvider
        return RentPathProvider()

    raise ValueError(f"Unknown listing provider configured: {settings.LISTING_PROVIDER}")
