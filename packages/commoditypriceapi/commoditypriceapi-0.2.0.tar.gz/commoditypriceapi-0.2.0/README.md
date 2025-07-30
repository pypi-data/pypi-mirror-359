# 📦 Example Usage

```python
from commoditypriceapi.client import CommodityPriceClient

# Initialize the API client with your API key
client = CommodityPriceClient(api_key="YOUR_API_KEY_HERE")

# 🔹 Get the latest price for gold
latest_price = client.get_latest_price("gold")
print("Latest Gold Price:", latest_price)

# 🔹 Get historical price data for oil
historical_prices = client.get_historical_prices("oil", "2024-01-01", "2024-12-31")
print("Historical Oil Prices:", historical_prices)

# 🔹 Get market insights for silver
market_insights = client.get_market_insights("silver")
print("Market Insights for Silver:", market_insights)
