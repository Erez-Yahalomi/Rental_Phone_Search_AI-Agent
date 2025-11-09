#  
 

IMPORTANT:
- Zillow does not provide an unrestricted public scraping API. Use a licensed
  partner API or a legally authorized scraping service (Apify, ZenRows, ScraperAPI, etc.).
- Update ZILLOW_* and ZILLOW_SCRAPER_* settings in config/settings.py and .env.
"""

from typing import List, Dict, Optional
import logging
import requests
from config.settings import settings

logger = logging.getLogger(__name__)


class RentPathProvider:
    """
    Adapter class preserved under the RentPathProvider name for compatibility.

    It delegates to Zillow-style fetch logic and returns canonical listings.
    If you prefer to rename callers, replace imports to use apps.ingestion.zillow_provider.ZillowProvider
    and remove this compatibility shim.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, session: Optional[requests.Session] = None):
        # Use Zillow-configured settings by default
        self.api_key = api_key or getattr(settings, "ZILLOW_API_KEY", "")
        self.base_url = base_url or getattr(settings, "ZILLOW_BASE_URL", "https://api.zillow.com")
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": "rental-outreach/1.0 (+https://your-org.example.com)",
            "Accept": "application/json"
        })

    def search_listings(self, city: str = "", state: str = "", min_price: int = 0, max_price: int = 0,
                        beds: int = 0, baths: int = 0, limit: int = 50) -> List[Dict]:
        """
        Search listings using the configured Zillow integration path.

        Strategy:
        - If ZILLOW_SCRAPER_SERVICE is configured, route to the chosen scraper integration.
        - Otherwise attempt a hypothetical Zillow partner API under ZILLOW_BASE_URL.

        Returns a list of canonical listing dicts.
        """
        service = (getattr(settings, "ZILLOW_SCRAPER_SERVICE", "") or "").lower()
        if service == "apify":
            return self._search_via_apify(city, state, min_price, max_price, beds, baths, limit)
        if service == "zenrows":
            return self._search_via_zenrows(city, state, min_price, max_price, beds, baths, limit)
        if service == "scraperapi":
            return self._search_via_scraperapi(city, state, min_price, max_price, beds, baths, limit)

        # Fallback to partner API style call
        return self._search_via_partner_api(city, state, min_price, max_price, beds, baths, limit)

    def _search_via_partner_api(self, city, state, min_price, max_price, beds, baths, limit):
        """
        Example partner API call (adapt to your partner API spec).
        """
        endpoint = f"{self.base_url.rstrip('/')}/v1/listings/search"
        params = {
            "city": city,
            "state": state,
            "min_price": min_price or None,
            "max_price": max_price or None,
            "beds": beds or None,
            "baths": baths or None,
            "limit": limit
        }
        params = {k: v for k, v in params.items() if v is not None}
        headers = self.session.headers.copy()
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            resp = self.session.get(endpoint, params=params, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.exception("Zillow partner API search failed: %s", e)
            return []

        results = data.get("listings") or data.get("results") or []
        items = []
        for p in results:
            mapped = self._map_provider_to_internal(p)
            if mapped:
                items.append(mapped)
        return items

    def _search_via_apify(self, city, state, min_price, max_price, beds, baths, limit):
        """
        Example integration with Apify actor that scrapes Zillow.
        Requires ZILLOW_SCRAPER_API_KEY (Apify token) and an actor configured.
        """
        apify_key = getattr(settings, "ZILLOW_SCRAPER_API_KEY", "") or ""
        if not apify_key:
            logger.warning("Apify API key not configured (ZILLOW_SCRAPER_API_KEY).")
            return []

        # Replace actor_id with your authorized actor
        actor_id = "eunit/zillow-rent-data-scraper"
        apify_run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={apify_key}"
        input_payload = {
            "city": city,
            "state": state,
            "min_price": min_price or None,
            "max_price": max_price or None,
            "beds": beds or None,
            "limit": limit
        }
        try:
            resp = self.session.post(apify_run_url, json={"body": input_payload}, timeout=10)
            resp.raise_for_status()
            run_info = resp.json()
            # Actor-specific: robust integration should poll run status then fetch dataset
            items = run_info.get("defaultDataset", {}).get("items") or run_info.get("items") or []
        except Exception as e:
            logger.exception("Apify run failed: %s", e)
            items = []

        results = []
        for p in items:
            mapped = self._map_provider_to_internal(p)
            if mapped:
                results.append(mapped)
        return results

    def _search_via_zenrows(self, city, state, min_price, max_price, beds, baths, limit):
        """
        Example proxy fetch using ZenRows. Replace parsing logic with a real parser for the HTML returned.
        """
        zen_key = getattr(settings, "ZILLOW_SCRAPER_API_KEY", "") or ""
        if not zen_key:
            logger.warning("ZenRows API key not configured (ZILLOW_SCRAPER_API_KEY).")
            return []

        query = f"https://www.zillow.com/homes/for_rent/{city}-{state}/"
        proxy_url = f"https://api.zenrows.com/v1/?apikey={zen_key}&url={requests.utils.quote(query)}"
        try:
            resp = self.session.get(proxy_url, timeout=15)
            resp.raise_for_status()
            html = resp.text
            # TODO: parse HTML and extract listing items into structured dicts
            parsed_items = []
        except Exception as e:
            logger.exception("ZenRows proxy fetch failed: %s", e)
            parsed_items = []

        results = []
        for p in parsed_items:
            mapped = self._map_provider_to_internal(p)
            if mapped:
                results.append(mapped)
        return results

    def _search_via_scraperapi(self, city, state, min_price, max_price, beds, baths, limit):
        """
        Example integration for ScraperAPI or similar proxy service.
        """
        scraper_key = getattr(settings, "ZILLOW_SCRAPER_API_KEY", "") or ""
        if not scraper_key:
            logger.warning("ScraperAPI key not configured (ZILLOW_SCRAPER_API_KEY).")
            return []

        query = f"https://www.zillow.com/homes/for_rent/{city}-{state}/"
        proxy_url = f"http://api.scraperapi.com?api_key={scraper_key}&url={requests.utils.quote(query)}"
        try:
            resp = self.session.get(proxy_url, timeout=15)
            resp.raise_for_status()
            html = resp.text
            # TODO: parse HTML into structured listing dicts
            parsed_items = []
        except Exception as e:
            logger.exception("ScraperAPI fetch failed: %s", e)
            parsed_items = []

        results = []
        for p in parsed_items:
            mapped = self._map_provider_to_internal(p)
            if mapped:
                results.append(mapped)
        return results

    def _map_provider_to_internal(self, p: Dict) -> Optional[Dict]:
        """
        Map various Zillow/scraper fields into the canonical internal schema.
        Update after inspecting the actual response format of your chosen integration.
        """
        try:
            listing_id = str(p.get("id") or p.get("listing_id") or p.get("zpid") or p.get("uid") or "")
            title = p.get("title") or p.get("headline") or p.get("description") or ""
            address = ""
            addr_obj = p.get("address") or {}
            if isinstance(addr_obj, dict):
                address = addr_obj.get("street") or addr_obj.get("line1") or ""
            else:
                address = p.get("address") or ""
            city = (addr_obj.get("city") if isinstance(addr_obj, dict) else p.get("city")) or ""
            state = (addr_obj.get("state") if isinstance(addr_obj, dict) else p.get("state")) or ""
            zipcode = (addr_obj.get("zip") if isinstance(addr_obj, dict) else p.get("zipcode")) or ""
            price = p.get("price") or p.get("rent") or None
            beds = p.get("beds") or p.get("bedrooms") or None
            baths = p.get("baths") or p.get("bathrooms") or None
            sqft = p.get("sqft") or p.get("area") or None
            url = p.get("url") or p.get("listing_url") or p.get("detail_url") or ""
            contact_phone = p.get("contact", {}).get("phone") or p.get("phone") or p.get("contact_phone") or ""

            return {
                "listing_id": listing_id,
                "provider": "zillow",
                "search_id": "",  # set by caller when ingesting into a search context
                "title": title,
                "address": address,
                "city": city,
                "state": state,
                "zipcode": zipcode,
                "price": price,
                "beds": beds,
                "baths": baths,
                "sqft": sqft,
                "url": url,
                "contact_phone": contact_phone
            }
        except Exception as e:
            logger.exception("Failed to map Zillow provider listing: %s", e)
            return None
