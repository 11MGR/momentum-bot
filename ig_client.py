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
        payload = {
            "identifier": IG_USERNAME,
            "password": IG_PASSWORD,
            "encryptedPassword": False,
        }
        try:
            resp = self.session.post(url, headers=headers, json=payload, timeout=15)
            if not resp.ok:
                logger.error(
                    "IG login failed: HTTP %s | body: %s",
                    resp.status_code,
                    resp.text[:500],
                )
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(
                f"IG API login error ({e.response.status_code}): {e.response.text[:300]}"
            ) from e
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
        """Return account details."""
        url = f"{IG_BASE_URL}/accounts"
        resp = self.session.get(url, headers=self._headers("1"), timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_prices(self, epic: str, resolution: str = "DAY", num_points: int = 260):
        """Fetch historical prices for an epic."""
        url = f"{IG_BASE_URL}/prices/{epic}/{resolution}/{num_points}"
        resp = self.session.get(url, headers=self._headers("3"), timeout=30)
        if not resp.ok:
            logger.warning(
                "get_prices failed for %s: HTTP %s | %s",
                epic,
                resp.status_code,
                resp.text[:200],
            )
            return None
        return resp.json().get("prices", [])

    def get_positions(self):
        """Return current open positions."""
        url = f"{IG_BASE_URL}/positions/otc"
        resp = self.session.get(url, headers=self._headers("2"), timeout=15)
        resp.raise_for_status()
        return resp.json().get("positions", [])

    def search_market(self, search_term: str):
        """Search for an instrument by keyword."""
        url = f"{IG_BASE_URL}/markets?searchTerm={search_term}"
        resp = self.session.get(url, headers=self._headers("1"), timeout=15)
        resp.raise_for_status()
        return resp.json().get("markets", [])

    def place_order(
        self,
        epic: str,
        direction: str,
        size: float,
        stop_distance: float = None,
    ):
        """Place a market order on the demo account."""
        url = f"{IG_BASE_URL}/positions/otc"
        payload = {
            "epic": epic,
            "expiry": "-",
            "direction": direction.upper(),
            "size": size,
            "orderType": "MARKET",
            "timeInForce": "FILL_OR_KILL",
            "guaranteedStop": False,
            "forceOpen": True,
        }
        if stop_distance:
            payload["stopDistance"] = stop_distance
        resp = self.session.post(
            url, headers=self._headers("2"), json=payload, timeout=15
        )
        if not resp.ok:
            logger.error(
                "place_order failed: HTTP %s | %s", resp.status_code, resp.text[:300]
            )
        resp.raise_for_status()
        return resp.json()

    def close_position(self, deal_id: str, direction: str, size: float):
        """Close an open position."""
        url = f"{IG_BASE_URL}/positions/otc"
        headers = self._headers("1")
        headers["_method"] = "DELETE"
        payload = {
            "dealId": deal_id,
            "direction": direction.upper(),
            "size": size,
            "orderType": "MARKET",
            "timeInForce": "FILL_OR_KILL",
        }
        resp = self.session.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()
