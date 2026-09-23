from fastapi.testclient import TestClient

from backend.app import app
from seed import seed

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_and_analytics():
    seed(include_history=True)
    login = client.post("/login", json={"email": "admin@pizzastock.local", "senha": "123456"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    assert login.json()["perfil"] == "administrador"

    analytics = client.get("/analytics")
    assert analytics.status_code == 200
    body = analytics.json()
    assert "faturamento_hoje" in body
    assert "cmv_percentual" in body

    alertas = client.get("/alertas")
    assert alertas.status_code == 200
    assert isinstance(alertas.json(), list)

    headers = {"Authorization": f"Bearer {token}"}
    ingredientes = client.get("/ingredientes")
    assert ingredientes.status_code == 200
    assert len(ingredientes.json()) >= 1

    pizzas = client.get("/pizzas")
    assert pizzas.status_code == 200
    assert len(pizzas.json()) >= 1

    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "admin@pizzastock.local"
