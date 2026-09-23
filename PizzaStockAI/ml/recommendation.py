from __future__ import annotations


def purchase_recommendations(
    forecast: dict[str, float],
    stock: dict[str, float],
    safety_stock: float | dict[str, float] = 0.0,
) -> list[dict]:
    """Recomenda compras: necessidade = consumo_previsto + segurança - estoque_atual."""
    recommendations = []
    for name, predicted in forecast.items():
        safety = safety_stock.get(name, 0.0) if isinstance(safety_stock, dict) else float(safety_stock)
        needed = max(0.0, predicted + safety - stock.get(name, 0.0))
        if needed > 0:
            recommendations.append({"ingrediente": name, "quantidade": round(needed, 2)})
    return sorted(recommendations, key=lambda item: item["quantidade"], reverse=True)
