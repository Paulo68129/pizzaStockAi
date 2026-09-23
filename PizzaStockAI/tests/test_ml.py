from ml.forecast import forecast_demand
from ml.recommendation import purchase_recommendations


def test_forecast_demand_returns_horizon():
    history = [100, 120, 110, 130, 140, 150]
    result = forecast_demand(history, days=7)
    assert len(result) == 7
    assert all(value >= 0 for value in result)


def test_purchase_recommendations():
    result = purchase_recommendations(
        {"Mussarela": 20, "Calabresa": 5},
        {"Mussarela": 10, "Calabresa": 8},
        safety_stock={"Mussarela": 5, "Calabresa": 2},
    )
    assert result[0]["ingrediente"] == "Mussarela"
    assert result[0]["quantidade"] == 15
