import requests
import logging
from config import IG_API_KEY, IG_USERNAME, IG_PASSWORD, IG_BASE_URL

logger = logging.getLogger(__name__)


class IGClient:
    """Thin wrapper around the IG REST API for the demo account."""

    def __init__(self):
        self.session = requests.Session()
        self.cst = None
        self.security_token = None
        self._login()

    def _login(self):
        url = f"{IG_BASE_URL}/session"
        headers = {
            "X-IG-API-KEY": IG_API_KEY,
            "Content-Type": "application/json",
            "Version": "2",
        }
        payload = {"identifier": IG_USERNAME, "password": IG_PASSWORD}
        resp = self.session.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        self.cst = resp.headers["CST"]
        self.security_token = resp.headers["X-SECURITY-TOKEN"]
        logger.info("IG login successful.")

    def _headers(self, version="1"):
        return {
            "X-IG-API-KEY": IG_API_KEY,
            "CST": self.cst,
            "X-SECURITY-TOKEN": self.security_token,
            "Content-Type": "application/json",
            "Version": version,
        }

    def get_account_info(self):
        url = f"{IG_BASE_URL}/accounts"
        resp = self.session.get(url, headers=self._headers(), timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_prices(self, epic: str, resolution: str = "DAY", num_points: int = 260):
        """Fetch historical prices. resolution: MINUTE|HOUR|DAY|WEEK."""
        url = f"{IG_BASE_URL}/prices/{epic}/{resolution}/{num_points}"
        resp = self.session.get(url, headers=self._headers(version="3"), timeout=30)
        if resp.status_code == 200:
            return resp.json().get("prices", [])
        logger.warning(f"Could not fetch prices for {epic}: {resp.status_code}")
        return []

    def search_market(self, search_term: str):
        """Search for an instrument EPIC by name/ticker."""
        url = f"{IG_BASE_URL}/markets?searchTerm={search_term}"
        resp = self.session.get(url, headers=self._headers(), timeout=15)
        resp.raise_for_status()
        return resp.json().get("markets", [])

    def get_positions(self):
        url = f"{IG_BASE_URL}/positions/otc"
        resp = self.session.get(url, headers=self._headers(), timeout=15)
        resp.raise_for_status()
        return resp.json().get("positions", [])

    def place_order(self, epic: str, direction: str, size: float, stop_distance: int):
        """Place a market order. direction: BUY|SELL."""
        url = f"{IG_BASE_URL}/positions/otc"
        payload = {
            "epic": epic,
            "expiry": "-",
            "direction": direction,
            "size": size,
            "orderType": "MARKET",
            "timeInForce": "EXECUTE_AND_ELIMINATE",
            "stopDistance": stop_distance,
            "guaranteedStop": False,
            "forceOpen": True,
        }
        resp = self.session.post(url, headers=self._headers(version="2"), json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def close_position(self, deal_id: str, direction: str, size: float):
        url = f"{IG_BASE_URL}/positions/otc"
        payload = {
            "dealId": deal_id,
            "direction": direction,
            "size": size,
            "orderType": "MARKET",
            "timeInForce": "EXECUTE_AND_ELIMINATE",
        }
        headers = self._headers(version="1")
        headers["_method"] = "DELETE"
        resp = self.session.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()
