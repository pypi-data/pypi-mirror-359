def test_methods_exist():
    from commoditpriceyapi.client import CommodityPriceClient
    client = CommodityPriceClient("dummy")
    assert hasattr(client, "get_latest_price")
