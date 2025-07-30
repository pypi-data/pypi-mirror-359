import requests

class CommodityPriceAPIError(Exception):
    pass

class CommodityPriceClient:
    """
    Client for CommodityPriceAPI
    """
    def __init__(self, api_key: str, base_url: str = "https://api.commoditypriceapi.com/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self._session = requests.Session()
        self._session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        })

    def _get(self, path: str, params: dict = None) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self._session.get(url, params=params)
        if not resp.ok:
            raise CommodityPriceAPIError(f"Error {resp.status_code}: {resp.text}")
        return resp.json()

    def get_latest_price(self, commodity: str, currency: str = 'USD') -> dict:
        """
        Fetch the latest price for a given commodity.
        :param commodity: Commodity symbol (e.g. 'gold', 'oil')
        :param currency: ISO currency code (default 'USD')
        :returns: JSON response with price data
        """
        return self._get('prices/latest', params={'commodity': commodity, 'currency': currency})

    def get_historical_prices(self, commodity: str, start_date: str, end_date: str,
                              currency: str = 'USD') -> dict:
        """
        Fetch historical price data over a date range.
        :param start_date: 'YYYY-MM-DD'
        :param end_date: 'YYYY-MM-DD'
        """
        params = {
            'commodity': commodity,
            'currency': currency,
            'start_date': start_date,
            'end_date': end_date,
        }
        return self._get('prices/historical', params=params)

    def get_market_insights(self, commodity: str) -> dict:
        """
        Fetch market insights or news summary for a commodity.
        """
        return self._get(f'insights/{commodity}')