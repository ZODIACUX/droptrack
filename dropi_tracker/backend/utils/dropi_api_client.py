import requests
import os

API_BASE_URL = 'https://api.dropi.co/api'

class DropiAPIClient:
    def __init__(self):
        self.email = os.environ.get('DROPI_EMAIL')
        self.password = os.environ.get('DROPI_PASSWORD')
        self.white_brand_id = 'df3e6b0bb66ceaadca4f84cbc371fd66e04d20fe51fc414da8d1b84d31d178de'

        if not self.email or not self.password:
            raise Exception("DROPI_EMAIL and DROPI_PASSWORD environment variables must be set.")

        self.token = self._get_auth_token()

    def _get_auth_token(self):
        """Logs into Dropi and returns an auth token."""
        login_url = f"{API_BASE_URL}/login"
        credentials = {
            "email": self.email,
            "password": self.password,
            "white_brand_id": self.white_brand_id
        }

        response = requests.post(login_url, json=credentials)
        response.raise_for_status()

        token = response.json().get('token')
        if not token:
            raise Exception("Failed to get auth token from Dropi API. Check your credentials.")

        return token

    def get_shipments(self):
        """Fetches orders from Dropi and extracts shipment information (tracking number and carrier)."""
        orders_url = f"{API_BASE_URL}/orders/myorders"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        response = requests.get(orders_url, headers=headers)
        response.raise_for_status()

        orders = response.json()
        if not isinstance(orders, list):
            orders = orders.get('data', [])

        shipments = []
        for order in orders:
            guide = order.get('shipping_guide')
            carrier = order.get('shipping_company')
            if guide and carrier:
                shipments.append({
                    "number": guide,
                    "carrier": carrier
                })

        return shipments
